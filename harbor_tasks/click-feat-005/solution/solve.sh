#!/bin/bash
set -e
cat << 'PYEOF' > /app/src/click/json_help.py
import json
import click

def export_command_schema(cmd: click.Command) -> str:
    payload = {
        'name': cmd.name,
        'help': cmd.help or '',
        'params': [
            {
                'name': p.name,
                'param_type_name': p.param_type_name,
                'required': bool(p.required),
                'default': p.default,
            }
            for p in cmd.params
        ],
    }
    return json.dumps(payload, indent=2)
PYEOF
