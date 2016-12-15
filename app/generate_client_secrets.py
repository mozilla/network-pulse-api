'''
Generate a client_secrets.json based on environment variables.
This is a workaround for the Google oauth library not being able
to read in credentials *except* from JSON source... yay!
'''

import os
import json

client_secrets = {
  'web': {
    'client_id': os.getenv('client_id', 'no id set'),
    'client_secret': os.getenv('client_secret', 'no secret set'),
    'redirect_uris': os.getenv('redirect_uris', 'http://localhost:0').split(','),
    'auth_uri': os.getenv('auth_uri', 'http://localhost:0'),
    'token_uri': os.getenv('token_uri', 'http://localhost:0')
  }
}

data = json.dumps(client_secrets)

text_file = open("client_secrets.json", "w")
text_file.write(data)
text_file.close()
