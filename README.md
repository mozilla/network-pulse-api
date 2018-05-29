[![Travis Build Status](https://travis-ci.org/mozilla/network-pulse-api.svg?branch=master)](https://travis-ci.org/mozilla/network-pulse-api) [![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/mozilla/network-pulse-api?svg=true)](https://ci.appveyor.com/project/mozillafoundation/network-pulse-api) [![Current API Version](https://img.shields.io/badge/dynamic/json.svg?label=Current%20API%20Version&colorB=blue&prefix=&suffix=&query=$.latestApiVersion&uri=https%3A%2F%2Fpulse-api.mofostaging.net%2Fapi%2Fpulse%2Fstatus%2F)](#supported-api-versions)

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
- [Pipenv and Invoke](#pipenv-and-invoke)
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

- Version 2 - `/api/pulse/v2/` and `/v2/`
- Version 1 - `/api/pulse/v1/` and `/v1/`

---

# General Routes

All routes, including those with the `/api/pulse/` prefix should include a version in the URL (see the section on [Versioning](#versioning)) and although a URLs without the version are currently supported, versions will be made mandatory in the future.

## Login routes

### `GET /login?original_url=<url>`

This will kick off a Google OAuth2 login process. This process is entirely based on browser redirects, and once this process completes the user will be redirect to `original_url` with an additional url query argument `loggedin=True` or `loggedin=False` depending on whether the login attemp succeeded or not.

### `GET /logout`

This will log out a user if they have an authenticated session going. Note that this route does not have a redirect path associated with it: calling `/logout` with an XHR or Fetch operation is enough to immediately log the user out and invalidate their session at the API server. The only acknowledgement that callers will receive around this operation succeeding is that if an HTTP 200 status code is received, logout succeeded.

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

#### DEPRECATION NOTICE

This route has been deprecated in favor of [`GET /api/pulse/profiles/?name=`](). Version 1 (v1) of this API route is supported for now.

#### Version 1 - `GET /api/pulse/v1/creators/?name=...`

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
- `results` points to an array of creator records, where each creator has a `name` (string data), a `creator_id` (integer which is the same as `profile_id`) as well as a `profile_id` (integer). By default, this array will contain 6 objects, but this number can be increased (to a maximum of 20) by adding `&page_size=...` to the query with the desired results-per-page number.

## Entries

### Entry object schema

```
  {
    id: <integer: id of the entry>,
    is_bookmarked: <boolean: whether this entry is bookmarked for the currently authenticated user>,
    tags: <array: list of tags as strings>,
    issues: <array: list of issues as strings>,
    help_types: <array: list of help categories as strings>,
    published_by: <string: name of the user who published this entry>,
    submitter_profile_id: <integer: id of the profile of the user who published this entry>,
    bookmark_count: <integer: number of users who have bookmarked this entry>,
    related_creators: <array: list of related creator objects (see below)>,
    title: <string: title of this entry>,
    content_url: <string: external url for the contents of the entry>,
    description: <string: description of the entry>,
    get_involved: <string: CTA text for this entry>,
    get_involved_url: <string: CTA url for this entry>,
    interest: <string: description of why this entry might be interesting>,
    featured: <boolean: whether this entry is featured on the pulse homepage or not>,
    published_by_creator: <boolean: does this entry mention the user who submitted it as a creator>,
    thumbnail: <string: url to a thumbnail image for the entry>,
    created: <timestamp: ISO 8601 timestamp of when this entry was created>,
    moderation_state: <integer: id of the moderation state of this entry>
  }
```

### Related creator object schema

The related creator object will differ based on the API version that is used.

#### Version 2 - `GET /api/pulse/v2/`

Each `related_creator` object will have the following schema:

```
{
  name: <string: name of the creator profile>
  profile_id: <integer: id of the creator profile>
}
```

#### Version 1 - `GET /api/pulse/v1/`

Each `related_creator` object should have the following schema:

```
{
  name: <string: name of the creator profile>
  profile_id: <integer: id of the creator profile>
  creator_id: <integer: same as the profile_id>
}
```

### `GET /api/pulse/entries/` with optional `?format=json`

This retrieves a paginated list of all [entries](#entry-object-schema) as stored in the database. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

The schema for the payload returned is:
```
{
    "count": <integer: number of entries>,
    "next": <string: url to the next page of entries> or null,
    "previous": <string: url to the previous page of entries> or null,
    "results": <array: list of entry objects (see above)>
}
```

#### Filters

- `?search=<string>` - Search for entries by their title, description, CTA, interest, creators, or tags
- `?ids=<comma-separated integers>` - Filter entries with specific ids
- `?tag=<string>` - Filter entries by a specific tag
- `?issue=<string>` - Filter entries by an issue area
- `?help_type=<string>` - Filter entries by a specific help category
- `?featured=<true or false>` - Filter featured or non-featured entries
- `?ordering=<string>` - Order entries by a certain property e.g. `?ordering=title`. Prepend the property with a hyphen to get entries in descending order, e.g. `?ordering=-title`
- `?moderationstate=<string>` - Filter entries by its moderation state. This filter will only be applied if the API call was made by an authenticated user with moderation permissions

### `GET /api/pulse/entries/<id=number>/` with optional `?format=json`

This retrieves a single [entry](#entry-object-schema) with the indicated `id` as stored in the database. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.


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
  related_creators: optional array of related creator objects (see below)where each object either has a creator_id or a name. The creator_id should be the id of an existing creator.
  published_by_creator: optional boolean to indicate that this user is (one of) the content creator(s)
}
```

---

__Related creator object schema__

The related creator object will differ based on the API version that is used.

#### Version 2 - `POST /api/pulse/v2/entries/`

Each `related_creator` object should have the following schema:

```
{
  name: optional string that represents a profile that does not exist yet
  profile_id: optional id of an existing profile
}
```

Either the `name` or the `profile_id` must be specified.

#### Version 1 - `POST /api/pulse/v1/entries/`

Each `related_creator` object should have the following schema:

```
{
  name: optional string that represents a creator that does not exist yet
  creator_id: optional id of an existing creator/profile
}
```

Either the `name` or the `creator_id` must be specified.

---

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

Get the list of all [entries](#entry-object-schema) that have been bookmarked by the currently authenticated user. Calling this as anonymous user yields an object with property `count` equals to `0`.  As a base URL call this returns an HTML page with formatted result, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

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

### Profile object schema

This represents a full profile object schema. Changes to the schema based on the API version are mentioned below the schema.

```
  {
    profile_id: <integer: id of the profile>,
    custom_name: <string: a custom name for this profile or empty string if not set>,
    name: <string: the custom name if set, otherwise the name of the user associated with this profile>,
    location: <string: location of the person this profile is associated to>,
    thumbnail: <string: url of the thumbnail for this profile>,
    issues: <array: list of issue areas related to this profile as strings>,
    twitter: <string: url to Twitter profile or empty string if not set>,
    linkedin: <string: url to LinkedIn profile or empty string if not set>,
    github: <string: url to Github profile or empty string if not set>,
    website: <string: url to personal website or empty string if not set>,
    user_bio: <string: biography of this profile>,
    profile_type: <string: type of profile>,
    my_profile: <boolean: whether this profile belongs to the currently authenticated user or not>,
    entry_count: <object: specifies the counts of entries related to this profile> -
                 {
                    created: <integer: count of entries created by this profile>,
                    published: <integer: count of entries published by this profile>,
                    favorited: <integer: count of entries bookmarked by this profile>
                 }
}
```

#### Version 2 - `/api/pulse/v2/profiles/*`

Returns a user profile object as specified by the schema exactly as shown above.

#### Version 1 - `/api/pulse/v1/profiles/*`

Returns a user profile object as specified by the schema above with two additional properties in the schema:

- `published_entries` - <array: list of [entries](#entry-object-schema) that were published by the user associated with this profile>
- `created_entries` - <array: list of [entries](#entry-object-schema) in which this profile was mentioned as a creator>

### `GET /api/pulse/profiles/<id=number>/` with optional `?format=json`

This retrieves a single [user profile object](#profile-object-schema) with the indicated `id` as stored in the database. Any profile can be retrieved using this route even without being authenticated. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

### `GET /api/pulse/profiles/<id=number>/entries/?...` with filter arguments, and optional `?format=json`

This retrieves a list of entries associated with a profile specified by `id`. The entries returned can be filtered based on any combination of the following query arguments:

- `?created=true`: Include a list of entries (with their `related_creators`) created by this profile.
- `?published=true`: Include a list of entries (with their `related_creators`) published by this profile.
- `?favorited=true`: Include a list of entries (with their `related_creators`) favorited/bookmarked by this profile.

__NOTE__: If none of the filters are specified, only the number of entries directly associated with the profile will be returned.

Based on the filter specified, the response payload will accordingly contain a `created`, `published`, and/or `favorited` property, each of whose value is a list of their corresponding entry objects.

The schema of the entry objects is specified below:

```
{
  id: <integer: id of the entry>,
  title: <string: title of the entry>,
  content_url: <string: external url for the contents of the entry>,
  thumbnail: <string: url to a thumbnail image for the entry>,
  is_bookmarked: <boolean: whether this entry is bookmarked for the currently authenticated user>,
  related_creators: <array: list of related creator objects (see below)>
}
```

Depending on the API version specified, the `related_creator` object schema will vary as mentioned [here](#related-creator-object-schema).

### `GET /api/pulse/profiles/?...` with filter arguments, and optional `format=json`

Returns a list of [user profile objects](#profile-object-schema). This route supports filtering based on properties of profiles and also supports searching for profiles based on `name`.

__NOTE__: At least one filter or search query from below must be specified, otherwise an empty array is returned in the payload.

#### Filters and Search Queries

- `?profile_type=...`: filter the list by profile types `board member`, `fellow`, `grantee`, `plain`, or `staff`.
- `?program_type=...`: filter the list by program types `media fellow`, `open web fellow`, `science fellow`, `senior fellow`, or `tech policy fellow`.
- `?program_year=...`: filter the list by program year in the range 2015-2019 (inclusive).
- `?is_active=<true or false>`: filter profiles by their active state.
- `?name=...`: search for profiles by their name. Supports partial and full search matches.

#### Other Supported Queries

- `?ordering=...` - You can sort these results using the `ordering` query param, passing it either `custom_name` or `program_year` (negated like `-custom_name` for descending order).
- `?basic=<true or false>` - This provides a way to only get basic information about profiles. Each profile object in the list will only contain the `id` of the profile and the `name` of the profile. This query can be useful for providing autocomplete options for profiles. __NOTE__ - This query is not compatible with version 1 of the API.

### `GET /api/pulse/myprofile/` with optional `?format=json`

This retrieves the **editable** [user profile](#profile-object-schema) for the currently authenticated user without the `name` and `my_profile` properties in the payload. An unauthenticated user will receive an HTTP 403 Forbidden response if they try to access this route. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

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

## Setup

**Requirements**: [python3.6 or later](https://www.python.org/), [pip](https://pypi.python.org/pypi), [pipenv](https://docs.pipenv.org/), [invoke](http://www.pyinvoke.org/installing.html).

1. Clone this repo: `git clone https://github.com/mozilla/network-pulse-api.git`,
2. Set up a Google client (https://console.developers.google.com/apis/credentials),
3. Run `inv setup`,
4. Open `client_secrets.json` and edit `client_id` and `client_secret` with your Google client's values.

**If you're on Windows:** you will need to Create a super user by running `pipenv run python manage.py createsuperuser`

`inv setup` takes care of installing the project's dependencies, copying environment variables, creating a superuser when possible and generating fake data. When it's done, do `inv runserver` to start your local server.

You can get a full list of inv commands by running `inv -l`.

## Generating fake data

Fake model data can be loaded into your dev site with the following command:

- `pipenv run python manage.py load_fake_data`

Two options are available:

- `--delete`: Delete bookmarks, creators, entries, profiles, tags and users from the database,
- `--seed`: A seed value to pass to Faker before generating data.
- `--fellows-count`: The number of fellows to generate per program type, per year. Defaults to 3

## Pipenv and Invoke

This project doesn't use a `requirements.txt` file, but `Pipfile` and `Pipfile.lock` files, managed by Pipenv. It also uses a set of Invoke tasks to provide shortcuts for commonly used commands.

### Using pipenv

Checking [Pipenv's documentation](https://docs.pipenv.org/) is highly recommended if you're new to it.

#### Running commands

The general syntax is:

- `pipenv run python [COMMAND]`. For example: `pipenv run python manage.py runserver`

#### Installing dependencies

- `pipenv install [package name]`

After installing a package, pipenv automatically runs a `pipenv lock` that updates the `pipfile.lock`. You need to add both `pipfile` and `pipfile.lock` to your commit.

#### Updating dependencies

- `pipenv check` to check security vulnerabilities,
- `pipenv update --outdated` to list dependencies that need to be updated,
- `pipenv update` to update dependencies

If a dependency is updated, pipenv automatically runs a `pipenv lock` that updates the `pipfile.lock`. You need to add both `pipfile` and `pipfile.lock` to your commit.

#### Listing installed dependencies

- `pipenv graph`

#### Virtual environment

- `pipenv shell` activates your virtual environment and automatically loads your `.env`. Run `exit` to leave it. **You don't need to be in your virtual environment to run python commands:** Use `pipenv run python [COMMAND]` instead.

#### Known issues

If you run `pipenv run python manage.py runserver` but get a `Cross-Origin Request Blocked` in the front, deactivate the auto-loading of the `.env`. ex: `PIPENV_DONT_LOAD_ENV=1 pipenv run ./manage.py runserver`

The reason behind this is that our CORS withelist regex is messed up by [a bug in python-dotenv](https://github.com/theskumar/python-dotenv/issues/112).

### Using invoke

Invoke is a task execution tool. Instead of running `pipenv run python manage.py runserver`, you can run `inv 
runserver`.

Available tasks:
- `inv -l`: list available invoke tasks
- `inv makemigrations`: Creates new migration(s) for apps
- `inv migrate`: Updates database schema
- `inv runserver`: Start a web server
- `inv setup`: Prepare your dev environment after a fresh git clone.
- `inv test`: Run tests and linter

For management commands not covered by an invoke tasks, use `inv manage [command]` (example: `inv manage load_fake_data`). You can pass flag and options to management commands using `inv manage [command] -o [positional argument] -f [optional argument]`. For example:
- `inv manage runserver -o 3000`
- `inv manage load_fake_data -f seed=VALUE`
- `inv manage migrate -o news`

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

Opening a PR will automatically create a Review App in the `network-pulse-api` pipeline. It's not possible to use OAuth but you can still access the admin with `test@mozillafoundation.org` as a user. To get the password, you need to go to the Heroku dashboard, click on the menu of your Review App and select `View initial app setup...`. The password is in the `Run scripts & scale dynos` log.


## Debugging all the things

You may have noticed that when running with `DEBUG=TRUE`, there is a debugger toolbar to the right of any page you try to access. This is the [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/stable/), and that link will take you straight to the documentation for it on how to get the most out of it while trying to figure out what's going on when problems arise.


## Resetting your database because of incompatible model changes

When working across multiple branches with multiple model changes, it sometimes becomes necessary to reset migrations and build a new database from scratch. You can either do this manually by deleting your `db.sqlite3` as well as all model migration files that start with a number (**except** for the 0001 migration for `issues`, which instantiates various records in addition to boostrapping the issues table, and should never be deleted), but because this is inconvenient, there is a helper script to do this for you.

run `pipenv run python reset_database.py` and the steps mentioned above will be run automatically.

**Note:** This does wipe *everything* so you will still need to call `pipenv run python manage.py createsuperuser` afterwards to make sure you have a super user set up again.

## Migrating data from Google sheets

To migrate data, export JSON from the Google Sheets db, and save it in the root directory as `migrationData.json`. Then run `pipenv run python migrate.py`. This generates `massagedData.json`.
In `public/migrate.html`, update the endpoint to be the address of the one you're trying to migrate data into. If it's a local db, leave as is.
Spin up a server from the `public` folder on port 8080. Log in to your API using Oauth (either the hosted site or `test.example.com:8000` if doing this locally)
Visit `http://test.example.com:8080/migrate.html`, paste the contents of `massagedData.json`, and submit. It will process the entire array of entries one at a time, POSTing them to the server. Check your developer console and network requests if it doesn't complete after a minute or two.
