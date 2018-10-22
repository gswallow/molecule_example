# This suppresses about 80% of the deprecation warnings from python 3.7.
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import os
    import testinfra.utils.ansible_runner
    # EXAMPLE_1: make the linter fail by importing an unused module
    # Hint: From now on, try running molecule test --destroy never
    import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_hosts_file(host):
    f = host.file('/etc/hosts')

    # EXAMPLE_7 break TestInfra by testing that /etc/hosts does not esist
    assert f.exists  # is not True
    assert f.user == 'root'
    assert f.group == 'root'


@pytest.mark.parametrize('name', ['which', 'iproute'])
def test_base_packages(host, name):
    p = host.package(name)

    assert p.is_installed


# def test_which_package(host):
#     p = host.package('which')
#
#     assert p.is_installed
#
#
# def test_iproute_package(host):
#     p = host.package('iproute')
#
#     assert p.is_installed
