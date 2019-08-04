from pathlib import Path

import mock
from click.testing import CliRunner
from pixivapi import LoginError

from pixi.commands import auth, config
from pixi.errors import PixiError


@mock.patch('pixi.commands.Config')
@mock.patch('pixi.commands.Client')
def test_auth_failure(client, _):
    client.return_value.login.side_effect = LoginError
    result = CliRunner().invoke(auth, ['-u', 'u', '-p', 'p'])
    assert isinstance(result.exception, PixiError)


@mock.patch('pixi.commands.Config')
@mock.patch('pixi.commands.Client')
def test_auth_success(client, config):
    client.return_value.refresh_token = 'token value'
    config_dict = {'pixi': {}}
    config.return_value = config_dict

    CliRunner().invoke(auth, ['-u', 'u', '-p', 'p'])
    assert config_dict['pixi']['refresh_token'] == 'token value'


@mock.patch('click.edit')
def test_edit_config_completed(edit, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        config_path = Path.cwd() / 'config.ini'
        with config_path.open('w') as f:
            f.write('a bunch of text')

        monkeypatch.setattr('pixi.commands.CONFIG_PATH', config_path)
        edit.return_value = 'text2'
        result = runner.invoke(config)
        assert result.output == 'Edit completed.\n'

        assert edit.called_with('a bunch of text')

        with config_path.open('r') as f:
            assert 'text2' == f.read()


@mock.patch('click.edit')
def test_edit_config_aborted(edit, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        config_path = Path.cwd() / 'config.ini'
        with config_path.open('w') as f:
            f.write('a bunch of text')

        monkeypatch.setattr('pixi.commands.CONFIG_PATH', config_path)
        edit.return_value = None
        result = runner.invoke(config)
        assert result.output == 'Edit aborted.\n'

        with config_path.open('r') as f:
            assert 'a bunch of text' == f.read()
