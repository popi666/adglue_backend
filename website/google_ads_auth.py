from flask import Blueprint, request, session
from .models import User, Customer, User_datasources_tokens, User_datasources, Serializer
from . import db
import json
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, unset_jwt_cookies, jwt_required, JWTManager
from google_auth_oauthlib.flow import Flow
import requests
import hashlib
import os
import pandas as pd

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
google_ads_auth = Blueprint('google_ads_auth', __name__)


@google_ads_auth.route('/gad', methods=['GET'])
@jwt_required()
def gad():
    # if request.method == 'GET':
    #response = {"message": "success"}
    user = get_jwt_identity()
    #auth_url = run_auth()
    #response = {"url": auth_url}
    # main(user)
    scopes = ['https://www.googleapis.com/auth/adwords']

    client_config = {
        "web": {
            "client_id": "384533319422-5kbe301aebs7i9nf6js486r37onmqvh7.apps.googleusercontent.com",
            "project_id": "dv360test-335416",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "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",
            "redirect_uris": ["http://localhost:3000/datasources"]
        }
    }
    passthrough_val = hashlib.sha256(os.urandom(1024)).hexdigest()

    flow = Flow.from_client_config(
        client_config, scopes=scopes, state=passthrough_val)
    flow.redirect_uri = "http://localhost:3000/datasources"

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        state=passthrough_val,
        include_granted_scopes='true'
    )

    response = {"url": authorization_url}
    session['state'] = state

    return response


@google_ads_auth.route('/gad2', methods=['POST'])
@jwt_required()
def gad2():
    if request.method == 'POST':
        a = json.loads(request.data)
        s = a['tokens']
        #result = re.search('code=(.*)&scope', s)
        #asd = result.group(1)
        state = session['state']

        scopes = ['https://www.googleapis.com/auth/adwords']

        client_config = {
            "web": {
                "client_id": "384533319422-5kbe301aebs7i9nf6js486r37onmqvh7.apps.googleusercontent.com",
                "project_id": "dv360test-335416",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "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",
                "redirect_uris": ["http://localhost:3000/datasources"]
            }
        }

        flow = Flow.from_client_config(
            client_config, scopes=scopes, state=state)
        flow.redirect_uri = "http://localhost:3000/datasources"

        #code = _get_authorization_code(state)

        # Pass the code back into the OAuth module to get a refresh token.
        authorization_response = s
        flow.fetch_token(authorization_response=authorization_response)
        # flow.fetch_token(code=asd)
        refresh_token = flow.credentials.refresh_token
        access_token = flow.credentials.token
        # Vraj vracia ID uctu pod ktorym emailom sa autorizuje. Mame istotu ze vracia len jeden riadok?
        user = get_jwt_identity()
        user_id = User.query.filter_by(email=user).first()

        #[ds['Datasource'] for ds in datasources]

        if refresh_token != None:
            # tu potrebujeme updatnut refresh token alebo zalozit noveho zakaznika
            account_id = get_customer(refresh_token, True)
            datasources = User_datasources_tokens.query.filter_by(
                User_ID=user_id.id, account_id=account_id, Datasource='gad').first()

            if datasources != None:

                datasources.token = refresh_token
                db.session.commit()

            else:
                new_datasource = User_datasources_tokens(
                    Datasource='gad', token=refresh_token, account_id=account_id, User_ID=user_id.id)
                db.session.add(new_datasource)
                db.session.commit()
        else:
            # tu potrebujeme len pozriet nove accountu pod nasim zakacnickym accountom
            account_id = get_customer(access_token, False)

        # vracia customerov pod accountom
        # z accountId berem 0 lebo to vracia list
        if refresh_token != None:
            customers_u_account = get_customers_under_account(
                account_id[0], refresh_token, True)
        else:
            customers_u_account = get_customers_under_account(
                account_id[0], access_token, False)

        customers_u_account['User_ID'] = user_id.id
        customers_u_account['Active'] = 0
        customers_u_account['Datasource'] = 'gad'
        customers_u_account['Account'] = account_id[0]

        print(customers_u_account)
        db.session.query(User_datasources).filter(
            User_datasources.User_ID == user_id.id, User_datasources.Datasource == 'gad', User_datasources.Account == account_id[0]).delete()
        db.session.commit()

        customers_u_account.to_sql(
            name='User_datasources', con=db.engine, if_exists="append", index=False, method='multi')

        user_datasources = User_datasources.query.filter_by(
            User_ID=user_id.id).all()

        response = json.dumps(
            User_datasources.serialize_list(user_datasources))

    return response


def get_customer(token, is_refresh):
    url = "https://googleads.googleapis.com/v8/customers:listAccessibleCustomers"

    payload = {}

    if is_refresh:
        authorization_token = get_oauth_token(token)
    else:
        authorization_token = "Bearer " + token

    headers = {
        'Content-Type': 'application/json',
        'developer-token': 'FcSPrV8UTy3Ed7fTug8KMg',
        'Authorization': authorization_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()["resourceNames"]


def get_customers_under_account(account_id, token, is_refresh):

    url = "https://googleads.googleapis.com/v8/{}/googleAds:searchStream".format(
        account_id)
    payload = json.dumps({
        "query": "SELECT customer_client.client_customer,customer_client.level,customer_client.manager,customer_client.descriptive_name,customer_client.currency_code,customer_client.time_zone,customer_client.id FROM customer_client WHERE customer_client.manager <> true"
    })

    if is_refresh:
        authorization_token = get_oauth_token(token)
    else:
        authorization_token = "Bearer " + token

    headers = {
        'Content-Type': 'application/json',
        'developer-token': 'FcSPrV8UTy3Ed7fTug8KMg',
        'Authorization': authorization_token
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response = response.json()

    normalized_response = pd.json_normalize(
        data=response, record_path=["results"])

    # final = pd.DataFrame(normalized_response[['customerClient.id',
    #                             'customerClient.descriptiveName']])
    final = pd.DataFrame(normalized_response[['customerClient.id']])
    final.rename(columns={'customerClient.id': 'Client'}, inplace=True)

    return final


def get_oauth_token(refresh_token):

    client_id = "384533319422-5kbe301aebs7i9nf6js486r37onmqvh7.apps.googleusercontent.com"
    client_secret = "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"
    grant_type = "refresh_token"

    url = "https://www.googleapis.com/oauth2/v3/token?client_id={}&client_secret={}&refresh_token={}&grant_type={}".format(
        client_id, client_secret, refresh_token, grant_type)

    payload = {}
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload)

    bearer_token = response.json()["token_type"] + \
        " " + response.json()["access_token"]

    return bearer_token
