import json
import click
from click.json_help import export_command_schema

def test_export_command_schema_json():
    @click.command(name='deploy', help='Deploy service')
    @click.option('--replicas', type=int, default=2, required=True)
    def deploy(replicas):
        pass

    data = json.loads(export_command_schema(deploy))
    assert data['name'] == 'deploy'
    assert data['help'] == 'Deploy service'
    assert data['params'][0]['name'] == 'replicas'
    assert data['params'][0]['default'] == 2
    assert data['params'][0]['required'] is True
