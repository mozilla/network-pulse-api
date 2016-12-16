# The Mozilla Foundation Network Pulse API Server

... text goes here!...

## getting up and running for local development

You'll need `python` (v3) with `pip` (latest) and optionally `virtualenv` (python3 comes with a way to build virtual environments, but you can also install `virtualenv` as a dedicated library if you prefer)

1. clone this repo
2. set up a virtual environment in the `network-pulse-api` directory
3. set up a Google client (https://console.developers.google.com/apis/credentials) 
4. generate a `client_secrets.json` by running `> python generate_client_secrets.json`, then edit this file so that it has your client's `client_id` and `client_secret`, with `http://test.stuff.com:8000/oauth2callback` as your callback URI (double check that's what it's set to. It should be, but it's super important you check this).
5. bootstrap the Django setup:

- `python manage.py migrate` (or `python manage.py migrate --run-syncdb` on subsequent rebootstrap attempts, if things in the DB are broken)
- `python manage.py makemigrations` (creates files that instruct django how to uplift the database to match your current models)
- `python manage.py migrate` (performs the database migrations to your latest model specifications, based on the previous command's migration files)

## running the server

As a Django server, this API server is run like any other Django server:

- `python manage.py runserver`

## Using a localhost rebinding to a "real" domain

Google Auth does not like oauth2 to `localhost`, so you will need to set up a host binding such that 127.0.0.1 looks like a real domain. You can do this by editing your `hosts` file (in `/etc/hosts` on most unix-like systems, or `Windows\System32\Drivers\etc\hosts` in Windows). Add the following rule:

`127.0.0.1    test.stuff.com`

and then use `http://test.stuff.com:8000` instead of `http://localhost:8000` everywhere. Google Auth should now be perfectly happy.


## Setting up your superuser

Run `> python manage.py createsuperuser` to create a super user for accessing the Django `/admin` route. This setup uses a custom User model that uses an email address as primary identifier, so you will be prompted for an email, a name, and a password (twice).

I like using:

```
email: admin@example.com
name: admin
password: admin
password (again): admin
```

because it's easy to remember and doesn't require any kind of password management beyond "the browser itself".
