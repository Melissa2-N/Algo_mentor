"""Images et commandes d'exécution par langage dans la sandbox Docker.

Deux phases : compilation éventuelle (timeout large, toolchain uniquement),
puis exécution du code utilisateur (timeout strict).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LanguageSpec:
    image: str
    file_name: str
    run_command: str            # exécution utilisateur, stdin via " < stdin.txt"
    compile_command: str | None = None
    compile_memory: str = "512m"  # javac a besoin de plus que les 128 Mo d'exécution


SPECS: dict[str, LanguageSpec] = {
    "python": LanguageSpec(
        image="python:3.12-slim",
        file_name="main.py",
        run_command="python3 main.py",
    ),
    "c": LanguageSpec(
        image="gcc:14",
        file_name="main.c",
        run_command="./prog",
        compile_command="gcc main.c -o prog",
    ),
    "javascript": LanguageSpec(
        image="node:20-alpine",
        file_name="main.js",
        run_command="node main.js",
    ),
    "java": LanguageSpec(
        image="eclipse-temurin:17-jdk-alpine",
        file_name="Main.java",
        run_command="java Main",
        compile_command="javac Main.java",
    ),
}


def get_spec(language: str) -> LanguageSpec | None:
    return SPECS.get(language)
