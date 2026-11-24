# Feature: Machine-Readable JSON Command Schema Exporter (`click.json_help`)

Implement `src/click/json_help.py` exposing `export_command_schema(cmd: click.Command) -> str` which serializes the command's `name`, `help`, and list of `params` (each with `name`, `param_type_name`, `required`, and `default`) into a deterministic JSON string.