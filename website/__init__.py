from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import urllib.parse
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, unset_jwt_cookies, jwt_required, JWTManager
from datetime import datetime, timedelta, timezone

db = SQLAlchemy()
DB_NAME = "database.db"
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=baseadpoint.database.windows.net;DATABASE=Adglue;UID=adpoint;PWD=RDmCVIKuUPFhnBR9PwJ3")


def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
    db.init_app(app)

    app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    jwt = JWTManager(app)

    #db = SQLAlchemy(app)
    with app.app_context():

        db.Model.metadata.reflect(db.engine)

    #from .views import views
    from .auth import auth
    from .google_ads_auth import google_ads_auth
    #app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(google_ads_auth, url_prefix='/')

    # db.engine.table_names()

    from .models import User  # , Note

    # with app.app_context():

    #    print(db.engine.table_names())
    # print(db.metadata.tables.keys())
    #  ccc = db.Table('core.C_platform', db.metadata,
    #                 autoload=True, autoload_with=db.engine)

    #from .models import User, Note

    # create_database(app)
    '''
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    '''
    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
