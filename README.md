[![Travis Build Status](https://travis-ci.org/mozilla/network-pulse-api.svg?branch=master)](https://travis-ci.org/mozilla/network-pulse-api) [![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/mozilla/network-pulse-api?svg=true)](https://ci.appveyor.com/project/mozillafoundation/network-pulse-api) [![Current API Version](https://img.shields.io/badge/dynamic/json.svg?label=Current%20API%20Version&colorB=blue&query=$.latestApiVersion&uri=https%3A%2F%2Fpulse-api.mofostaging.net%2Fapi%2Fpulse%2Fstatus%2F)](#supported-api-versions)

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
- [Local development documentation](#local-development)
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

- Version 3 - `/api/pulse/v3/` and `/v3/`
- Version 2 - `/api/pulse/v2/` and `/v2/`
- Version 1 - `/api/pulse/v1/` and `/v1/`

---

# General Routes

All routes, including those with the `/api/pulse/` prefix should include a version in the URL (see the section on [Versioning](#versioning)) and although a URLs without the version are currently supported, versions will be made mandatory in the future.

## Login routes

### `GET /login?original_url=<url>`

This will kick off a Google OAuth2 login process. This process is entirely based on browser redirects, and once this process completes the user will be redirect to `original_url` with an additional url query argument `loggedin=True` or `loggedin=False` depending on whether the login attempt succeeded or not.

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
  is_active: <boolean: flag indicating whether this creator profile is attached to a user>
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
- `?has_help_types=<True or False>` - Filter entries by whether they have help types or not. Note that `True` or `False` is case-sensitive.
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

The order of the entries returned for each filter can be specified using the corresponding ordering query argument. The value of the query argument should be the entry field (prefixed with `-` for descending order) to use for ordering. The supported ordering arguments are:
- `?created_ordering`: Specify the order of entries created by this profile.
- `?published_ordering`: Specify the order of entries published by this profile.
- `?favorited_ordering`: Specify the order of entries bookmarked/favorited by this profile.

For example, `?created&created_ordering=-id` will return the entries created by the profile reverse ordered by the entry `id`.

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

Returns a list (paginated for `v3` and above) of user profile objects each with the following schema:
```
{
  id: <integer: id of the profile>,
  name: <string: the custom name if set, otherwise the name of the user associated with this profile>,
  location: <string: location of the person this profile is associated to>,
  thumbnail: <string: url of the thumbnail for this profile>,
  user_bio: <string: biography of this profile>,
  profile_type: <integer: the id of the profile type associated with this profile>,
  is_active: <boolean: true if the profile has a user attached to it, false otherwise>,
  is_group: <boolean: whether this profile belongs to a group>,

  // The following properties will only be included if they are enabled
  // for the profile
  affiliation: <string: affiliations associated with this profile>,
  user_bio_long: <string: a longer biography for this profile>,
  program_type: <integer: the id of the program type this profile is associated with>,
  program_year: <integer: the id of the program year this profile belongs to>
}
```

The schema for the paginated payload returned for `v3` and above is:
```
{
    "count": <integer: total number of profiles found for this query>,
    "next": <string: url to the next page of profiles> or null,
    "previous": <string: url to the previous page of profiles> or null,
    "results": <array: list of profile objects (see above)>
}
```

__NOTE__: Versions below `v3` will not use the above schema and will follow the [general profile object schema](#profile-object-schema) instead.

This route supports filtering based on properties of profiles.

__NOTE__: At least one filter or search query from below must be specified, otherwise an empty array is returned in the payload.

#### Filters and Search Queries

- `?search=...`: search for profiles by their name, user bio, affiliation, or their location
- `?profile_type=...`: filter the list by profile types `board member`, `fellow`, `grantee`, `plain`, or `staff`.
- `?program_type=...`: filter the list by program types `media fellow`, `open web fellow`, `science fellow`, `senior fellow`, or `tech policy fellow`.
- `?program_year=...`: filter the list by program year in the range 2015-2019 (inclusive).
- `?is_active=<true or false>`: filter profiles by their active state.
- `?name=...`: filter profiles by their name. Supports partial and full matches.
- `?limit=...`: limit the number of results to some maximum.

#### Other Supported Queries

- `?ordering=...` - You can sort these results using the `ordering` query param, passing it either `id`, `custom_name`, or `program_year` (reversed by prefixing a `-`, e.g. `-custom_name` for descending alphabetical order based on the custom profile name).
- `?basic=<true or false>` - This provides a way to only get basic information about profiles. Each profile object in the list will only contain the `id` of the profile and the `name` of the profile. This query can be useful for providing autocomplete options for profiles. __NOTE__ - This query is not compatible with version 1 of the API.
- `?page_size=<number>` - Specify how many profiles will be in each page of the API call (only for `v3` and above)
- `?page=<number>` - Page number of the API call (`v3` and above)

### `GET /api/pulse/myprofile/` with optional `?format=json`

This retrieves the **editable** [user profile](#profile-object-schema) for the currently authenticated user without the `name` and `my_profile` properties in the payload. An unauthenticated user will receive an HTTP 403 Forbidden response if they try to access this route. As a base URL call this returns an HTML page with formatted results, as url with `?format=json` suffix this results a JSON object for use as data input to applications, webpages, etc.

### `PUT /api/pulse/myprofile/`

Allows an authenticated user to update their profile data. The payload that needs to be passed into this PUT request is:

```
{
	custom_name: <optional string: a custom name for this profile>,
	location: <optional string: location of the person this profile is associated to>,
	thumbnail: <optional object: a thumbnail object (see below) with the profile's image>,
	issues: <optional array: list of issue areas related to this profile as strings>,
	twitter: <optional string: url to Twitter profile>,
	linkedin: <optional string: url to LinkedIn profile>,
	github: <optional string: url to Github profile>,
	website: <optional string: url to personal website>,
	user_bio: <optional string: biography of this profile>
}
```

The thumbnail object should have the following schema:
```
{
  name: <string: name of the image file>,
  base64: <string: the base64 encoded binary representation of the image file's bytes>
}
```
The thumbnail object can also be `null` to set the thumbnail to `null` in the database (i.e. delete the image).

Also note that this PUT **must** be accompanied by the following header:

```
X-CSRFToken: required csrf token string obtained from [GET /nonce]
```

#### Updating extended profile information

If a user's profile has the `enable_extended_information` flag set to `True`, then there are additional fields that can be updated by this user:

```
{
  ...
  program_type: <string: the name of the program type this profile is associated with (must already exist)>,
  program_year: <string: the program year this profile belongs to (must already exist)>,
  affiliation: <string: affiliations associated with this profile>,
  user_bio_long: <string: a longer biography for this profile>
}
```

### `GET /api/pulse/profiles/categories`

This retrieves an object containing exhaustive lists of the profile types, program types, and program years available to use when filtering profiles

```
{
    profile_types: ["plain", "staff", "fellow", "board member", "grantee"],
    program_types: ["tech policy fellowship", "mozfest speaker"],
    program_years: ["2014", "2015", "2016", "2017", "2018"]
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

**Requirements**:
- python 3.7 (https://www.python.org/)
- invoke (with python installed, `pip install invoke` - if you are on legacy hardward or a legacy OS that still has python 2.7 installed, `pip3 install invoke`).
- PostgreSQL, consult the internet for how to install this for your Operating System.

- Run `inv setup`.
- Start your server with `inv runserver`.
- Your admin login is `admin@mozillafoundation.org` with password `admin`.
- (Optional) To enable Google and/or GitHub login, follow the [instructions below](#setting-up-social-authentication).

Update your branch by doing a git pull and `inv catchup`.
When switching branches, get a new virtualenv and database by running `inv new-env`.

You can get a full list of inv commands by running `inv -l`.

Instructions on how to setup this project using `nix-shell` (Linux and MacOS) are [available here](#nix-shell).

## Setting up Social Authentication

### Google

1. Set up a [Google OAuth client](https://console.developers.google.com/apis/credentials).
  - If you need to set up an oauth consent screen, click through and:
    - make sure it's set to "testing" (not "production") and
    - make sure it's set to "external" (not "internal")
  - Use `http://localhost:8000` as the "Authorized Javascript URL"
  - Use `http://localhost:8000/accounts/google/login/callback/` as the "Authorized Redirect URL"
  - Keep the client ID and client secret handy
2. Run the server with `inv runserver`
3. Go to http://localhost:8000/admin and log in using the superuser credentials [noted above](#requirements)
4. Add and save a new "Social Application" instance:
  - The "Provider" should be `Google`
  - The "Name" can be anything that will identify your Google social application
  - Fill in the client ID and client secret (leave "key" empty)
  - move `example.com` from the "Available sites" list to the "Chosen sites" list
5. Log out of the admin interface.

### GitHub

1. Log in to GitHub and setup a [GitHub OAuth client](https://github.com/settings/applications/new).
  - Use `http://localhost:8000` as the "Homepage URL"
  - Use `http://localhost:8000/accounts/github/login/callback/` as the "Authorized Callback URL"
  - Keep the client ID and client secret handy
2. Run the server with `inv runserver`.
3. Go to http://localhost:8000/admin and log in using the superuser credentials [noted above](#requirements)
4. Add and save a new "Social Application" instance:
  - The "Provider" should be `GitHub`
  - The "Name" can be anything that will identify your GitHub social application
  - Fill in the client ID and client secret
  - move `example.com` from the "Available sites" list to the "Chosen sites" list
5. Logout of the admin interface.

## Setting up Email

This app allows Django to send email to users for various purposes (e.g. email verification during social login). An email backend is required to make this possible and the email backend is determined based on the value of the `USE_CONSOLE_EMAIL` environment variable.

If it is set to `True` (or no value is provided), all emails will be sent to the terminal window in which Pulse API is running.

If it is set to `False`, you are required to use [Mailgun](https://www.mailgun.com/) as the email SMTP server and configure the `MAILGUN_SMTP_SERVER`, `MAILGUN_SMTP_PORT`, `MAILGUN_SMTP_LOGIN`, and `MAILGUN_SMTP_PASSWORD` environment variables.

## Generating fake data

Fake model data can be loaded into your dev site with the following command:

- `inv manage load_fake_data`

`inv manage "load_fake_data -e 30"` will run the full `load_fake_data` script, but changes the number of entries per variations to 30 instead of 20.

Options available:

- `--delete`: Delete bookmarks, creators, entries, profiles, tags and users from the database,
- `--seed`: A seed value to pass to Faker before generating data.
- `-f`, `--fellows-count`: The number of fellows to generate per program type, per year. Defaults to 3
- `-u`, `--users-count`: The number of users to generate per possible variations. Default: 1, variations: 80
- `-e`, `--entries-count`: The number of entries to generate per possible variations. Default: 20, variations: 16
- `-t`, `--tags-count`: The number of tags to generate. Default: 6

## Local development

### How to use

- Install [Invoke](http://www.pyinvoke.org/installing.html) using [pipx](https://pypi.org/project/pipx/).
- Run `inv setup`.
- Start your server with `inv runserver`.

Update your branch by doing a git pull and `inv catchup`.
When switching branches, get a new virtualenv and database by running `inv new-env`.

### Using invoke

Invoke is a task execution tool. Instead of running `./pulsevenv/bin/python manage.py runserver`, you can run `inv
runserver`.

Available tasks:
```
  catch-up (catchup)                           Install dependencies and apply migrations
  makemigrations                               Creates new migration(s) for apps
  manage                                       Shorthand to manage.py. inv docker-manage "[COMMAND] [ARG]"
  migrate                                      Updates database schema
  new-db                                       Create a new database with fake data
  pip-compile (docker-pip-compile)             Shorthand to pip-tools. inv pip-compile "[COMMAND] [ARG]"
  pip-compile-lock (docker-pip-compile-lock)   Lock prod and dev dependencies
  pip-sync (docker-pip-sync)                   Sync your python virtualenv
  runserver                                    Start a web server
  setup (new-env)                              Automate project's configuration and dependencies installation
  test                                         Run tests
```

### How to install or update dependencies?

**Note on [pip-tools](https://github.com/jazzband/pip-tools)**:
- Only edit the `.in` files and use `invoke pip-compile-lock` to generate `.txt` files.
- Both `(dev-)requirements.txt` and `(dev-)requirements.in` files need to be pushed to Github.
- `.txt` files act as lockfiles, where dependencies are pinned to a precise version.

Dependencies live on your filesystem: you don't need to rebuild the `backend` image when installing or updating dependencies.

**Install packages:**

- Modify the `requirements.in` or `dev-requirements.in` to add the dependency you want to install.
- Run `invoke pip-compile-lock`.
- Run `invoke pip-sync`.

**Update packages:**

- `invoke pip-compile "-upgrade (dev-)requirements.in"`: update all (the dev) dependencies.
- `invoke pip-compile "--upgrade-package [PACKAGE](==x.x.x)"`: update the specified dependency. To update multiple dependencies, you always need to add the `-P` flag.

When it's done, run `inv pip-sync`.

### Nix-shell

If you want to use nix-shell to isolate your dev environment:

- Install [Nix](https://nixos.org/nix/): `curl https://nixos.org/nix/install | sh`,
- In `network-pulse-api` directory, enter `nix-shell`. It will install Python 3.7 and invoke.
- Enter `inv setup` to setup the project.
- When it's done, use invoke commands as usual.

If you want to use another shell instead of bash, use `nix-shell --command SHELL` (`nix-shell --command zsh` for example).

#### Direnv
[Direnv](https://direnv.net/) will load your `nix-shell` automatically when you enter the `network-pulse-api` directory.

To use it:
- Follow the instruction to [install direnv](https://direnv.net/) on your system.
- Allow direnv to auto-load your nix-shell by entering `direnv allow .` in the `network-pulse-api` directory.


### Testing the API using the "3rd party library" test file

Fire up a localhost server with port 8080 pointing at the `public` directory (some localhost servers like [http-server](https://npmjs.com/package/http-server) do this automatically for you) and point your browser to [http://localhost:8080](http://localhost:8080). If all went well (but read this README.md to the end, first) you should be able to post to the API server running "on" http://localhost:8000


## Environment variables

Heroku provisions some environments on its own, like a `PORT` and `DATABASE_URL` variable, which this codebase will make use of if it sees them, but these values are only really relevant to Heroku deployments and not something you need to mess with for local development purposes.

Configure the following environment variables as needed in your `.env` file. All variables are optional, but some are highly recommended to be set explicitly.

### Authentication variables

- `ALLOW_SIGNUP` &mdash; Determines whether signing up for a new account is permitted. **Defaults to `True`.**
- `LOGIN_ALLOWED_REDIRECT_DOMAINS` &mdash; A comma-separated list of domains that are allowed to be redirected to after logging in a user. **Defaults to  `localhost:3000`.**
- `AUTH_STAFF_EMAIL_DOMAINS` &mdash; A comma-separated list of email domains that should be considered "safe" to make as "staff" in Django. **Defaults to `mozillafoundation.org`.**
- `AUTH_REQUIRE_EMAIL_VERIFICATION` &mdash; A boolean indicating whether a user needs to verify their email attached to a social account (e.g. Github) before being able to login. **Defaults to `False`.**
- `AUTH_EMAIL_REDIRECT_URL` &mdash; The url to redirect to after a user verifies their email to login successfully. **Defaults to `/`.**
- `PULSE_CONTACT_URL` &mdash; A contact url for users to file questions or problems when authenticating. **Defaults to an empty string.**
- `USE_RECAPTCHA` &mdash; Determines whether the login route is locked behind Google reCAPTCHA or not. **Defaults to `True`**.
- `RECAPTCHA_SECRET` &mdash; The Google reCAPTCHA secret value. **Defaults to an empty string.**

### Email variables

- `USE_CONSOLE_EMAIL` &mdash; A boolean to indicate whether the terminal should be used to display emails sent from Django, instead of an email backend. Useful for local development. **Defaults to `True`.**
- `EMAIL_VERIFICATION_FROM` &mdash; The email address used in the "From:" section of emails sent by Django. **Defaults to `webmaster@localhost`.**

These variables are only used (and are required) if `USE_CONSOLE_EMAIL` is set to `False`.

- `MAILGUN_SMTP_SERVER` &mdash; The url for the Mailgun SMTP server that will be used to send emails.
- `MAILGUN_SMTP_PORT` &mdash; The port (as a number) to connect to the Mailgun server.
- `MAILGUN_SMTP_LOGIN` &mdash; The login user credential to use to authenticate with the Mailgun server.
- `MAILGUN_SMTP_PASSWORD` &mdash; The password to authenticate with the Mailgun server.

### Data storage variables

- `DATABASE_URL` &mdash; The url to connect to the database. **Defaults to `False` which forces Django to create a local SQLite database file.**
- `USE_S3` &mdash; A boolean to indicate whether to store user generated assets (like images) on Amazon S3. **Defaults to `False`.**

These variables are only used (and are required) if `USE_S3` is set to `True`.

- `AWS_ACCESS_KEY_ID` &mdash; Amazon user Access Key for authentication.
- `AWS_SECRET_ACCESS_KEY` &mdash; Amazon user Secret Key for authentication.
- `AWS_STORAGE_BUCKET_NAME` &mdash; S3 bucket name where the assets will be stored.
- `AWS_STORAGE_ROOT` &mdash; S3 root path in the bucket where assets will be stored.
- `AWS_S3_CUSTOM_DOMAIN` &mdash; A custom domain (for e.g. Amazon CloudFront) used to access assets in the S3 bucket.

### Security variables

- `DEBUG` *(recommended)* &mdash; A boolean that indicates whether Django should run in debug mode. DO NOT SET THIS TO `True` IN PRODUCTION ENVIRONMENTS SINCE YOU RISK EXPOSING PRIVATE DATA SUCH AS CREDENTIALS. **Defaults to `True`.**
- `SECRET_KEY` *(recommended)* &mdash; A unique, unpredictable string that will be used for cryptographic signing. PLEASE GENERATE A NEW SECRET STRING FOR PRODUCTION ENVIRONMENTS. **Defaults to a set string of characters.**
- `SSL_PROTECTION` *(recommended)* &mdash; A catch-all boolean that indicates whether SSL encryption, XSS filtering, content-type sniff protection, HSTS, and cookie security should be enabled. THIS SHOULD LIKELY BE SET TO `True` IN A PRODUCTION ENVIRONMENT. **Defaults to `False`.**
- `ALLOWED_HOSTS` &mdash; A comma-separated list of host domains that this app can serve. This is meant to prevent HTTP Host header attacks. **Defaults to a list of `localhost`, `localhost`, `network-pulse-api-staging.herokuapp.com`, and `network-pulse-api-production.herokuapp.com`.**
- `CORS_ORIGIN_REGEX_WHITELIST` *(recommended)* &mdash; A comma-separated list of python regular expressions matching domains that should be enabled for CORS. **Defaults to anything running on `localhost` or on `localhost`.**
- `CORS_ORIGIN_WHITELIST` &mdash; A comma-separated list of domains that should be allowed to make CORS requests. **Defaults to an empty list.**
- `CSRF_TRUSTED_ORIGINS` &mdash; A comma-separated list of trusted domains that can send POST, PUT, and DELETE requests to this API. **Defaults to a list of `localhost:3000`, `localhost:8000`, `localhost:8080` , `localhost:8000`, and `localhost:3000`.**

### Front-end variables

- `PULSE_FRONTEND_HOSTNAME` &mdash; The hostname for the front-end used for Pulse. This is used for the RSS and Atom feed data. **Defaults to `localhost:3000`.**

### Review Apps bot variables

- `GITHUB_TOKEN` &mdash; Used to get the PR title.
- `SLACK_WEBHOOK_RA` &mdash; Incoming webhook of the `HerokuReviewAppBot` Slack app.

### Miscellaneous variables

- `HEROKU_APP_NAME` &mdash; A domain used to indicate if this app is running as a review app on Heroku. This is used to determine if social authentication is available or not (since it isn't for review apps). **Defaults to an empty string.**

## Deploying to Heroku

While for local development we provide a `sample.env` that you can use as default environment variables, for Heroku deployment all the above-stated variables need to be real things. **Make sure to add these to the Heroku config!**

### Review App

#### Review App for PRs

Opening a PR will automatically create a Review App in the `network-pulse-api` pipeline. A slack bot posts credentials and links to Review Apps in to the `mofo-ra-pulse-api` Slack channel.

*Note:* This only work for Mo-Fo staff: you will need to manually open a Review App on Heroku for PRs opened by external contributors.

#### Review App for branches

You can manually create a review app for any branch pushed to this repo. It's useful if you want to test your code on Heroku without opening a PR yet.

To create one:
- log into Heroku.
- Go to the `network-pulse-api` pipeline.
- Click on `+ New app` and select the branch you want to use.

The review app slack bot will post a message in the `mofo-ra-pulse-api` channel with links and credentials as soon as the review app is ready.

#### Environment variables:

- `GITHUB_TOKEN`: GITHUB API authentication,
- `SLACK_WEBHOOK_RA`: Webhook to `mofo-ra-pulse-api`

Non-secret envs can be added to the `app.json` file. Secrets must be set on Heroku in the `Review Apps` (pipelines' `settings` tab).

## Debugging all the things

You may have noticed that when running with `DEBUG=TRUE`, there is a debugger toolbar to the right of any page you try to access. This is the [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/stable/), and that link will take you straight to the documentation for it on how to get the most out of it while trying to figure out what's going on when problems arise.


## Resetting your database because of incompatible model changes

When working across multiple branches with multiple model changes, it sometimes becomes necessary to reset migrations and build a new database from scratch. You can either do this manually by deleting your `db.sqlite3` as well as all model migration files that start with a number (**except** for the 0001 migration for `issues`, which instantiates various records in addition to boostrapping the issues table, and should never be deleted), but because this is inconvenient, there is a helper script to do this for you.

run `pulsevenv/bin/python reset_database.py` and the steps mentioned above will be run automatically.

**Note:** This does wipe *everything* so you will still need to call `pulsevenv/bin/python manage.py createsuperuser` afterwards to make sure you have a super user set up again.

## Migrating data from Google sheets

To migrate data, export JSON from the Google Sheets db, and save it in the root directory as `migrationData.json`. Then run `pulsevenv/bin/python migrate.py`. This generates `massagedData.json`.
In `public/migrate.html`, update the endpoint to be the address of the one you're trying to migrate data into. If it's a local db, leave as is.
Spin up a server from the `public` folder on port 8080. Log in to your API using Oauth (either the hosted site or `localhost:8000` if doing this locally)
Visit `http://localhost:8080/migrate.html`, paste the contents of `massagedData.json`, and submit. It will process the entire array of entries one at a time, POSTing them to the server. Check your developer console and network requests if it doesn't complete after a minute or two.
