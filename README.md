# The Mozilla Foundation Network Pulse API Server

This is the REST API server for the Mozilla Network Pulse project.

## Current API end points

### `GET /entries/` with optional `?format=json`

This retrieves the full list of entries as stored in the database. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

#### Filters

Please run the server and see [http://localhost:8000/entries](http://localhost:8000/entries) for all supported filters

#### Special filters

In addition to basic Django Rest Framework filtering, the following special filters are supported:

1. `?ids=1,2,3,...` -- retrieve a list of specific entries by specifying their id as comma-separated list.

### `GET /nonce/`

This gets a current user's session information in the form of their CSRF token, as well as a "nonce" value for performing a one-time post operation. Every time a user POSTs data to the /entry route, this nonce gets invalidated (whether it matches or not) to prevent repeat-posting. As such, is a user is to post several entries, they will need to call `/nonce` as many times.

The call response is a 403 for not authenticated users, or a JSON object when authenticated, of the form:

```
{
  csrf_token: <string: the user's session CSRF value>,
  nonce: <string: one-time-use value>
}
```

**This data should never be cached persistently**. Do not store this in localStorage, cookies, or any other persistent data store. When the user terminates their client, or logs out, this information should immediately be lost. Also do not store this in a global namespace like `window` or `document`, or in anything that isn't protected by a closure.

Also note that "the page itself" counts as global scope, so you generally don't want to put these values on the page as `<form>` elements. Instead, a form submission should be intercepted, and an in-memory form should be created with all the information of the original form, but with the nonce and csrf values copied. The submission can then use this in-memory form as basis for its POST payload instead.

### `GET /userstatus/`

This gets the current user's session information in the form of their full name and email address.

The call response is a JSON object of the following form:

```
{
  username: <string: the user's full name according to Google>,
  email: <string: the user's google-login-associated email address>
  loggedin: <boolean: whether this user is logged in or not>
}
```

If a user is authenticated, all three fields will be present. If a user is not authenticated, the response object will only contain the `loggedin` key, with value `false`.

**This data should never be cached persistently**. Do not store this in localStorage, cookies, or any other persistent data store. When the user terminates their client, or logs out, this information should immediately be lost. Also do not store this in a global namespace like `window` or `document`, or in anything that isn't protected by a closure.

### `POST /entries/`

POSTing of entries requires sending the following payload object:

```
{
  csrfmiddlewaretoken: '<csrf token>'
  nonce: '<nonce value obtained from [GET /nonce]>',
  data: {
    title: ...
    ...

  }
}
```

### `GET /entries/<id=number>/` with optional `?format=json`

This retrieves a single entry with the indicated `id` as stored in the database. As a base URL call this returns an HTML page with formatted result, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

### `PUT /entries/<id=number>/bookmark`

This toggles the "bookmarked" status for an entry for an authenticated user. No payload is expected, and no response is sent other than an HTTP 204 on success, HTTP 403 for not authenticated users, and HTTP 500 if something went terribly wrong on the server side.

### `GET /entries/bookmarks` with optional `?format=json`

Get the list of all entries that have been bookmarked by the currently authenticated user. Calling this as anonymous user yields an empty list.  As a base URL call this returns an HTML page with formatted result, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

### `GET /login?original_url=<url>`

This will kick off a Google OAuth2 login process. This process is entirely based on browser redirects, and once this process completes the user will be redirect to `original_url` with an additional url query argument `loggedin=True` or `loggedin=False` depending on whether the login attemp succeeded or not.

### `GET /logout`

This will log out a user if they have an authenticated session going. Note that this route does not have a redirect path associated with it: simply calling `/logout` with an XHR or Fetch operation is enough to immediately log the user out and invalidate their session at the API server. The only acknowledgement that callers will receive around this operation succeeding is that if an HTTP 200 status code is received, logout succeeded.

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


## Resetting your database because of incompatible model changes

When working across multiple branches with multiple model changes, it sometimes becomes necessary to reset migrations and build a new database from scratch. You can either do this manually by deleting your `db.sqlite3` as well as all model migration files that start with a number (**except** for the 0001 migration for `issues`, which instantiates various records in addition to simply boostrapping the issues table, and should never be deleted), but because this is inconvenient, there is a helper script to do this for you.

Simply run `python reset_database.py` and the steps mentioned above will be run automatically.

**Note:** This does wipe *everything* so you will still need to call `python manage.py createsuperuser` to make sure you have a super user set up again.

## Migrating data

To migrate data, export JSON from the Google Sheets db, and save it in the root directory as `migrationData.json`. Then run `python migrate.py`. This generates `massagedData.json`.
In `public/migrate.html`, update the endpoint to be the address of the one you're trying to migrate data into. If it's a local db, leave as is.
Spin up a server from the `public` folder on port 8080. Log in to your API using Oauth (either the hosted site or `test.example.com:8000` if doing this locally)
Visit `http://test.example.com:8080/migrate.html`, paste the contents of `massagedData.json`, and submit. It will process the entire array of entries one at a time, POSTing them to the server. Check your developer console and network requests if it doesn't complete after a minute or two.
