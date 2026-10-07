"""Smoke test rapide de la sandbox Docker (sans base de donnees)."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.sandbox.runner import run_code  # noqa: E402

cases = [
    ("python", 'n = int(input())\nprint(n * 2)\n', "21\n", "42\n"),
    ("javascript", 'const n = parseInt(require("fs").readFileSync(0, "utf8"));\nconsole.log(n * 2);\n', "21\n", "42\n"),
    ("c", '#include <stdio.h>\nint main(void){int n;scanf("%d",&n);printf("%d\\n",n*2);return 0;}\n', "21", "42\n"),
    ("java", 'import java.util.Scanner;\npublic class Main {public static void main(String[] a){Scanner s=new Scanner(System.in);System.out.println(s.nextInt()*2);}}\n', "21", "42\n"),
    ("python", 'i = 0\nwhile True:\n    i += 1\n', "", "TIMEOUT"),
]

ok = True
for lang, code, stdin_data, expected in cases:
    result = run_code(lang, code, stdin_data)
    if expected == "TIMEOUT":
        passed = result.timed_out
    else:
        passed = result.ok and result.stdout == expected
    print(f"[{'PASS' if passed else 'FAIL'}] {lang:10s} exit={result.exit_code} "
          f"out={result.stdout!r} err={result.stderr[:120]!r} {result.duration_ms}ms")
    ok = ok and passed

print("SANDBOX_ALL_OK" if ok else "SANDBOX_FAILURES")
sys.exit(0 if ok else 1)
