import sqlalchemy as sal
from sqlalchemy import create_engine
import urllib
import pandas as pd
#import logginglogger as logger
import os
import sys
from datetime import datetime as dt
import config_keyvault as kv


class get_config:

    def __init__(self):

        self.driver = "{ODBC Driver 17 for SQL Server}"
        self.server = "baseadpoint.database.windows.net"
        self.database = "nutraceutics_extractors"
        self.user = "adpoint"
        self.password = kv.get_secret_value("MsSqlPassword")
        self.schema = "meta"
        self.table = "Config_datasource"

        self.conn = f"""Driver={self.driver};Server=tcp:{self.server},1433;Database={self.database};
            Uid={self.user};Pwd={self.password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""
        self.params = urllib.parse.quote_plus(self.conn)
        self.conn_str = 'mssql+pyodbc:///?autocommit=true&odbc_connect={}'.format(
            self.params)
        self.engine = create_engine(
            self.conn_str, fast_executemany=True, echo=False)

        self.df = self.get_config_data()

    def get_config_data(self):

        conn = f"""Driver={self.driver};Server=tcp:{self.server},1433;Database={self.database};
        Uid={self.user};Pwd={self.password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""

        params = urllib.parse.quote_plus(conn)
        conn_str = 'mssql+pyodbc:///?autocommit=true&odbc_connect={}'.format(
            params)
        engine = create_engine(conn_str, fast_executemany=True, echo=False)

        dataframe = pd.read_sql_table(
            table_name=self.table,
            schema=self.schema,
            con=engine)

        return dataframe

    def get_parameter(self, datasource, entity, parameter):

        return self.df.loc[(self.df.datasource == datasource) &
                           (self.df.entity == entity), parameter].values[0]

    def insert_new_customer(self, data):

        connection = self.engine.connect()

        df_template = self.df.head(0)

        print(df_template)
        print(data)
        dataframe = df_template.append(data, ignore_index=True, sort=True)
        print(dataframe)
        dataframe.to_sql(name=self.table, schema=self.schema, con=connection,
                         if_exists="append", index=False)
