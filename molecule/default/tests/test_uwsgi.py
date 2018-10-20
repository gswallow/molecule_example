# This suppresses about 80% of the deprecation warnings from python 3.7.
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import os
    import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_uwsgi(host):
    s = host.service('uwsgi')

    assert s.is_running
    assert s.is_enabled


def test_nginx(host):
    s = host.service('nginx')

    assert s.is_running


def test_port_81(host):
    s = host.socket("tcp://0.0.0.0:81")

    assert s.is_listening
