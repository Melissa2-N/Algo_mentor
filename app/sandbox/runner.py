"""Exécution isolée de code utilisateur : conteneur Docker éphémère.

Sécurité : --network none, mémoire limitée (128 Mo pour l'exécution),
1 CPU, dossier temporaire détruit après exécution, watchdog qui tue le
conteneur au bout du timeout (boucles infinies), utilisateur non-root.
Jamais d'exécution sur l'hôte.
"""
from __future__ import annotations

import shutil
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

import docker

from ..config import settings
from .images import get_spec


@dataclass
class RunResult:
    ok: bool
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool
    duration_ms: int


def _ensure_image(client: docker.DockerClient, image: str) -> None:
    try:
        client.images.get(image)
    except docker.errors.ImageNotFound:
        print(f"[sandbox] pulling {image} (premiere fois seulement)...")
        client.images.pull(image)


def _run_container(
    client: docker.DockerClient,
    *,
    image: str,
    command: str,
    workdir: Path,
    timeout_seconds: float,
    mem_limit: str,
) -> RunResult:
    """Lance un conteneur éphémère sh -c "command", avec watchdog."""
    container = client.containers.create(
        image=image,
        command=["sh", "-c", command],
        working_dir="/sandbox",
        volumes={str(workdir): {"bind": "/sandbox", "mode": "rw"}},
        network_disabled=True,               # pas de reseau
        mem_limit=mem_limit,
        nano_cpus=int(settings.sandbox_cpu_limit * 1e9),
        auto_remove=False,
        user="65534:65534",                  # nobody : pas de root
    )
    start = time.monotonic()
    container.start()

    deadline = start + timeout_seconds
    timed_out = False
    result: dict = {}
    while True:
        container.reload()
        if container.status in ("exited", "dead"):
            result = container.wait()
            break
        if time.monotonic() > deadline:
            timed_out = True
            try:
                container.kill()
                result = container.wait()
            except docker.errors.APIError:
                result = {"StatusCode": 137}
            break
        time.sleep(0.05)

    duration_ms = int((time.monotonic() - start) * 1000)
    stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
    stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")
    try:
        container.remove(force=True)
    except docker.errors.APIError:
        pass

    exit_code = result.get("StatusCode")
    if timed_out:
        stderr += f"\nTemps limite depasse ({timeout_seconds}s) : boucle infinie ?"
    ok = (not timed_out) and exit_code == 0
    return RunResult(ok, stdout, stderr, exit_code, timed_out, duration_ms)


def run_code(language: str, code: str, stdin_data: str = "") -> RunResult:
    spec = get_spec(language)
    if spec is None:
        return RunResult(False, "", f"langage inconnu : {language}", None, False, 0)

    client = docker.from_env()
    _ensure_image(client, spec.image)

    # Dossier temporaire detruit apres execution
    workdir = Path(tempfile.gettempdir()) / f"algo_tutor_{uuid.uuid4().hex}"
    workdir.mkdir(parents=True)
    try:
        (workdir / spec.file_name).write_text(code, encoding="utf-8")
        (workdir / "stdin.txt").write_text(stdin_data, encoding="utf-8")

        # Phase 1 : compilation (toolchain, pas de code utilisateur à exécuter)
        if spec.compile_command:
            compile_result = _run_container(
                client,
                image=spec.image,
                command=spec.compile_command,
                workdir=workdir,
                timeout_seconds=20.0,
                mem_limit=spec.compile_memory,
            )
            if not compile_result.ok:
                return RunResult(
                    False,
                    compile_result.stdout,
                    "Erreur de compilation :\n" + compile_result.stderr,
                    compile_result.exit_code,
                    compile_result.timed_out,
                    compile_result.duration_ms,
                )

        # Phase 2 : exécution du code utilisateur (timeout strict)
        return _run_container(
            client,
            image=spec.image,
            command=f"{spec.run_command} < stdin.txt",
            workdir=workdir,
            timeout_seconds=settings.sandbox_timeout_seconds,
            mem_limit=settings.sandbox_memory_limit,
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def run_tests(language: str, code: str, test_cases) -> list[dict]:
    """Exécute le code pour chaque cas de test et compare stdout."""
    results = []
    for i, case in enumerate(test_cases):
        run = run_code(language, code, stdin_data=case.stdin)
        actual = run.stdout.strip()
        expected = case.expected.strip()
        results.append({
            "label": case.label or f"test {i + 1}",
            "stdin": case.stdin,
            "expected": expected,
            "actual": actual,
            "passed": run.ok and actual == expected,
            "stdout": run.stdout,
            "stderr": run.stderr,
            "timed_out": run.timed_out,
        })
    return results
