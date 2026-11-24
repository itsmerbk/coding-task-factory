import click
from click.testing import CliRunner
from click.mutex_options import validate_mutually_exclusive

def test_mutex_conflict_raises_usage_error():
    @click.command()
    @click.option('--json', 'as_json', is_flag=True)
    @click.option('--yaml', 'as_yaml', is_flag=True)
    @click.pass_context
    def cli(ctx, as_json, as_yaml):
        validate_mutually_exclusive(ctx, ['as_json', 'as_yaml'])
        click.echo('OK')

    runner = CliRunner()
    assert runner.invoke(cli, ['--json']).exit_code == 0
    conflict = runner.invoke(cli, ['--json', '--yaml'])
    assert conflict.exit_code == 2
    assert 'as_json' in conflict.output and 'as_yaml' in conflict.output
