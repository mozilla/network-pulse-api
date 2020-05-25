import re
from sys import platform

from invoke import task

# Workaround for homebrew installation of Python (https://bugs.python.org/issue22490)
import os
os.environ.pop('__PYVENV_LAUNCHER__', None)

ROOT = os.path.dirname(os.path.realpath(__file__))

# Python commands's outputs are not rendering properly. Setting pty for *Nix system and
# "PYTHONUNBUFFERED" env var for Windows at True.
if platform == 'win32':
    PLATFORM_ARG = dict(env={'PYTHONUNBUFFERED': 'True'})
else:
    PLATFORM_ARG = dict(pty=True)


def create_env_file(env_file):
    """Create or update the .env file"""
    with open(env_file, 'r') as f:
        env_vars = f.read()
    # update the DATABASE_URL env
    new_db_url = "DATABASE_URL=postgres://postgres@localhost:5432/pulse"
    old_db_url = re.search('DATABASE_URL=.*', env_vars)
    if old_db_url:
        env_vars = env_vars.replace(old_db_url.group(0), new_db_url)
    else:
        env_vars = env_vars + "DATABASE_URL=postgres://postgres@localhost:5432/pulse\n"

    # update the ALLOWED_HOSTS env
    new_hosts = "ALLOWED_HOSTS=*"
    old_hosts = re.search('ALLOWED_HOSTS=.*', env_vars)
    if old_hosts:
        env_vars = env_vars.replace(old_hosts.group(0), new_hosts)
    else:
        env_vars = env_vars + "ALLOWED_HOSTS=*\n"

    # create the new env file
    with open('.env', 'w') as f:
        f.write(env_vars)


def create_super_user(ctx):
    preamble = "from django.contrib.auth import get_user_model;User = get_user_model();"
    create = "User.objects.create_superuser('admin', 'admin@mozillafoundation.org', 'admin')"
    manage(ctx, f'shell -c "{preamble} {create}"')
    print("\nCreated superuser `admin@mozillafoundation.org` with password `admin`.")


# Project setup and update
@task(aliases=["new-env"])
def setup(ctx):
    """Automate project's configuration and dependencies installation"""
    with ctx.cd(ROOT):
        if os.path.isfile(".env"):
            print("* Updating your .env")
            create_env_file(".env")
        else:
            print("* Creating a new .env")
            create_env_file("sample.env")
        # create virtualenv
        if not os.path.isfile("./pulsevenv/bin/python"):
            print("* Creating a Python virtual environment")
            ctx.run("python3 -m venv pulsevenv")
            print("* Installing pip-tools")
            ctx.run("./pulsevenv/bin/pip install pip-tools")
        # install deps
        print("* Installing Python dependencies")
        pip_sync(ctx)
        new_db(ctx)


@task(aliases=["catchup"])
def catch_up(ctx):
    """Install dependencies and apply migrations"""
    print("Installing Python dependencies")
    pip_sync(ctx)
    print("Applying database migrations")
    migrate(ctx)


@task
def new_db(ctx):
    """Create a new database with fake data"""
    print("* Reset the database")
    ctx.run("dropdb --if-exists -h localhost pulse")
    ctx.run("createdb -h localhost pulse")
    print("* Migrating database")
    migrate(ctx)
    print("* Creating fake data")
    manage(ctx, "load_fake_data")
    create_super_user(ctx)
    print("* Done!\n"
          "You can get a full list of inv commands with 'inv -l'\n"
          "Start you server with 'inv runserver'\n"
          )


# Django shorthands
@task
def manage(ctx, command):
    """Shorthand to manage.py. inv docker-manage \"[COMMAND] [ARG]\""""
    with ctx.cd(ROOT):
        ctx.run(f"./pulsevenv/bin/python manage.py {command}", **PLATFORM_ARG)


@task
def runserver(ctx):
    """Start a web server"""
    manage(ctx, "runserver")


@task
def migrate(ctx):
    """Updates database schema"""
    manage(ctx, "migrate")


@task
def makemigrations(ctx):
    """Creates new migration(s) for apps"""
    manage(ctx, "makemigrations")


# Tests
@task
def test(ctx):
    """Run tests"""
    print("Running flake8")
    ctx.run("./pulsevenv/bin/python -m flake8 pulseapi", **PLATFORM_ARG)
    print("Running tests")
    manage(ctx, "test")


# Pip-tools
@task(aliases=["docker-pip-compile"])
def pip_compile(ctx, command):
    """Shorthand to pip-tools. inv pip-compile \"[COMMAND] [ARG]\""""
    with ctx.cd(ROOT):
        ctx.run(
            f"./pulsevenv/bin/pip-compile {command}",
            **PLATFORM_ARG,
        )


@task(aliases=["docker-pip-compile-lock"])
def pip_compile_lock(ctx):
    """Lock prod and dev dependencies"""
    with ctx.cd(ROOT):
        ctx.run(
            "./pulsevenv/bin/pip-compile",
            **PLATFORM_ARG,
        )
        ctx.run(
            "./pulsevenv/bin/pip-compile dev-requirements.in",
            **PLATFORM_ARG,
        )


@task(aliases=["docker-pip-sync"])
def pip_sync(ctx):
    """Sync your python virtualenv"""
    with ctx.cd(ROOT):
        ctx.run(
            "./pulsevenv/bin/pip-sync requirements.txt dev-requirements.txt",
            **PLATFORM_ARG,
        )
