from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from numpy import DataSource
from .models import User, Customer, User_datasources_tokens, User_datasources, Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import json
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, unset_jwt_cookies, jwt_required, JWTManager
from .DB_creation import create_db_instance
from .extractors.main_extractor import main
# from .extractors.google_auth import run_auth
from google_auth_oauthlib.flow import Flow
import requests
import os
import itertools

from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = json.loads(request.data)
        email = data['email']
        password = data['pass']

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                # flash('Logged in successfully!', category='success')
                # login_user(user, remember=True)
                # return redirect(url_for('views.home'))
                access_token = create_access_token(identity=email)
                response = {"access_token": access_token}

            else:
                return {"msg": "Wrong email or password"}, 401
        else:
            return {"msg": "Email does not exist"}, 401
    return response


@auth.route('/user', methods=['GET'])
@jwt_required()
def user():
    if request.method == 'GET':
        response = {"user": "success"}
        # print(user)

    return response


@auth.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        response = jsonify({"msg": "logout successful"})
        unset_jwt_cookies(response)
    return response


@ auth.route('/sign-up', methods=['POST'])
def sign_up():
    if request.method == 'POST':
        data = json.loads(request.data)

        email = data['email']
        first_name = data['first_name']
        password1 = data['password']
        password2 = data['password2']

        user = User.query.filter_by(email=email).first()
        if user:
            return {'message': 'Email already exists.'}
        # elif len(email) < 4:
        #    flash('Email must be greater than 3 characters.', category='error')
        # elif len(first_name) < 2:
        #    flash('First name must be greater than 1 character.', category='error')
        # elif password1 != password2:
        #    flash('Passwords don\'t match.', category='error')
        # elif len(password1) < 7:
        #    flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()

            create_db_instance(email)

            # login_user(new_user, remember=True)
           # flash('Account created!', category='success')
            # return redirect(url_for('views.home'))

    # render_template("sign_up.html", user=current_user)
    return {"message": 'access_token'}


@auth.route('/fb', methods=['GET'])
@jwt_required()
def fb():
    # if request.method == 'GET':
    # response = {"message": "success"}
    user = get_jwt_identity()
    # auth_url = run_auth()
    # response = {"url": auth_url}
    # main(user)
    DEFAULT_OAUTH_URL = "https://www.facebook.com/dialog/oauth"
    DEFAULT_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"
    DEFAULT_REDIRECT_URL = "http://localhost:3000/"
    # DEFAULT_REDIRECT_URL = "https://www.adglue.io/"
    # app_id = "276770624263710"
    # app_secret = "157c670e522c91e17c9f8a1754332def"

    app_id = "7189850204418573"  # test app
    app_secret = "b51eeb5e21ed1233ab9da8c671c81830"

    facebook = OAuth2Session(
        client_id=app_id, redirect_uri=DEFAULT_REDIRECT_URL)
    facebook = facebook_compliance_fix(facebook)

    authorization_url, state = facebook.authorization_url(DEFAULT_OAUTH_URL)

    response = {"url": authorization_url}
    session['state'] = state

    return response


@auth.route('/fb2', methods=['POST'])
@jwt_required()
def fb2():
    if request.method == 'POST':
        a = json.loads(request.data)
        s = a['tokens']
        # result = re.search('code=(.*)&scope', s)
        # asd = result.group(1)
        DEFAULT_OAUTH_URL = "https://www.facebook.com/dialog/oauth"
        DEFAULT_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"
        DEFAULT_REDIRECT_URL = "http://localhost:3000/"
        # DEFAULT_REDIRECT_URL = "https://www.adglue.io/"
        # app_id = "276770624263710"
        # app_secret = "157c670e522c91e17c9f8a1754332def"

        app_id = "7189850204418573"  # test app
        app_secret = "b51eeb5e21ed1233ab9da8c671c81830"

        facebook = OAuth2Session(
            client_id=app_id, redirect_uri=DEFAULT_REDIRECT_URL)
        facebook = facebook_compliance_fix(facebook)

        # code = _get_authorization_code(state)

        # Pass the code back into the OAuth module to get a refresh token.
        authorization_response = s
        facebook.fetch_token(
            token_url=DEFAULT_TOKEN_URL,
            client_secret=app_secret,
            authorization_response=authorization_response,
        )
        access_token = facebook.access_token

        print(access_token)

        # refresh_token = credentials._refresh_token

    return {"message": 'success'}


@auth.route('/customers', methods=['GET', 'POST'])
@jwt_required()
def customer():
    if request.method == 'GET':

        user = get_jwt_identity()

        user_id = User.query.filter_by(email=user).first()
        customers = Customer.query.filter_by(User_ID=user_id.id).all()
        customers_serialized = json.dumps(Customer.serialize_list(customers))

        response = customers_serialized

    else:
        data = json.loads(request.data)

        user = get_jwt_identity()

        user_info = User.query.filter_by(email=user).first()

        # db.session.query(Customer).filter(
        #    Customer.User_ID == user_info.id).delete()
        for row in data:

            customer = Customer.query.filter_by(
                User_ID=user_info.id, id=row['id']).first()
            if customer == None:
                db.session.add(Customer(**row))
            else:
                customer.Client = row['Client']
                customer.Volume = row['Volume']
                customer.Active = row['Active']

        db.session.commit()


#        for row in data:
#

#        db.session.commit()
        response = {"message": 'success'}

    return response


@auth.route('/datasources', methods=['GET', 'POST'])
@jwt_required()
def datasources():
    if request.method == 'GET':

        user = get_jwt_identity()

        user_id = User.query.filter_by(email=user).first()
        # user_datasources = User_datasources.query.filter_by(
        #    User_ID=user_id.id).all()

        results = db.session.query(User_datasources.id, User_datasources.Account, User_datasources.Master_account, User_datasources.Datasource, User_datasources.Active,
                                   User_datasources.User_ID, Customer.Client).join(Customer, Customer.id == User_datasources.user_client_id, isouter=True).filter(User_datasources.User_ID == user_id.id).all()

        keys = ['id', 'Account', 'Master_account',
                'Datasource', 'Active', 'User_ID', 'Client']
        response_list = [{keys[0]: result[0], keys[1]: result[1], keys[2]: result[2], keys[3]: result[3],
                          keys[4]: result[4], keys[5]: result[5], keys[6]: result[6]} for result in results]

        # results = db.session.query(User_datasources, Customer).join(
        #    Customer, Customer.id == User_datasources.user_client_id, isouter=True).filter(User_datasources.User_ID == user_id.id).all()

        # response = json.dumps(User_datasources.serialize_list(results))

        response = json.dumps(response_list)

    else:
        data = json.loads(request.data)
        print(type(data))
        print(data)

        user = get_jwt_identity()

        user_info = User.query.filter_by(email=user).first()

        db.session.query(Customer).filter(
            Customer.User_ID == user_info.id).delete()
        db.session.commit()

        for row in data:
            db.session.add(Customer(**row))

        db.session.commit()
        response = {"message": 'success'}

    return response

# Slouží pro vygenerování CustomerId, které je součástí config.json
