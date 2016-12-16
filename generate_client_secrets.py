'''
Generate a client_secrets.json based on environment variables.
This is a workaround for the Google oauth library not being able
to read in credentials *except* from JSON source... yay!
'''

import os
import json

client_secrets = {
  'web': {
    'client_id': os.getenv('client_id', 'PUT YOUR GOOGLE CLIENT_ID VALUE HERE'),
    'client_secret': os.getenv('client_secret', 'PUT YOUR GOOGLE CLIENT_SECRET VALUE HERE'),
    'redirect_uris': os.getenv('redirect_uris', 'http://localhost:8000/oauth2callback').split(','),
    'auth_uri': os.getenv('auth_uri', 'https://accounts.google.com/o/oauth2/auth'),
    'token_uri': os.getenv('token_uri', 'https://accounts.google.com/o/oauth2/token')
  }
}

data = json.dumps(client_secrets, sort_keys=True, indent=4, separators=(',', ': '))

text_file = open("client_secrets.json", "w")
text_file.write(data)
text_file.close()
