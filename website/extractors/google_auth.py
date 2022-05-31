from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
#import json
#import os
#import pprint
#import google.oauth2.credentials
from googleapiclient.errors import HttpError
#from sklearn import get_config
#from . import config_keyvault as kv
#import config_sql
#import pandas as pd
#pp = pprint.PrettyPrinter(indent=2)


import hashlib
import os
import re
import socket
import sys


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
#CLIENT_SECRETS_FILE = "creds.json"

# This access scope grants read-only access to the authenticated user's Drive
# account.
#SCOPES = ['https://www.googleapis.com/auth/display-video']


API_SERVICE_NAME = 'displayvideo'
API_VERSION = 'v1'


def run_auth():

    #scopes = ['https://www.googleapis.com/auth/adwords']
    SCOPES = ['https://www.googleapis.com/auth/display-video']

    # client_config = {
    #    "installed": {
    #        "client_id": kv.get_secret_value("GADClientId"),
    #        "client_secret":  kv.get_secret_value("GADClientSecret"),
    #        "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"],
    #        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    #        "token_uri": "https://oauth2.googleapis.com/token"
    #    }
    # }

    # toto je config z nutraceutics appky
    client_config = {
        "web": {
            "client_id": "384533319422-5kbe301aebs7i9nf6js486r37onmqvh7.apps.googleusercontent.com",
            "project_id": "dv360test-335416",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "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",
            "redirect_uris": ["http://localhost:3000/"]
        }
    }

    # toto je config z nasej appky

    # client_config = {
    #    "installed": {
    #        "client_id": "483487325408-5mvkflj2q44vg6f47up2oeo424p4fr9h.apps.googleusercontent.com",
    # "project_id": "adglue",
    #        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    #        "token_uri": "https://oauth2.googleapis.com/token",
    #        "client_secret": "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",  # ,
    #        "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
    # "redirect_uris": ["http://localhost:3000/"]
    #    }
    # }

    # def get_authenticated_service():
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    credentials = flow.run_local_server(host='localhost',
                                        port=8090,
                                        authorization_prompt_message='Please visit this URL: {url}',
                                        success_message='The auth flow is complete; you may close this window.',
                                        open_browser=True)

    #credentials = flow.run_console()

    #flow = Flow.from_client_config(client_config, scopes=scopes)

    #flow.redirect_uri = "http://localhost:3000/"

    #passthrough_val = hashlib.sha256(os.urandom(1024)).hexdigest()

    # authorization_url, state = flow.authorization_url(
    #    access_type='offline',
    #    state=passthrough_val,
    #    include_granted_scopes='true',
    #    open_browser=True
    # )

    #code = _get_authorization_code(passthrough_val)

    # Pass the code back into the OAuth module to get a refresh token.
    # flow.fetch_token(code=code)
    #refresh_token = flow.credentials.refresh_token

    refresh_token = credentials._refresh_token
    print(refresh_token)
    return refresh_token


run_auth()


def run_auth_con():

    code = _get_authorization_code(passthrough_val)


def _get_authorization_code(passthrough_val):
    """Opens a socket to handle a single HTTP request containing auth tokens.
    Args:
        passthrough_val: an anti-forgery token used to verify the request
            received by the socket.
    Returns:
        a str access token from the Google Auth service.
    """
    # Open a socket at localhost:PORT and listen for a request
    sock = socket.socket()
    sock.bind(('localhost', 8090))
    sock.listen(1)
    connection, address = sock.accept()
    data = connection.recv(1024)
    # Parse the raw request to retrieve the URL query parameters.
    params = _parse_raw_query_params(data)

    try:
        if not params.get("code"):
            # If no code is present in the query params then there will be an
            # error message with more details.
            error = params.get("error")
            message = f"Failed to retrieve authorization code. Error: {error}"
            raise ValueError(message)
        elif params.get("state") != passthrough_val:
            message = "State token does not match the expected state."
            raise ValueError(message)
        else:
            message = "Authorization code was successfully retrieved."
    except ValueError as error:
        print(error)
        sys.exit(1)
    finally:
        response = (
            "HTTP/1.1 200 OK\n"
            "Content-Type: text/html\n\n"
            f"<b>{message}</b>"
            "<p>Please check the console output.</p>\n"
        )

        connection.sendall(response.encode())
        connection.close()

    return params.get("code")


def _parse_raw_query_params(data):
    """Parses a raw HTTP request to extract its query params as a dict.
    Note that this logic is likely irrelevant if you're building OAuth logic
    into a complete web application, where response parsing is handled by a
    framework.
    Args:
        data: raw request data as bytes.
    Returns:
        a dict of query parameter key value pairs.
    """
    # Decode the request into a utf-8 encoded string
    decoded = data.decode("utf-8")
    # Use a regular expression to extract the URL query parameters string
    match = re.search("GET\s\/\?(.*) ", decoded)
    params = match.group(1)
    # Split the parameters to isolate the key/value pairs
    pairs = [pair.split("=") for pair in params.split("&")]
    # Convert pairs to a dict to make it easy to access the values
    return {key: val for key, val in pairs}


'''
data = [['google_ads', None, None, refresh_token,
         'refresh_token', 'FcSPrV8UTy3Ed7fTug8KMg', 'campaign', 'nutraceutics_stage', 'googleads_campaign'],
        ['google_ads', None, None, refresh_token,
         'refresh_token', 'FcSPrV8UTy3Ed7fTug8KMg', 'ad_group_ad', 'nutraceutics_stage', 'googleads_adgroup_ad']]

df = pd.DataFrame(data, columns=['datasource', 'client_id', 'client_secret', 'authorization_token',
                                 'grant_type', 'developer_token', 'entity', 'sql_target_schema', 'sql_target_table'])

config = config_sql.get_config()
config.insert_new_customer(df)
'''
# run_auth()
# run_auth()
