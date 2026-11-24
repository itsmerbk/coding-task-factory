# Feature: Multi-Prefix Environment Precedence Resolver (`click.env_precedence`)

Implement `src/click/env_precedence.py` providing `resolve_env_chain(environ: dict[str, str], prefixes: list[str], key: str) -> str | None` which checks `<PREFIX>_<KEY.upper()>` in priority order, skips missing or whitespace-only values, strips outer whitespace, and returns `None` if unset.