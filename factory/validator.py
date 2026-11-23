import ast
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple
from factory.generator import CodingTask

BANNED_CALLS = {"eval", "exec", "compile", "__import__", "open", "system", "popen"}

def static_ast_check(code: str, expected_fn: str) -> Tuple[bool, str]:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, f"SyntaxError: {exc}"

    fn_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    if expected_fn not in fn_names:
        return False, f"Missing required function `{expected_fn}`"

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in BANNED_CALLS:
                return False, f"Banned call detected: {node.func.id}"
    return True, "AST check passed"

def run_in_sandbox(solution_code: str, test_code: str, timeout_sec: float = 2.0) -> Tuple[bool, str]:
    harness = f"{solution_code}\n\n{test_code}\nprint('ALL_TESTS_PASSED')\n"
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / "test_harness.py"
        script_path.write_text(harness, encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )
            if proc.returncode == 0 and "ALL_TESTS_PASSED" in proc.stdout:
                return True, "Passed"
            return False, (proc.stderr.strip() or proc.stdout.strip() or "AssertionError")
        except subprocess.TimeoutExpired:
            return False, "TimeoutError"

def validate_task(task: CodingTask) -> Tuple[bool, str]:
    ok_ast, msg_ast = static_ast_check(task.reference_solution, task.function_name)
    if not ok_ast:
        return False, msg_ast

    ok_ref, msg_ref = run_in_sandbox(task.reference_solution, task.test_code)
    if not ok_ref:
        return False, f"Reference failed: {msg_ref}"

    stub = f"def {task.function_name}(*args, **kwargs):\n    return None\n"
    ok_stub, _ = run_in_sandbox(stub, task.test_code)
    if ok_stub:
        return False, "Trivial stub passed tests; test suite is too weak"

    return True, "Verified"
