import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_URL = "https://github.com/itsmerbk/coding-task-factory"

def open_workspace() -> None:
    print("Opening VS Code workspace...")
    subprocess.run(
        [
            "open",
            "-a",
            "Visual Studio Code",
            ".",
            "README.md",
            "run_pipeline.py",
            "results/benchmark_summary.md",
        ],
        check=False,
    )
    time.sleep(1.5)

    print("Opening GitHub repository in browser...")
    subprocess.run(["open", REPO_URL], check=False)
    time.sleep(1.5)

    subprocess.run(
        ["osascript", "-e", 'tell application "Terminal" to activate'],
        check=False,
    )
    print("Launching macOS Screen Recorder toolbar...")
    subprocess.run(["open", "-a", "Screenshot"], check=False)

def run_automated_walkthrough() -> None:
    os.system("clear")
    print("=" * 68)
    print("  CODING TASK FACTORY | Innodata Frontier AI Hackathon 2026")
    print("  Author: Bharath Kumar R (github.com/itsmerbk)")
    print("=" * 68)
    time.sleep(1.5)

    print("\n>>> Running end-to-end Task Synthesis, Sandbox Validation & Benchmark...\n")
    time.sleep(1)
    subprocess.run([sys.executable, "run_pipeline.py"], check=False)
    time.sleep(3)

    verified_file = Path("results/verified_tasks.jsonl")
    if verified_file.exists():
        first_task = json.loads(verified_file.read_text(encoding="utf-8").splitlines()[0])
        print("\n>>> Sample Verified Task Artifact (results/verified_tasks.jsonl):")
        print(json.dumps({
            "task_id": first_task["task_id"],
            "domain": first_task["domain"],
            "difficulty": first_task["difficulty"],
            "function_name": first_task["function_name"],
            "prompt": first_task["prompt"],
        }, indent=2))
        time.sleep(3.5)

    print("\n>>> Switching to VS Code to inspect project files...")
    time.sleep(1)
    subprocess.run(
        ["osascript", "-e", 'tell application "Visual Studio Code" to activate'],
        check=False,
    )
    time.sleep(4)

    print(">>> Switching to GitHub repository...")
    subprocess.run(["open", REPO_URL], check=False)
    time.sleep(4)

    subprocess.run(
        ["osascript", "-e", 'tell application "Terminal" to activate'],
        check=False,
    )
    print("\n" + "=" * 68)
    print("  DEMO COMPLETE! Click the Stop Recording icon in the top menu bar.")
    print("=" * 68 + "\n")

if __name__ == "__main__":
    open_workspace()
    input(
        "\n[STEP 1] Click 'Record Entire Screen' in the bottom toolbar.\n"
        "[STEP 2] Once recording starts, press ENTER here to run the live demo..."
    )
    run_automated_walkthrough()
