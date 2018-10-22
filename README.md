## Test-driven Ansible Role Development with Molecule and Docker

[Molecule](https://molecule.readthedocs.io/) is a testing framework 
that can fire up a VM or a Linux container and test an Ansible role through 
scenarios (example playbooks). It checks the syntax of the scenario playbook 
(and thus, the associated role), converges the VM or container, and then 
tests that Ansible did its job with [TestInfra](https://testinfra.readthedocs.io/).

### Why docker?

Spinning up a container takes a fraction of the time it takes to spin up a VM 
using Vagrant.

### Homebrew

On a Mac, some components should be installed with [Homebrew](https://brew.sh/).
The python bits should be installed with Python pip, once Homebrew has it set up.

Homebrew sets up Python 3 so that non-privileged users can install Python
modules with pip in `/usr/local/lib/python3.x`. Binary symlinks get created in
`/usr/local/bin`. So far, it’s working ok without having to use virtualenv on my Mac.

### Getting started

Installing on a Mac with homebrew and pip:

        brew install python
        brew cask install docker

        pip --version
        # pip 18.0 from /usr/local/lib/python3.7/site-packages/pip (python 3.7)
        
        pip install molecule docker
        
        cat >> ~/.bash_profile <<EOF
        # Molecule autocomplete
        eval "$(_MOLECULE_COMPLETE=source molecule)"
        EOF

Stop here an open the docker application through Finder.
        
        # test it out:
        docker run --name test -d centos /bin/bash -c 'echo it worked'
        docker logs test

This repository is set up to fail.  You'll be running `molecule test` to uncover bugs
in the test suite, and fixing those bugs as you go.

### Running molecule

Simply running `molecule` will generate command help. Some commands are complex, 
while some commands are simple. `molecule matrix` explains what a complex command does:

        $ molecule matrix test
        --> Validating schema /Users/gswallow/src/greg/molecule-example/molecule/default/molecule.yml.
        Validation completed successfully.
        --> Test matrix  
        └── default
            ├── lint
            ├── destroy
            ├── dependency
            ├── syntax
            ├── create
            ├── prepare
            ├── converge
            ├── idempotence
            ├── side_effect
            ├── verify
            └── destroy

The complex commands understandably take a while to run because they do a lot 
of things. You can control these steps by hand, which speeds up your ability 
to fix errors in response to failing tests:

- `molecule create` creates your test subject (container or VM)
- `molecule converge` runs Ansible on your test subject
- `molecule verify` runs TestInfra on the converged test subject

You can get the current status of your test subject with `molecule list`.

### Creating a role:

        cd ~/src
        molecule init -r my-role [-d azure|delegated|docker|ec2|gce|lxc|lxd|openstack|vagrant]

Running `molecule init` creates a new folder with scaffolding to run other 
molecule commands. The driver can be any of the examples, above. By default, 
the driver is “docker.” Inside the “my-role” file, you’ll find the 
`molecule/default` directory, with a molecule.yml file. The “default” directory reflects 
the “default” scenario (there can be more than one scenario). The molecule.yml 
file defines settings that control Docker, Ansible, Ansible Galaxy, and 
Testinfra. By default, a simple test will check that the `/etc/hosts` file exists 
in a Docker container. If you run `molecule test` in side the example role 
directory, it should pass. Let’s make it not pass.

### Writing tests

Tests are written with Testinfra. They’re placed in the `molecule/default/tests` directory. 
Function names must start with ‘test_’. Let’s test that nginx is installed by our Ansible role:

        # This suppresses about 80% of the deprecation warnings from python 3.7.
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            import os
            import testinfra.utils.ansible_runner
        
        testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
            os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')
        
        
        def test_hosts_file(host):
            f = host.file('/etc/hosts')
        
            assert f.exists
            assert f.user == 'root'
            assert f.group == 'root'
        
        
        def test_nginx_package(host):
            p = host.package('nginx')
        
            assert p.is_installed

A bit of an aside: note the warning suppression at the top of the file. Something’s 
up with Python 3.7 cluttering output with deprecation warnings. Let’s run our test:

        molecule create && molecule converge && molecule verify
        ...
            ____________________ test_nginx_package[ansible://instance] ____________________
            
            host = <testinfra.host.Host object at 0x105dbf668>
            
                def test_nginx_package(host):
                    p = host.package('nginx')
                
            >       assert p.is_installed
            E       assert False
            E        +  where False = <package nginx>.is_installed
            
            tests/test_default.py:23: AssertionError

Our test fails because nginx is not installed. Let’s install nginx. Edit the 
`tasks/main.yml` file and add a task to install nginx:

        - name: "Install nginx package"
          yum:
            name: nginx
            state: present

It should pass. Run `molecule converge`.
        
         TASK [molecule-example : Install nginx package] ********************************
            fatal: [instance]: FAILED! => {"changed": false, "msg": "No package matching 'nginx' found available, installed or updated", "rc": 126, "results": ["No package matching 'nginx' found available, installed or updated"]}

Whoops. There’s no package named ‘nginx.' Let’s fix that. Edit the `molecule/default/tests/test_default.py`
file and add ‘epel-release’ to the list of packages:
        
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            import os
            import testinfra.utils.ansible_runner
            import pytest
        # ^^^ Note that we change the top of the file to import pytest ^^^
        
        # Yes, it's parametrize
        @pytest.mark.parametrize('name', ['epel-release', 'nginx'])
        def test_package(host, name):
            p = host.package(name)
        
            assert p.is_installed

Add EPEL to the `tasks/main.yml` file:

        ---
        - name: "Enable EPEL and install nginx""
          yum:
            name: "{{ item }}"
            state: present
          with_items:
            - epel-release
            - nginx

Run `molecule converge`, and `molecule verify` again. The tests should pass, 
and instead of running two tests, you’ll have run three.

### Importing roles

We’ll fast forward a bit here, installing django, virtulaenv, git and standing 
up an example Django app. What's important is that we’re going to use 
Galaxy. Ansible Galaxy is a collection of reusable roles maintained by the Ansible 
community. Let’s import a role to manage a Django app. Modify the 
`molecule/default/molecule.yml` file, then create a `requirements.yml` file:

        ---
        # molecule.yml
        dependency:
          name: galaxy
          options:
            role-file: requirements.yml
            
        ---
        - name: "cchurch.django"
          version: '0.5.6'

Let’s test that we can satisfy our dependencies by running `molecule dependency`. 

### Template and variable scope

Depending on the role is fine but let’s use it. Edit the `molecule/default/playbook.yml` 
file to include the role and set some variables that the django role requires. Note that
we define variables for the `cchurch.django` role in our playbook, but *NOT* in our
role's `vars` or `defaults` direcrtories. 

When creating templates just for testing, the same rule applies.  Drop templates into
the `molecule/default/templates` folder, instead of directly into your role.

Finally, we’ll include the role in the play:

        ---
        - name: Converge
          hosts: all 
          vars:
            django_app_path: /app/django-blog
            django_virtualenv: /venv
            django_main_commands:
              - command: migrate
              - command: loaddata 
                fixtures: users posts comments
            django_user: root
        
          roles:
            - role: molecule-example
            - role: cchurch.django

#### Molecule test flags and test_sequence

Note that `molecule test`, above, will destroy your test subject when a test fails.
Repeatedly creating docker containers and running Ansible is slow.  Using the `--destroy never`
flag suppresses this behavior.

Also note that `molecule test` runs idempotence checks.  You can rely on idempotence
checks to test your own role, but others' roles that you depend on may not be idempotent
(and probably aren't!).  You can disable individual test suites in the 
`molecule/default/molecule.yml` file once your own role passes the idempotence test.  Which 
leads us to...

### Scenarios

Perhaps you want to test the idempotence of your Ansible role by hand, but you don't want 
your CI server to trip on idempotence checks.  This is a reason to use Molecule scenarios.
Thankfully, you can DRY up your scenarios by sharing tests and playbooks.  See [this](https://molecule.readthedocs.io/en/latest/examples.html#sharing-across-scenarios)
page for details on how to set up multiple scenarios.

### Credit

Getting started, I was heavily informed by [this article](https://hashbangwallop.com/tdd-ansible.html).  Props.
