# The Mozilla Foundation Network Pulse API Server

... text goes here!...

## Getting up and running for local development

You'll need `python` (v3) with `pip` (latest) and optionally `virtualenv` (python3 comes with a way to build virtual environments, but you can also install `virtualenv` as a dedicated library if you prefer)

1. clone this repo
2. set up a virtual environment in the `network-pulse-api` directory
3. set up a Google client (https://console.developers.google.com/apis/credentials)
4. generate a `client_secrets.json` by running `> python generate_client_secrets.py`, then edit this file so that it has your client's `client_id` and `client_secret`, with `http://test.example.com:8000/oauth2callback` as your callback URI (double check that's what it's set to. It should be, but it's super important you check this).
5. bootstrap the Django setup:

- `python manage.py migrate` (or `python manage.py migrate --run-syncdb` on subsequent rebootstrap attempts, if things in the DB are broken)
- `python manage.py makemigrations` (creates files that instruct django how to uplift the database to match your current models)
- `python manage.py migrate` (performs the database migrations to your latest model specifications, based on the previous command's migration files)

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

## Running the server

As a Django server, this API server is run like any other Django server:

- `python manage.py runserver`

## Testing the API using the "3rd party library" test file

Fire up a localhost server with port 8080 pointing at the `public` directory (some localhost servers like [http-server](https://npmjs.com/package/http-server) do this automatically for you) and point your browser to [http://localhost:8080](http://localhost:8080). If all went well (but read this README.md to the end, first) you should be able to post to the API server running "on" http://test.example.com:8000

## **Important**: using a localhost rebinding to a "real" domain

Google Auth does not like oauth2 to `localhost`, so you will need to set up a host binding such that 127.0.0.1 looks like a real domain. You can do this by editing your `hosts` file (in `/etc/hosts` on most unix-like systems, or `Windows\System32\Drivers\etc\hosts` in Windows). Add the following rule:

`127.0.0.1    test.example.com`

and then use `http://test.example.com:8000` instead of `http://localhost:8000` everywhere. Google Auth should now be perfectly happy.

### Why "test.example.com"?

Example.com and example.org are "special" domains in that they *cannot* resolve to a real domain as part of the policy we, as the internet-connected world, agreed on. This means that if you forget to set that `hosts` binding, visiting test.example.com will be a guaranteed failure. Any other domain may in fact exist, and you don't want to be hitting a real website when you're doing login and authentication.


## Deploying to Heroku

There is a Procfile in place for deploying to Heroku, but in order for the codebase to work you will need to specify the following environment variables for any Heroku instance:

 - `CLIENT_ID`: The client_id that Google gives you in the credentials console.
 - `CLIENT_SECRET`: The client_secret that Google gives you in the credentials console.
 - `REDIRECT_URIS`: This should match the redirect uri that you provided in the Google credentials console. For local testing this will be 'http://test.example.com:8000/oauth2callback' but for a Heroku instance you will need to replace `http://test.example.com:8000` with your Heroku url, and you'll have to make sure that your Google credentials use that same uri.
 - `AUTH_URI`: optional, defaults to 'https://accounts.google.com/o/oauth2/auth' and there is no reason to change it.
 - `TOKEN_URI`: optional, defaults to 'https://accounts.google.com/o/oauth2/token' and there is no reason to change it.
 
 Heroku provisions some environmnets on its own, like a `PORT` and `DATABASE_URL` variable, which this codebase will make use of if it sees them, but these values are only really relevant to Heroku deployments and not something you need to mess with for local development purposes.
