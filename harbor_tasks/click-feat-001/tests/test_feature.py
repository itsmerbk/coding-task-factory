import pytest
import click
from click.testing import CliRunner
from click.bounded_int import BoundedIntParamType

def test_invalid_constructor_bounds():
    with pytest.raises(ValueError):
        BoundedIntParamType(10, 5)

def test_cli_inclusive_bounds_and_rejection():
    @click.command()
    @click.option('--workers', type=BoundedIntParamType(1, 8), default=None)
    def cli(workers):
        click.echo(f'W={workers}')

    runner = CliRunner()
    assert runner.invoke(cli, []).output.strip() == 'W=None'
    assert runner.invoke(cli, ['--workers', '1']).output.strip() == 'W=1'
    assert runner.invoke(cli, ['--workers', '8']).output.strip() == 'W=8'
    assert runner.invoke(cli, ['--workers', '0']).exit_code != 0
    assert runner.invoke(cli, ['--workers', '9']).exit_code != 0
