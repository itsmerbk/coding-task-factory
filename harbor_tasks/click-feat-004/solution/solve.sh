#!/bin/bash
set -e
cat << 'PYEOF' > /app/src/click/ctx_lifo_guard.py
import click

def register_lifo_resources(ctx: click.Context, resources: list[str], audit_log: list[str]) -> None:
    for res in resources:
        audit_log.append(f'open:{res}')
        ctx.call_on_close(lambda r=res: audit_log.append(f'close:{r}'))
PYEOF
