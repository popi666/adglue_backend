import requests

import pandas as pd
import json
from datetime import datetime as dt
#import data_to_blob as blob

import sys
import os
# test pre ucet 240270927886966


access_token ='AQDIyOefYkfKYmMj403njs3ZeA0sDhMaxsP_RYWRlAGIgDxReaXper3xGQIDoKVmp7SQLNciy05WR_ygc5ZCRHgMnQ7KIDfpUeab8WcI4CM9XmUm_8HnS00BWX3TCrAW11we7q3fyauXcJNR7pR6nYch9ASQLNxPNkiL5ogItpgVHabrtD21eE7RVQoDCnsxQlwd6YUkmMmcG-9OycvbMVsbtvGo3XyMIvZczF9e-GgRPpAYH_VcxHd9zwTsoIUJfdJbYzk5-IwHHup-XTbG6p5hRvFnOEwGA2VLsAe0Kh_NPonCyj0Zub6CfnNDOtK4S0nfYferVbW-L7j8b51DTTPv7RbgzJ_ibtpOvyf4ThxxN7mKYe3bv4jQ__YH6rbQBeI'

'''url = "https://graph.facebook.com/v12.0/me/adaccounts" \
    "{insights" \
    "{campaign_name," \
    "date_start," \
    "date_stop}}," \
    "name,account_id" \
    "&access_token=" + access_token
'''
url = "https://graph.facebook.com/v12.0/me?fields=id,first_name,adaccounts" \
    "&access_token=" + access_token

payload = {}
headers = {}
response = requests.request("GET", url, headers=headers, data=payload)

response_json = response.json()
print(response_json)
