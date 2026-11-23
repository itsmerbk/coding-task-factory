# Coding Task Factory - Innodata Frontier AI Hackathon 2026

An automated, deterministic pipeline that synthesizes multi-domain software engineering tasks, verifies solvability and non-triviality via AST static checks and isolated subprocess sandboxes, and benchmarks frontier coding models (`pass@1`).

## Architecture
1. **Task Synthesizer (`factory/generator.py`):** Generates parameterized tasks across `algorithms`, `systems_security`, and `data_structures` with Easy/Medium/Hard tiers and edge-case test suites.
2. **Quality & Validation Gate (`factory/validator.py`):** Enforces AST safety checks, runs reference solutions in isolated `-I` subprocess sandboxes with strict timeouts, and rejects weak tests if a trivial stub passes.
3. **Evaluation Harness (`factory/benchmark.py`):** Evaluates candidate model outputs and exports `pass@1` metrics and failure logs to `results/`.

## Quickstart
    python3 run_pipeline.py
