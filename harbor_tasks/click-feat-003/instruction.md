# Feature: Mutually Exclusive Option Validator (`click.mutex_options`)

Implement `src/click/mutex_options.py` with `validate_mutually_exclusive(ctx: click.Context, option_names: list[str]) -> None` that inspects `ctx.params` for truthy/non-None values among `option_names`. If two or more are simultaneously active, raise `click.UsageError` naming the conflicting options.