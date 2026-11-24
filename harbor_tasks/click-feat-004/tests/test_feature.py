import click
from click.testing import CliRunner
from click.ctx_lifo_guard import register_lifo_resources

def test_lifo_cleanup_on_exception():
    log = []
    @click.command()
    @click.pass_context
    def cli(ctx):
        register_lifo_resources(ctx, ['db', 'cache', 'lock'], log)
        raise click.ClickException('abort')

    runner = CliRunner()
    res = runner.invoke(cli, [])
    assert res.exit_code != 0
    assert log == ['open:db', 'open:cache', 'open:lock', 'close:lock', 'close:cache', 'close:db']
