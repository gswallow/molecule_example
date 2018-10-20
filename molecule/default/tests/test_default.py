# This suppresses about 80% of the deprecation warnings from python 3.7.
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import os
    import testinfra.utils.ansible_runner
    import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


# Yes, it's parametrize
@pytest.mark.parametrize('name', [
    'epel-release',
    'ius-release',
    'nginx',
    'python-setuptools',
    'python36u',
    'python36u-devel',
    'python36u-pip',
    'python36u-setuptools',
    'git',
    'sqlite',
    'uwsgi',
    'which'
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


def test_django(host):
    p = host.pip_package.get_packages(pip_path='/venv/bin/pip')
    assert 'Django' in p


@pytest.mark.parametrize('directory', [
    '/app',
    '/venv',
    '/run/uwsgi'
    ])
def test_paths(host, directory):
    d = host.file(directory)

    assert d.is_directory


def test_project(host):
    f = host.file('/app/django-blog/.git/config')

    assert f.is_file


def test_manage_py_perms(host):
    f = host.file('/app/django-blog/manage.py')

    assert oct(f.mode) == '0o755'


def test_uwsgi(host):
    s = host.service('uwsgi')

    assert s.is_running
    assert s.is_enabled
