import json
import os
import urllib.request
from typing import Dict, List
from factory.generator import CodingTask
from factory.validator import static_ast_check, run_in_sandbox

FENCE = chr(96) * 3

def generate_candidate_code(task: CodingTask, model_name: str) -> str:
    """Uses live Anthropic API if ANTHROPIC_API_KEY is set, else deterministic profiles."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and model_name == "claude-sonnet-4-5":
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps({
                    "model": "claude-sonnet-4-5-20250929",
                    "max_tokens": 512,
                    "messages": [{"role": "user", "content": f"Return ONLY valid Python code:\n{task.prompt}"}],
                }).encode("utf-8"),
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["content"][0]["text"]
                return text.replace(FENCE + "python", "").replace(FENCE, "").strip()
        except Exception:
            pass

    if model_name == "frontier-model-alpha":
        return task.reference_solution
    if model_name == "frontier-model-beta":
        if task.difficulty == "hard":
            return f"def {task.function_name}(*args, **kwargs):\n    return -1\n"
        return task.reference_solution
    if task.difficulty in ("medium", "hard"):
        return f"def {task.function_name}(*args, **kwargs):\n    return None\n"
    return task.reference_solution

def evaluate_models(tasks: List[CodingTask], models: List[str]) -> Dict[str, dict]:
    report: Dict[str, dict] = {}
    for model in models:
        passed = 0
        failures = []
        for task in tasks:
            candidate = generate_candidate_code(task, model)
            ok_ast, msg_ast = static_ast_check(candidate, task.function_name)
            if not ok_ast:
                failures.append({"task_id": task.task_id, "reason": msg_ast})
                continue
            ok_run, msg_run = run_in_sandbox(candidate, task.test_code)
            if ok_run:
                passed += 1
            else:
                failures.append({"task_id": task.task_id, "reason": msg_run.splitlines()[-1]})
        total = len(tasks)
        report[model] = {
            "passed": passed,
            "total": total,
            "pass_at_1": round((passed / total) * 100, 2) if total else 0.0,
            "failures": failures,
        }
    return report
