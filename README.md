[![Travis Build Status](https://travis-ci.org/mozilla/network-pulse-api.svg?branch=master)](https://travis-ci.org/mozilla/network-pulse-api) [![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/mozilla/network-pulse-api?svg=true)](https://ci.appveyor.com/project/mozillafoundation/network-pulse-api)

# The Mozilla Foundation Network Pulse API Server

This is the REST API server for the Mozilla Network Pulse project.

- [Current API end points](#current-api-end-points)
- [Getting up and running for local development](#getting-up-and-running-for-local-development)
- [Setting up your superuser](#setting-up-your-superuser)
- [Using a localhost rebinding to a "real" domain](#important-using-a-localhost-rebinding-to-a-real-domain)
- [Environment variables](#environment-variables)
- [Deploying to Heroku](#deploying-to-heroku)
- [Migrating data](#migrating-data)

## Resetting your database because of incompatible model changes

## Current API end points

All API routes are prefixed with `/api/pulse/`. The "pulse" might seem redundant, but this lets us move the API to different domains and fold it into other API servers without namespace conflicts.

### `GET /api/pulse/entries/` with optional `?format=json`

This retrieves the full list of entries as stored in the database. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

This route takes a swathe of optional arguments for filtering the entry set, visit this route in the browser for more detailed information on all available query arguments.

#### Filters

Please run the server and see [http://localhost:8000/entries](http://localhost:8000/entries) for all supported filters.

### `GET /api/pulse/nonce/`

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

### `GET /api/pulse/userstatus/`

This gets the current user's session information in the form of their full name and email address.

The call response is a JSON object of the following form:

```
{
  username: <string: the user's full name according to Google>,
  email: <string: the user's google-login-associated email address>
  loggedin: <boolean: whether this user is logged in or not>
  moderator: <boolean: whether this logged-in user has moderation rights>
}
```

If a user is authenticated, all three fields will be present. If a user is not authenticated, the response object will only contain the `loggedin` key, with value `false`.

**This data should never be cached persistently**. Do not store this in localStorage, cookies, or any other persistent data store. When the user terminates their client, or logs out, this information should immediately be lost. Also do not store this in a global namespace like `window` or `document`, or in anything that isn't protected by a closure.

### `GET /api/pulse/issues/`

Gets the list of internet health issues that entries can be related to. This route yields a documentation page unless the request mimetype is set to `application/json`, or the `?format=json` query argument is passed. When requesting JSON, this route yields an object of the form:

```
[{
  name: "issue name",
  description: "issue description"
},{
  name: ...
  description: ...
},
...]
```

### `GET /api/pulse/helptypes/`

Gets the list of help types that are used by entries to indicate how people can get involved. This route yields a documentation page unless the request mimetype is set to `application/json`, or the `?format=json` query argument is passed. When requesting JSON, this route yields an object of the form:

```
[{
  name: "help type name",
  description: "help type description"
},{
  name: ...
  description: ...
},
...]
```

### `POST /api/pulse/entries/`

POSTing of entries requires sending the following payload object:

```
{
  csrfmiddlewaretoken: required csrf token string obtained from [GET /nonce]
  nonce: required nonce string obtained from [GET /nonce]

  title: required string (max length 140 characters)
  content_url: required url string

  description: optional string (max length 600 characters)
  get_involved: optional 'how to get involved' string (max length 300 characters)
  get_involved_url: optional URL that people can visit to get involved
  interest: optional subject string (Free form, max length 600 characters)
  featured: optional boolean to set the "shown on featured page" flag

  thumbnail: optional object {
    name: name of the file,
    base64: the base64 encoded binary representation of the file's bytes
  }

  tags: optional array of strings
  issue: optional string, must match value from [GET /issues?format=json]
  help_type: optional string, must match value from [GET /helptypes?format=json]
  creators: optional array of names of creators for the content linked to
  published_by_creator: optional boolean to indicate that this user is (one of) the content creator(s)
}
```
Also note that this POST **must** be accompanied by the following header:

```
X-CSRFToken: csrfmiddlewaretoken as used above
```

A successful post will yield a JSON object:

```
{
  status: "submitted"
}
```

A failed post will yield an HTTP 400 response.

### `POST /api/pulse/entries/bookmarks/ids=<a comma-separated list of integer ids>`

POSTing to bookmark a list of entries requires sending the following payload object:

```
{
  csrfmiddlewaretoken: required csrf token string obtained from [GET /nonce]
  nonce: required nonce string obtained from [GET /nonce]
}
```
Also note that this POST **must** be accompanied by the following header:

```
X-CSRFToken: csrfmiddlewaretoken as used above
```

A successful post will yield a JSON object:

```
{
  status: "Entries bookmarked."
}
```

A failed post will yield
 - an HTTP 400 response if any entry id passed is invalid
 - an HTTP 403 response if the current user is not authenticated

### `GET /api/pulse/entries/moderation-states/` with optional `?format=json`

This retrieves the list of moderation states that are used for entry moderation. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

The result is of the format:
```
[
{
  id: "id number as string",
  name: "human-readable name for this moderation state"
},
{...},
...
]
```

### `GET /api/pulse/entries/<id=number>/` with optional `?format=json`

This retrieves a single entry with the indicated `id` as stored in the database. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

### `PUT /api/pulse/entries/<id=number>/moderate/<id=number>` with optional `?format=json`

This changes the moderation state for an entry to the passed moderations state. Note that the moderation state is indicated by `id` number, **not** by moderation state name.

### `PUT /api/pulse/entries/<id=number>/bookmark`

This toggles the "bookmarked" status for an entry for an authenticated user. No payload is expected, and no response is sent other than an HTTP 204 on success, HTTP 403 for not authenticated users, and HTTP 500 if something went terribly wrong on the server side.

This operation requires a payload of the following form:
```
{
  csrfmiddlewaretoken: required csrf token string obtained from [GET /nonce]
  nonce: required nonce string obtained from [GET /nonce]
}
```

### `GET /api/pulse/entries/bookmarks` with optional `?format=json`

Get the list of all entries that have been bookmarked by the currently authenticated user. Calling this as anonymous user yields an object with property `count` equals to `0`.  As a base URL call this returns an HTML page with formatted result, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

### `GET /api/pulse/profiles/<id=number>/` with optional `?format=json`

This retrieves a single user profile with the indicated `id` as stored in the database. Any profile can be retrieved using this route even without being authenticated. The payload returned by this route also includes an array of entries published (`published_entries`) by the user owning this profile. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

### `GET /api/pulse/myprofile/` with optional `?format=json`

This retrieves the **editable** user profile for the currently authenticated user as stored in the database. An unauthenticated user will receive an HTTP 403 Forbidden response if they try to access this route. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

### `PUT /api/pulse/myprofile/`

Allows an authenticated user to update their profile data. The payload that needs to be passed into this PUT request is:

```
{
  user_bio: optional string (max length 140 characters)
  custom_name: optional string containing the user's alternative name (max length 70 characters)
  thumbnail: optional object {
    name: name of the file,
    base64: the base64 encoded binary representation of the file's bytes
  }, if you pass in null, the thumbnail will be set to null
  twitter: optional url link to twitter account
  linkedin: optional url link to linkedin account
  github: optional url link to github account
  website: optional url link to the user's website
}
```

Also note that this PUT **must** be accompanied by the following header:

```
X-CSRFToken: required csrf token string obtained from [GET /nonce]
```

### `GET /api/pulse/login?original_url=<url>`

This will kick off a Google OAuth2 login process. This process is entirely based on browser redirects, and once this process completes the user will be redirect to `original_url` with an additional url query argument `loggedin=True` or `loggedin=False` depending on whether the login attemp succeeded or not.

### `GET /logout`

This will log out a user if they have an authenticated session going. Note that this route does not have a redirect path associated with it: simply calling `/logout` with an XHR or Fetch operation is enough to immediately log the user out and invalidate their session at the API server. The only acknowledgement that callers will receive around this operation succeeding is that if an HTTP 200 status code is received, logout succeeded.

## Getting up and running for local development

You'll need `python` (v3) with `pip` (latest) and optionally `virtualenv` (python3 comes with a way to build virtual environments, but you can also install `virtualenv` as a dedicated library if you prefer)

1. clone this repo
2. `cp sample.env .env` to turn on debug mode via environment variables.
3. set up a virtual environment in the `network-pulse-api` directory
4. run `pip install -r requirements.txt`
5. set up a Google client (https://console.developers.google.com/apis/credentials)
6. generate a `client_secrets.json` by running `> python generate_client_secrets.py`, then edit this file so that it has your client's `client_id` and `client_secret`, with `http://test.example.com:8000/api/pulse/oauth2callback` as your callback URI (double check that's what it's set to. It should be, but it's super important you check this).
7. bootstrap the Django setup:

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


## Environment variables

The following environment variables are used in this codebase

 - `CLIENT_ID`: The client_id that Google gives you in the credentials console.
 - `CLIENT_SECRET`: The client_secret that Google gives you in the credentials console.
 - `REDIRECT_URIS`: This should match the redirect uri that you provided in the Google credentials console. For local testing this will be 'http://test.example.com:8000/api/pulse/oauth2callback' but for a Heroku instance you will need to replace `http://test.example.com:8000` with your Heroku url, and you'll have to make sure that your Google credentials use that same uri.
 - `AUTH_URI`: optional, defaults to 'https://accounts.google.com/o/oauth2/auth' and there is no reason to change it.
 - `TOKEN_URI`: optional, defaults to 'https://accounts.google.com/o/oauth2/token' and there is no reason to change it.
 - `SSL_PROTECTION`: Defaults to `False` to make development easier, but if you're deploying you probably want this to be `True`. This sets a slew of security-related variables in `settings.py` that you can override individually if desired.
 Heroku provisions some environmnets on its own, like a `PORT` and `DATABASE_URL` variable, which this codebase will make use of if it sees them, but these values are only really relevant to Heroku deployments and not something you need to mess with for local development purposes.


## Deploying to Heroku

While for local development we provide a `sample.env` that you can use as default environment variables, for Heroku deployment all the above-stated variables need to be real things. **Make sure to add these to the Heroku config!**


## Resetting your database because of incompatible model changes

When working across multiple branches with multiple model changes, it sometimes becomes necessary to reset migrations and build a new database from scratch. You can either do this manually by deleting your `db.sqlite3` as well as all model migration files that start with a number (**except** for the 0001 migration for `issues`, which instantiates various records in addition to simply boostrapping the issues table, and should never be deleted), but because this is inconvenient, there is a helper script to do this for you.

Simply run `python reset_database.py` and the steps mentioned above will be run automatically.

**Note:** This does wipe *everything* so you will still need to call `python manage.py createsuperuser` to make sure you have a super user set up again.

## Migrating data

To migrate data, export JSON from the Google Sheets db, and save it in the root directory as `migrationData.json`. Then run `python migrate.py`. This generates `massagedData.json`.
In `public/migrate.html`, update the endpoint to be the address of the one you're trying to migrate data into. If it's a local db, leave as is.
Spin up a server from the `public` folder on port 8080. Log in to your API using Oauth (either the hosted site or `test.example.com:8000` if doing this locally)
Visit `http://test.example.com:8080/migrate.html`, paste the contents of `massagedData.json`, and submit. It will process the entire array of entries one at a time, POSTing them to the server. Check your developer console and network requests if it doesn't complete after a minute or two.
