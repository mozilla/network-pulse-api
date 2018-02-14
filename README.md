[![Travis Build Status](https://travis-ci.org/mozilla/network-pulse-api.svg?branch=master)](https://travis-ci.org/mozilla/network-pulse-api) [![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/mozilla/network-pulse-api?svg=true)](https://ci.appveyor.com/project/mozillafoundation/network-pulse-api) [![Current API Version](https://img.shields.io/badge/dynamic/json.svg?label=Current%20API%20Version&colorB=blue&prefix=&suffix=&query=$.latestApiVersion&uri=https%3A%2F%2Fpulse--api.mofostaging.net%2Fapi%2Fpulse%2Fstatus%2F)]

# The Mozilla Foundation Network Pulse API Server

This is the REST API server for the Mozilla Network Pulse project.

All API routes are prefixed with `/api/pulse/`. The "pulse" might seem redundant, but this lets us move the API to different domains and fold it into other API servers without namespace conflicts in the future.

---

# API documentation

- [Versioning](#versioning)
- [General Routes](#general-routes)
- [Content-specific routes](#content-specific-routes)
	- [Creators](#creators)
	- [Entries](#entries)
	- [Help Types](#help-types)
	- [Issues](#issues)
	- [Profiles](#profiles)
	- [Tags](#tags)
- [Syndication](#syndication)

---

# Developer information

- [Getting up and running for local development](#getting-up-and-running-for-local-development)
- [Setting up your superuser](#setting-up-your-superuser)
- [Running the server](#running-the-server)
- [Environment variables](#environment-variables)
- [Deploying to Heroku](#deploying-to-heroku)
- [Debugging](#debugging-all-the-things)
- [Resetting your database](#resetting-your-database-because-of-incompatible-model-changes)
- [Migrating data from Google sheets](#migrating-data-from-google-sheets)

---

# Versioning

## How is the API versioned?

All Pulse API routes are versioned via their url path so that any future changes made to data responses will not break API clients that rely on specific versions of the data. To get a specific version of the API, add the version after the API prefix (`/api/pulse/`) in the url. For example, if you want version 2 (v2) of the API for the `entries` route, you would query the `/api/pulse/v2/entries/` url.

API routes that do not include the `/api/pulse/` prefix are also versioned in the same way. For example, `/v1/login/` is a valid versioned route without the prefix. Note however that the `/rss` and `/atom` routes are unversioned, as these are syndication endpoints.

## What happens if you don't specify an API version in the URL?

To maintain legacy support, if the version is not specified in the url, we default to version 1 (v1) of the API. For example, querying `/api/pulse/entries/` will have the same result as querying `/api/pulse/v1/entries/`. However, we strongly recommend specifying a version in the URL as this feature may be removed in the future.

## Supported API Versions

- Version 1 - `/api/pulse/v1/` and `/v1/`

---

# General Routes

All routes, including those with the `/api/pulse/` prefix should include a version in the URL (see the section on [Versioning](#versioning)) and although a URLs without the version are currently supported, versions will be made mandatory in the future.

## Login routes

### `GET /login?original_url=<url>`

This will kick off a Google OAuth2 login process. This process is entirely based on browser redirects, and once this process completes the user will be redirect to `original_url` with an additional url query argument `loggedin=True` or `loggedin=False` depending on whether the login attemp succeeded or not.

### `GET /logout`

This will log out a user if they have an authenticated session going. Note that this route does not have a redirect path associated with it: simply calling `/logout` with an XHR or Fetch operation is enough to immediately log the user out and invalidate their session at the API server. The only acknowledgement that callers will receive around this operation succeeding is that if an HTTP 200 status code is received, logout succeeded.

### `GET /oauth2callback`

This is the route that oauth2 login systems must point to in order to complete an oauth2 login process with in-browser callback URL redirection.

### `GET /api/pulse/userstatus/`

This gets the current user's session information in the form of their full name and email address.

The call response is a JSON object of the following form:

```
{
  username: <string: the user's full name according to Google>
  profileid: <string: the user's profile id>
  customname: <string: the user's custom name as set in their profile>
  email: <string: the user's google-login-associated email address>
  loggedin: <boolean: whether this user is logged in or not>
  moderator: <boolean: whether this logged-in user has moderation rights>
}
```

If a user is authenticated, all three fields will be present. If a user is not authenticated, the response object will only contain the `loggedin` key, with value `false`.

**This data should never be cached persistently**. Do not store this in localStorage, cookies, or any other persistent data store. When the user terminates their client, or logs out, this information should immediately be lost. Also do not store this in a global namespace like `window` or `document`, or in anything that isn't protected by a closure.

## POST protection

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

## Healthcheck

### `GET /status/`

This is a healthcheck route that can be used to check the status of the pulse API server. The response contains the following information:

```
{
  latestApiVersion: <version string>
}
```

# Content-specific routes

## Creators

### `GET /api/pulse/creators/?name=...`

Gets the list of all creators whose name starts with the string passed as `name` argument. This yields a response that uses the following schema:

```
{
    "count": 123,
    "next": "http://.../api/pulse/creators/?page=2&search=...",
    "previous": null,
    "results": [
        {
            "name": "...",
            "creator_id": number,
            "profile_id": number or false
        },
        ...
    ]
}
```


In this response:

- `count` property represents how many hits the system knows about,
- `next` is a URL if there are more results than fit in a single result set (set to `null` if there are no additional pages of results).
- `results` points to an array of creator records, where each creator has a `name` (string data), a `creator_id` (integer) as well as a `profile_id` (which is either an integer if the creator has an associated profile, or `false` if the creator does not have an associated profile). By default, this array will contain 6 objects, but this number can be increased (to a maximum of 20) by adding `&page_size=...` to the query with the desired results-per-page number.

## Entries

### `GET /api/pulse/entries/` with optional `?format=json`

This retrieves the full list of entries as stored in the database. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

This route takes a swathe of optional arguments for filtering the entry set, visit this route in the browser for more detailed information on all available query arguments.

#### Filters

Please run the server and see [http://localhost:8000/entries](http://localhost:8000/entries) for all supported filters.

### `GET /api/pulse/entries/<id=number>/` with optional `?format=json`

This retrieves a single entry with the indicated `id` as stored in the database. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.


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
  related_creators: optional array of objects where each object either has a creator_id or a name. The creator_id should be the id of an existing creator.
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

## Entry Moderation

### Moderation state

#### `GET /api/pulse/entries/moderation-states/` with optional `?format=json`

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

#### `PUT /api/pulse/entries/<id=number>/moderate/<id=number>` with optional `?format=json`

This changes the moderation state for an entry to the passed moderations state. Note that the moderation state is indicated by `id` number, **not** by moderation state name.

### Featured Entries

#### `PUT /api/pulse/entries/<id=number>/feature` with optional `?format=json`

This *toggles* the featured state for an entry if called by a user with moderation rights. An entry that was not featured will become featured, and already featured entries will become unfeatured when this route is called.


## Entry Bookmarking


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

## Help Types

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


## Issues

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

### `GET /api/pulse/issues/<Issue Name>`

Fetches the same data as above, but restricted to an individual issue queried for. Note that this is a URL query, not a URL argument query, so to see the data for an issue named "Security and Privacy" for example, the corresponding URL will be `/api/pulse/issues/Security and Privacy`.


## Profiles


### `GET /api/pulse/profiles/<id=number>/` with optional `?format=json`

This retrieves a single user profile with the indicated `id` as stored in the database. Any profile can be retrieved using this route even without being authenticated. The payload returned by this route also includes an array of entries published (`published_entries`) by the user owning this profile and an array of entries created (`created_entries`) by this profile (as defined by other users when creating entries). As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

### `GET /api/pulse/profiles/?...` with a filter arguments, and optional `format=json`

The list of profiles known to the system can be queried, but **only** in conjunction with one or more of three query arguments:

- `profile_type`: filter the list by profile types `board member`, `fellow`, `grantee`, `plain`, or `staff`.
- `program_type`: filter the list by program types `media fellow`, `open web fellow`, `science fellow`, `senior fellow`, or `tech policy fellow`.
- `program_year`: filter the list by program year in the range 2015-2019 (inclusive).


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

#### Updating extended profile information

If a user's profile has the `enable_extended_information` flag set to `True`, then there are additional fields that can be updated by this user:

```
{
  ...
  program_type: one of the above-listed program types
  program_year: one of the above-listed program years
  affiliation: the name of the primary organisation associated with the program the user is part of
  user_bio_long: a long-form text for the user biography information (4096 character limit)
}
```

## Tags

### `GET /api/pulse/tags/` with optional `?format=json`

This retrieves the list of all tags known to the system. When requesting JSON, this route yields an object of the form:

```
[
  "tag 1",
  "tag 2",
  "tag 3",
  ...
]
```

### Filtering

The above route can also be passed a `?search=...` query argument, which will filter the tag list based on `starts-with` logic, such that searching on `?search=abc` will find all tags that start with the partial string `abc`.

# Syndication

There are several syndication routes for RSS/Atom feeds available - these do not use the `/api/pulse` prefix and they are not versioned:

## RSS

### `GET /rss/latest`

Replies with an RSS feed consisting of (a subset of) the latest entries that were published to Mozilla Pulse.

### `GET /rss/featured`

Replies with an RSS feed consisting of (a subset of) only those entries that are currently considered featured content.

## Atom

### `GET /atom/latest`

Replies with an Atom feed consisting of (a subset of) the latest entries that were published to Mozilla Pulse.

### `GET /atom/featured`

Replies with an Atom feed consisting of (a subset of) only those entries that are currently considered featured content.



---

# Getting up and running for local development

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

### Testing the API using the "3rd party library" test file

Fire up a localhost server with port 8080 pointing at the `public` directory (some localhost servers like [http-server](https://npmjs.com/package/http-server) do this automatically for you) and point your browser to [http://localhost:8080](http://localhost:8080). If all went well (but read this README.md to the end, first) you should be able to post to the API server running "on" http://test.example.com:8000

### **Important**: using a localhost rebinding to a "real" domain

Google Auth does not like oauth2 to `localhost`, so you will need to set up a host binding such that 127.0.0.1 looks like a real domain. You can do this by editing your `hosts` file (in `/etc/hosts` on most unix-like systems, or `Windows\System32\Drivers\etc\hosts` in Windows). Add the following rule:

`127.0.0.1    test.example.com`

and then use `http://test.example.com:8000` instead of `http://localhost:8000` everywhere. Google Auth should now be perfectly happy.

#### Why "test.example.com"?

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
 - `PULSE_FRONTEND_HOSTNAME`: Defaults to `localhost:3000`. Used by the RSS and Atom feed views to create entry URLs that link to the network pulse frontend rather than the JSON API.


## Deploying to Heroku

While for local development we provide a `sample.env` that you can use as default environment variables, for Heroku deployment all the above-stated variables need to be real things. **Make sure to add these to the Heroku config!**

### Review App

Opening a PR will automatically create a Review App in the `network-pulse-api` pipeline. It's not possible to 
use OAuth but you can still access the admin with `test@mozillafoundation.org` as a user. To get the password, you need to go to the Heroku dashboard, click on the menu of your Review App and select `View initial app setup...`. The password is in the `Run scripts & scale dynos` log.


## Debugging all the things

You may have noticed that when running with `DEBUG=TRUE`, there is a debugger toolbar to the right of any page you try to access. This is the [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/stable/), and that link will take you straight to the documentation for it on how to get the most out of it while trying to figure out what's going on when problems arise.


## Resetting your database because of incompatible model changes

When working across multiple branches with multiple model changes, it sometimes becomes necessary to reset migrations and build a new database from scratch. You can either do this manually by deleting your `db.sqlite3` as well as all model migration files that start with a number (**except** for the 0001 migration for `issues`, which instantiates various records in addition to simply boostrapping the issues table, and should never be deleted), but because this is inconvenient, there is a helper script to do this for you.

Simply run `python reset_database.py` and the steps mentioned above will be run automatically.

**Note:** This does wipe *everything* so you will still need to call `python manage.py createsuperuser` afterwards to make sure you have a super user set up again.

## Migrating data from Google sheets

To migrate data, export JSON from the Google Sheets db, and save it in the root directory as `migrationData.json`. Then run `python migrate.py`. This generates `massagedData.json`.
In `public/migrate.html`, update the endpoint to be the address of the one you're trying to migrate data into. If it's a local db, leave as is.
Spin up a server from the `public` folder on port 8080. Log in to your API using Oauth (either the hosted site or `test.example.com:8000` if doing this locally)
Visit `http://test.example.com:8080/migrate.html`, paste the contents of `massagedData.json`, and submit. It will process the entire array of entries one at a time, POSTing them to the server. Check your developer console and network requests if it doesn't complete after a minute or two.
