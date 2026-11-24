# Coding Task Factory — Team Technicians (Innodata AI Hackathon 2026)

- **Team Name:** Technicians
- **Team Leader:** Bharath Kumar R (`itsmerbk`)
- **Track:** Track 1 — Coding Task Factory
- **Designated Starter Repository:** `https://github.com/pallets/click.git`
- **Verified Starting Commit (`base_commit`):** `5884a16262a6735a68c742649818229747a27e9e` (Release Tag `8.1.8`)
- **Task Framework:** Harbor CLI `v0.25.x` (`pip install "harbor==0.25.*"`)

## 1. System Architecture & Technical Design
1. **Repository & Baseline Anchor (`factory/generator.py`):** Clones `pallets/click` at verified 40-character release commit SHA `5884a16262a6735a68c742649818229747a27e9e` where all upstream `pytest` regression tests pass.
2. **Feature-Development Synthesizer:** Generates **5 substantively distinct feature tasks** (`harbor_tasks/click-feat-001` to `click-feat-005`) covering new CLI features rather than bug fixes:
   - `click-feat-001`: Inclusive `BoundedIntParamType` with `BadParameter` diagnostics
   - `click-feat-002`: Ordered multi-prefix environment variable precedence resolver
   - `click-feat-003`: Declarative mutually exclusive CLI option group validator
   - `click-feat-004`: Scoped `click.Context` LIFO resource cleanup guard
   - `click-feat-005`: Machine-readable JSON command schema exporter
3. **Harbor v0.25.x Packager:** Emits standardized 5-component Harbor directories (`instruction.md`, `task.toml`, `environment/Dockerfile`, `solution/solve.sh`, and `tests/test.sh` + `test_feature.py` + `fail_to_pass.json` + `pass_to_pass.json`).
4. **Dual-Gate & Mutation Validator (`factory/validator.py`):**
   - **Baseline (`nop`) Check:** Confirms new feature tests fail on unpatched commit (`reward = 0.0`).
   - **Oracle (`oracle`) Check:** Confirms 100% pass rate after `solution/solve.sh` applies the reference patch (`reward = 1.0`).
   - **Mutation Testing:** Injects deliberately broken implementations to verify a **100% mutant kill rate**.

## 2. Declared Tools & Models
- **Languages & Runtime:** Python 3.11+, Bash, Docker, Git
- **Benchmark & Testing Tools:** Harbor Framework (`v0.25.x`), `pytest`, `click.testing.CliRunner`, Python `ast` & automated mutation verifier
- **Models & AI Assistance:** Anthropic Claude API (`claude-sonnet-4-5`) and Gemini for task specification drafting and pipeline engineering

## 3. Quickstart & Harbor Validation Commands
```bash
# 1. Generate all 5 Harbor v0.25.x task packages and run validation + mutation tests
python3 run_pipeline.py

# 2. Run Harbor CLI validation passes (requires Docker & harbor==0.25.*)
harbor run -p harbor_tasks/click-feat-001 -a nop -k 1 -o results/nop_out --no-delete -y
harbor run -p harbor_tasks/click-feat-001 -a oracle -k 1 -o results/oracle_out --no-delete -y
```
