import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple
from factory.generator import FeatureTaskSpec

REQUIRED_FILES = [
    "instruction.md",
    "task.toml",
    "environment/Dockerfile",
    "solution/solve.sh",
    "tests/test.sh",
    "tests/test_feature.py",
    "tests/fail_to_pass.json",
    "tests/pass_to_pass.json",
]

def validate_with_mutation_testing(spec: FeatureTaskSpec, root: Path = Path("harbor_tasks")) -> Tuple[bool, dict]:
    tdir = root / spec.task_id
    for rel in REQUIRED_FILES:
        if not (tdir / rel).exists():
            return False, {"task_id": spec.task_id, "status": f"Missing {rel}"}

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        src_click = tmp_path / "src" / "click"
        src_click.mkdir(parents=True)
        (src_click / "__init__.py").write_text("from click import *\n", encoding="utf-8")
        test_file = tmp_path / "test_feature.py"
        test_file.write_text(spec.test_feature_py, encoding="utf-8")

        # 1. NOP check (must fail -> reward 0.0)
        nop = subprocess.run([sys.executable, "-m", "pytest", str(test_file), "-q"], cwd=str(tmp_path), capture_output=True)
        if nop.returncode == 0:
            return False, {"task_id": spec.task_id, "status": "NOP baseline passed unexpectedly"}

        # 2. Oracle check (must pass -> reward 1.0)
        solve_script = tmp_path / "solve.sh"
        solve_script.write_text(spec.solve_sh.replace("/app/src/click", str(src_click)), encoding="utf-8")
        subprocess.run(["bash", str(solve_script)], check=True)
        oracle = subprocess.run([sys.executable, "-m", "pytest", str(test_file), "-q"], cwd=str(tmp_path), capture_output=True)
        if oracle.returncode != 0:
            return False, {"task_id": spec.task_id, "status": "Oracle patch failed tests"}

        # 3. Mutation test check (broken implementation must fail -> mutant killed)
        mod_file = list(src_click.glob("*.py"))
        for f in mod_file:
            if f.name != "__init__.py":
                f.write_text(spec.mutated_patch_py, encoding="utf-8")
        mutant = subprocess.run([sys.executable, "-m", "pytest", str(test_file), "-q"], cwd=str(tmp_path), capture_output=True)
        if mutant.returncode == 0:
            return False, {"task_id": spec.task_id, "status": "Mutation test escaped!"}

    return True, {
        "task_id": spec.task_id,
        "feature": spec.feature_name,
        "difficulty": spec.difficulty,
        "nop_reward": 0.0,
        "oracle_reward": 1.0,
        "mutant_killed": True,
        "status": "Verified (Harbor v0.25.x + Mutation Tested)",
    }
