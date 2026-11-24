#!/bin/bash
set -e
cat << 'PYEOF' > /app/src/click/mutex_options.py
import click

def validate_mutually_exclusive(ctx: click.Context, option_names: list[str]) -> None:
    active = [name for name in option_names if ctx.params.get(name) not in (None, False, '')]
    if len(active) > 1:
        joined = ', '.join(sorted(active))
        raise click.UsageError(f'Options are mutually exclusive: {joined}', ctx=ctx)
PYEOF
