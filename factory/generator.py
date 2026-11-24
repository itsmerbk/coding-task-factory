import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

CLICK_REPO = "https://github.com/pallets/click.git"
BASE_COMMIT = "934813e4d421071a1b3db3973c02fe2721359a6e"

@dataclass
class FeatureTaskSpec:
    task_id: str
    feature_name: str
    difficulty: str
    instruction_md: str
    task_toml: str
    dockerfile: str
    solve_sh: str
    test_sh: str
    test_feature_py: str
    mutated_patch_py: str
    fail_to_pass: List[str]
    pass_to_pass: List[str]

def build_five_distinct_tasks() -> List[FeatureTaskSpec]:
    tasks_data = [
        {
            "task_id": "click-feat-001",
            "feature_name": "BoundedIntParamType",
            "difficulty": "easy",
            "module": "bounded_int",
            "instruction": (
                "# Feature: Inclusive Bounded Integer Parameter Type (`click.bounded_int`)\n\n"
                "Implement `src/click/bounded_int.py` exposing `BoundedIntParamType(click.ParamType)` "
                "initialized with `min_value: int` and `max_value: int` (raising `ValueError` if `min_value > max_value`). "
                "During `convert(value, param, ctx)`, pass `None` unchanged, coerce valid integers within `[min_value, max_value]`, "
                "and call `self.fail(...)` for non-integers or out-of-range values."
            ),
            "code": (
                "import click\n\n"
                "class BoundedIntParamType(click.ParamType):\n"
                "    name = 'bounded_int'\n\n"
                "    def __init__(self, min_value: int, max_value: int) -> None:\n"
                "        if min_value > max_value:\n"
                "            raise ValueError('min_value cannot exceed max_value')\n"
                "        self.min_value = min_value\n"
                "        self.max_value = max_value\n\n"
                "    def convert(self, value, param, ctx):\n"
                "        if value is None:\n"
                "            return None\n"
                "        try:\n"
                "            num = int(value)\n"
                "        except (TypeError, ValueError):\n"
                "            self.fail(f'{value!r} is not a valid integer', param, ctx)\n"
                "        if num < self.min_value or num > self.max_value:\n"
                "            self.fail(f'{num} must be between {self.min_value} and {self.max_value}', param, ctx)\n"
                "        return num\n"
            ),
            "mutant": (
                "import click\n\n"
                "class BoundedIntParamType(click.ParamType):\n"
                "    name = 'bounded_int'\n"
                "    def __init__(self, min_value: int, max_value: int) -> None:\n"
                "        self.min_value = min_value\n"
                "        self.max_value = max_value\n"
                "    def convert(self, value, param, ctx):\n"
                "        return int(value) if value is not None else None\n"
            ),
            "test_py": (
                "import pytest\n"
                "import click\n"
                "from click.testing import CliRunner\n"
                "from click.bounded_int import BoundedIntParamType\n\n"
                "def test_invalid_constructor_bounds():\n"
                "    with pytest.raises(ValueError):\n"
                "        BoundedIntParamType(10, 5)\n\n"
                "def test_cli_inclusive_bounds_and_rejection():\n"
                "    @click.command()\n"
                "    @click.option('--workers', type=BoundedIntParamType(1, 8), default=None)\n"
                "    def cli(workers):\n"
                "        click.echo(f'W={workers}')\n\n"
                "    runner = CliRunner()\n"
                "    assert runner.invoke(cli, []).output.strip() == 'W=None'\n"
                "    assert runner.invoke(cli, ['--workers', '1']).output.strip() == 'W=1'\n"
                "    assert runner.invoke(cli, ['--workers', '8']).output.strip() == 'W=8'\n"
                "    assert runner.invoke(cli, ['--workers', '0']).exit_code != 0\n"
                "    assert runner.invoke(cli, ['--workers', '9']).exit_code != 0\n"
            ),
            "f2p": [
                "tests/test_feature.py::test_invalid_constructor_bounds",
                "tests/test_feature.py::test_cli_inclusive_bounds_and_rejection",
            ],
            "p2p": ["tests/test_types.py::test_int_range"],
        },
        {
            "task_id": "click-feat-002",
            "feature_name": "MultiPrefixEnvPrecedence",
            "difficulty": "medium",
            "module": "env_precedence",
            "instruction": (
                "# Feature: Multi-Prefix Environment Precedence Resolver (`click.env_precedence`)\n\n"
                "Implement `src/click/env_precedence.py` providing `resolve_env_chain(environ: dict[str, str], prefixes: list[str], key: str) -> str | None` "
                "which checks `<PREFIX>_<KEY.upper()>` in priority order, skips missing or whitespace-only values, strips outer whitespace, and returns `None` if unset."
            ),
            "code": (
                "def resolve_env_chain(environ: dict[str, str], prefixes: list[str], key: str) -> str | None:\n"
                "    norm_key = key.strip().upper()\n"
                "    for prefix in prefixes:\n"
                "        var_name = f'{prefix.strip().upper()}_{norm_key}'\n"
                "        raw = environ.get(var_name)\n"
                "        if raw is not None and raw.strip() != '':\n"
                "            return raw.strip()\n"
                "    return None\n"
            ),
            "mutant": (
                "def resolve_env_chain(environ: dict[str, str], prefixes: list[str], key: str) -> str | None:\n"
                "    return environ.get(f'{prefixes[-1]}_{key.upper()}')\n"
            ),
            "test_py": (
                "from click.env_precedence import resolve_env_chain\n\n"
                "def test_ordered_prefix_fallback_and_whitespace():\n"
                "    env = {'APP_OVERRIDE_HOST': '   ', 'APP_HOST': ' 10.0.0.5 ', 'DEFAULT_HOST': '127.0.0.1'}\n"
                "    assert resolve_env_chain(env, ['APP_OVERRIDE', 'APP', 'DEFAULT'], 'host') == '10.0.0.5'\n\n"
                "def test_unset_returns_none():\n"
                "    assert resolve_env_chain({}, ['APP', 'DEFAULT'], 'port') is None\n"
            ),
            "f2p": [
                "tests/test_feature.py::test_ordered_prefix_fallback_and_whitespace",
                "tests/test_feature.py::test_unset_returns_none",
            ],
            "p2p": ["tests/test_options.py::test_envvar_flag"],
        },
        {
            "task_id": "click-feat-003",
            "feature_name": "MutuallyExclusiveOptions",
            "difficulty": "medium",
            "module": "mutex_options",
            "instruction": (
                "# Feature: Mutually Exclusive Option Validator (`click.mutex_options`)\n\n"
                "Implement `src/click/mutex_options.py` with `validate_mutually_exclusive(ctx: click.Context, option_names: list[str]) -> None` "
                "that inspects `ctx.params` for truthy/non-None values among `option_names`. If two or more are simultaneously active, raise `click.UsageError` naming the conflicting options."
            ),
            "code": (
                "import click\n\n"
                "def validate_mutually_exclusive(ctx: click.Context, option_names: list[str]) -> None:\n"
                "    active = [name for name in option_names if ctx.params.get(name) not in (None, False, '')]\n"
                "    if len(active) > 1:\n"
                "        joined = ', '.join(sorted(active))\n"
                "        raise click.UsageError(f'Options are mutually exclusive: {joined}', ctx=ctx)\n"
            ),
            "mutant": (
                "import click\n\n"
                "def validate_mutually_exclusive(ctx: click.Context, option_names: list[str]) -> None:\n"
                "    return None\n"
            ),
            "test_py": (
                "import click\n"
                "from click.testing import CliRunner\n"
                "from click.mutex_options import validate_mutually_exclusive\n\n"
                "def test_mutex_conflict_raises_usage_error():\n"
                "    @click.command()\n"
                "    @click.option('--json', 'as_json', is_flag=True)\n"
                "    @click.option('--yaml', 'as_yaml', is_flag=True)\n"
                "    @click.pass_context\n"
                "    def cli(ctx, as_json, as_yaml):\n"
                "        validate_mutually_exclusive(ctx, ['as_json', 'as_yaml'])\n"
                "        click.echo('OK')\n\n"
                "    runner = CliRunner()\n"
                "    assert runner.invoke(cli, ['--json']).exit_code == 0\n"
                "    conflict = runner.invoke(cli, ['--json', '--yaml'])\n"
                "    assert conflict.exit_code == 2\n"
                "    assert 'as_json' in conflict.output and 'as_yaml' in conflict.output\n"
            ),
            "f2p": ["tests/test_feature.py::test_mutex_conflict_raises_usage_error"],
            "p2p": ["tests/test_parser.py::test_option_parser"],
        },
        {
            "task_id": "click-feat-004",
            "feature_name": "ScopedContextLifoGuard",
            "difficulty": "hard",
            "module": "ctx_lifo_guard",
            "instruction": (
                "# Feature: Scoped Context LIFO Resource Guard (`click.ctx_lifo_guard`)\n\n"
                "Implement `src/click/ctx_lifo_guard.py` defining `register_lifo_resources(ctx: click.Context, resources: list[str], audit_log: list[str]) -> None` "
                "that opens resources in forward order (`open:<name>`) and registers `ctx.call_on_close` hooks so resources close in strict LIFO order (`close:<name>`) even if a `ClickException` aborts execution."
            ),
            "code": (
                "import click\n\n"
                "def register_lifo_resources(ctx: click.Context, resources: list[str], audit_log: list[str]) -> None:\n"
                "    for res in resources:\n"
                "        audit_log.append(f'open:{res}')\n"
                "        ctx.call_on_close(lambda r=res: audit_log.append(f'close:{r}'))\n"
            ),
            "mutant": (
                "import click\n\n"
                "def register_lifo_resources(ctx: click.Context, resources: list[str], audit_log: list[str]) -> None:\n"
                "    for res in resources:\n"
                "        audit_log.append(f'open:{res}')\n"
            ),
            "test_py": (
                "import click\n"
                "from click.testing import CliRunner\n"
                "from click.ctx_lifo_guard import register_lifo_resources\n\n"
                "def test_lifo_cleanup_on_exception():\n"
                "    log = []\n"
                "    @click.command()\n"
                "    @click.pass_context\n"
                "    def cli(ctx):\n"
                "        register_lifo_resources(ctx, ['db', 'cache', 'lock'], log)\n"
                "        raise click.ClickException('abort')\n\n"
                "    runner = CliRunner()\n"
                "    res = runner.invoke(cli, [])\n"
                "    assert res.exit_code != 0\n"
                "    assert log == ['open:db', 'open:cache', 'open:lock', 'close:lock', 'close:cache', 'close:db']\n"
            ),
            "f2p": ["tests/test_feature.py::test_lifo_cleanup_on_exception"],
            "p2p": ["tests/test_context.py::test_context_close"],
        },
        {
            "task_id": "click-feat-005",
            "feature_name": "JsonHelpSchemaExporter",
            "difficulty": "hard",
            "module": "json_help",
            "instruction": (
                "# Feature: Machine-Readable JSON Command Schema Exporter (`click.json_help`)\n\n"
                "Implement `src/click/json_help.py` exposing `export_command_schema(cmd: click.Command) -> str` "
                "which serializes the command's `name`, `help`, and list of `params` (each with `name`, `param_type_name`, `required`, and `default`) into a deterministic JSON string."
            ),
            "code": (
                "import json\n"
                "import click\n\n"
                "def export_command_schema(cmd: click.Command) -> str:\n"
                "    payload = {\n"
                "        'name': cmd.name,\n"
                "        'help': cmd.help or '',\n"
                "        'params': [\n"
                "            {\n"
                "                'name': p.name,\n"
                "                'param_type_name': p.param_type_name,\n"
                "                'required': bool(p.required),\n"
                "                'default': p.default,\n"
                "            }\n"
                "            for p in cmd.params\n"
                "        ],\n"
                "    }\n"
                "    return json.dumps(payload, indent=2)\n"
            ),
            "mutant": (
                "import click\n\n"
                "def export_command_schema(cmd: click.Command) -> str:\n"
                "    return '{}'\n"
            ),
            "test_py": (
                "import json\n"
                "import click\n"
                "from click.json_help import export_command_schema\n\n"
                "def test_export_command_schema_json():\n"
                "    @click.command(name='deploy', help='Deploy service')\n"
                "    @click.option('--replicas', type=int, default=2, required=True)\n"
                "    def deploy(replicas):\n"
                "        pass\n\n"
                "    data = json.loads(export_command_schema(deploy))\n"
                "    assert data['name'] == 'deploy'\n"
                "    assert data['help'] == 'Deploy service'\n"
                "    assert data['params'][0]['name'] == 'replicas'\n"
                "    assert data['params'][0]['default'] == 2\n"
                "    assert data['params'][0]['required'] is True\n"
            ),
            "f2p": ["tests/test_feature.py::test_export_command_schema_json"],
            "p2p": ["tests/test_formatting.py::test_basic_functionality"],
        },
    ]

    specs: List[FeatureTaskSpec] = []
    for item in tasks_data:
        mod = item["module"]
        solve_sh = (
            "#!/bin/bash\n"
            "set -e\n"
            f"cat << 'PYEOF' > /app/src/click/{mod}.py\n"
            f"{item['code']}"
            "PYEOF\n"
        )
        task_toml = (
            'version = "1.0"\n\n'
            "[metadata]\n"
            'team_name = "Technicians"\n'
            'author_name = "Bharath Kumar R"\n'
            f'difficulty = "{item["difficulty"]}"\n'
            'category = "feature-development"\n'
            f'repository = "{CLICK_REPO}"\n'
            f'base_commit = "{BASE_COMMIT}"\n'
            'license = "BSD-3-Clause"\n\n'
            "[verifier]\n"
            "timeout_sec = 120.0\n\n"
            "[agent]\n"
            "timeout_sec = 180.0\n"
        )
        dockerfile = (
            "FROM python:3.11-slim\n"
            "RUN apt-get update && apt-get install -y --no-install-recommends git bash && rm -rf /var/lib/apt/lists/*\n"
            "WORKDIR /app\n"
            f"RUN git clone {CLICK_REPO} /app && git checkout {BASE_COMMIT}\n"
            "RUN pip install --no-cache-dir -e . pytest\n"
        )
        test_sh = (
            "#!/bin/bash\n"
            "set -e\n"
            "mkdir -p /logs/verifier\n"
            "if pytest /tests/test_feature.py -q; then\n"
            '  echo "1" > /logs/verifier/reward.txt\n'
            "else\n"
            '  echo "0" > /logs/verifier/reward.txt\n'
            "  exit 1\n"
            "fi\n"
        )
        specs.append(
            FeatureTaskSpec(
                task_id=item["task_id"],
                feature_name=item["feature_name"],
                difficulty=item["difficulty"],
                instruction_md=item["instruction"],
                task_toml=task_toml,
                dockerfile=dockerfile,
                solve_sh=solve_sh,
                test_sh=test_sh,
                test_feature_py=item["test_py"],
                mutated_patch_py=item["mutant"],
                fail_to_pass=item["f2p"],
                pass_to_pass=item["p2p"],
            )
        )
    return specs

def export_all_harbor_tasks(specs: List[FeatureTaskSpec], root: Path = Path("harbor_tasks")) -> None:
    if root.exists():
        import shutil
        shutil.rmtree(root)
    root.mkdir(parents=True)
    for s in specs:
        tdir = root / s.task_id
        (tdir / "environment").mkdir(parents=True)
        (tdir / "solution").mkdir(parents=True)
        (tdir / "tests").mkdir(parents=True)

        (tdir / "instruction.md").write_text(s.instruction_md, encoding="utf-8")
        (tdir / "task.toml").write_text(s.task_toml, encoding="utf-8")
        (tdir / "environment" / "Dockerfile").write_text(s.dockerfile, encoding="utf-8")
        solve_p = tdir / "solution" / "solve.sh"
        solve_p.write_text(s.solve_sh, encoding="utf-8")
        solve_p.chmod(0o755)
        test_sh_p = tdir / "tests" / "test.sh"
        test_sh_p.write_text(s.test_sh, encoding="utf-8")
        test_sh_p.chmod(0o755)
        (tdir / "tests" / "test_feature.py").write_text(s.test_feature_py, encoding="utf-8")
        (tdir / "tests" / "fail_to_pass.json").write_text(json.dumps(s.fail_to_pass, indent=2), encoding="utf-8")
        (tdir / "tests" / "pass_to_pass.json").write_text(json.dumps(s.pass_to_pass, indent=2), encoding="utf-8")
