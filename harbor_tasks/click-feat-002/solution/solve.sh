#!/bin/bash
set -e
cat << 'PYEOF' > /app/src/click/env_precedence.py
def resolve_env_chain(environ: dict[str, str], prefixes: list[str], key: str) -> str | None:
    norm_key = key.strip().upper()
    for prefix in prefixes:
        var_name = f'{prefix.strip().upper()}_{norm_key}'
        raw = environ.get(var_name)
        if raw is not None and raw.strip() != '':
            return raw.strip()
    return None
PYEOF
