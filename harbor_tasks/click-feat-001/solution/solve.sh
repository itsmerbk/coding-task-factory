#!/bin/bash
set -e
cat << 'PYEOF' > /app/src/click/bounded_int.py
import click

class BoundedIntParamType(click.ParamType):
    name = 'bounded_int'

    def __init__(self, min_value: int, max_value: int) -> None:
        if min_value > max_value:
            raise ValueError('min_value cannot exceed max_value')
        self.min_value = min_value
        self.max_value = max_value

    def convert(self, value, param, ctx):
        if value is None:
            return None
        try:
            num = int(value)
        except (TypeError, ValueError):
            self.fail(f'{value!r} is not a valid integer', param, ctx)
        if num < self.min_value or num > self.max_value:
            self.fail(f'{num} must be between {self.min_value} and {self.max_value}', param, ctx)
        return num
PYEOF
