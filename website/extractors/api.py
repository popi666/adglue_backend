from unicodedata import name
from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import sqlalchemy
import data_to_sql


app = Flask(__name__)
api = Api(app)


class Campaigns(Resource):
    # def get(self):
    #     #data = data_to_sql.get_data_from_table('nutraceutics_core', 'DD_Campaign_Stats')
    #     data = ['a', 'b', 'c']
    #     data = data.to_dict()
    #     return {'data':data}, 200
    pass


class Ads(Resource):
    pass


api.add_resource(Campaigns, '/campaigns')
api.add_resource(Ads, '/ads')

if __name__ == "__main__":
    app.run()
