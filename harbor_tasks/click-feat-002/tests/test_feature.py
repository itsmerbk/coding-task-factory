from click.env_precedence import resolve_env_chain

def test_ordered_prefix_fallback_and_whitespace():
    env = {'APP_OVERRIDE_HOST': '   ', 'APP_HOST': ' 10.0.0.5 ', 'DEFAULT_HOST': '127.0.0.1'}
    assert resolve_env_chain(env, ['APP_OVERRIDE', 'APP', 'DEFAULT'], 'host') == '10.0.0.5'

def test_unset_returns_none():
    assert resolve_env_chain({}, ['APP', 'DEFAULT'], 'port') is None
