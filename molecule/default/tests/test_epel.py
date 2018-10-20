# This suppresses about 80% of the deprecation warnings from python 3.7.
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import os
    import testinfra.utils.ansible_runner
    import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


# Yes, it's parametrize
@pytest.mark.parametrize('name', [
    'epel-release',
    'ius-release'
    ])
def test_package(host, name):
    p = host.package(name)

    assert p.is_installed
