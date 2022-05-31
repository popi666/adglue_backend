#import data_to_blob as blob
#import data_to_sql as sql
import configurator as conf

import requests
import json
from datetime import datetime as dt
import pandas as pd
#import logginglogger as logger
import sys
import os
import config_keyvault as kv

from config_sql import get_config


def get_oauth_token(config):
    client_id = kv.get_secret_value("GADClientId")
    client_secret = kv.get_secret_value("GADClientSecret")
    refresh_token = kv.get_secret_value("GADAuthToken")
    grant_type = config.get_parameter(
        'google_ads', 'ad_group_ad', 'grant_type')

    url = "https://www.googleapis.com/oauth2/v3/token?client_id={}&client_secret={}&refresh_token={}&grant_type={}&login_customer_id=7203692411".format(
        client_id, client_secret, refresh_token, grant_type)

    payload = {}
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload)

    bearer_token = response.json()["token_type"] + \
        " " + response.json()["access_token"]

    return bearer_token

# Slouží pro vygenerování CustomerId, které je součástí config.json


def create_customer(config):
    url = "https://googleads.googleapis.com//v9/customers/7203692411:createCustomerClient"

    payload = {}
    headers = {
        'Authorization': get_oauth_token(config),
        'developer-token': kv.get_secret_value("GADDevToken"),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.json())


def send_invitation_customer(config):
    url = "https://googleads.googleapis.com/v9/customers/7203692411/customerUserAccessInvitations:mutate"

    payload = {}
    headers = {
        'Authorization': get_oauth_token(config),
        'developer-token': kv.get_secret_value("GADDevToken"),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.json())


send_invitation_customer(get_config())
