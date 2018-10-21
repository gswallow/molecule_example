# This suppresses about 80% of the deprecation warnings from python 3.7.
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import os
    import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_settings_py(host):
    c = host.file('/app/django-blog/mysite/settings.py').content

    assert b'ALLOWED_HOSTS = ["*"]' in c


def test_etc_uwsgi_d_blog_ini(host):
    f = host.file('/etc/uwsgi.d/blog.ini')

    assert f.exists


def test_run_uwsgi_uwsgi_sock(host):
    f = host.file('/run/uwsgi/uwsgi.sock')

    assert f.is_socket


def test_uwsgi(host):
    s = host.service('uwsgi')

    assert s.is_running
    assert s.is_enabled
