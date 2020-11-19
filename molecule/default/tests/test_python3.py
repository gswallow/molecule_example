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
    'python-setuptools',
    'python3',
    'python3-devel',
    'python3-pip',
    'python3-setuptools'
    ])
def test_package(host, name):
    p = host.package(name)

    assert p.is_installed


@pytest.mark.parametrize('package', [
    'pip',
    'setuptools',
    'virtualenv',
    ])
def test_pip(host, package):
    p = host.pip_package.get_packages(pip_path='pip3.6')
    assert package in p
