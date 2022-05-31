import sqlalchemy as sal
from sqlalchemy import create_engine
import urllib
import pandas as pd
#import configurator as conf
#import logginglogger as logger
import os
import sys
from datetime import datetime as dt
from . import config_keyvault as kv


def get_target_object(object, entity, datasource):

    target_tables = {
        "schema": {
            "campaign": {
                "google_ads": "stage",
                "DV360": "stage"
            },
            "ad": {
                "google_ads": "googleads_ad",
                "DV360": "DV360_ad"
            }
        },
        "table": {
            "campaign": {
                "google_ads": "googleads_campaign",
                "DV360": "DV360_campaign"
            },
            "ad": {
                "google_ads": "googleads_ad",
                "DV360": "DV360_ad"
            }
        }
    }

    name = target_tables[object][entity][datasource]
    return name


def save_data_to_sql(data, customer, datasource, entity, user_email):

    # try:
    driver = "{ODBC Driver 17 for SQL Server}"
    server = "baseadpoint.database.windows.net"
    database = user_email
    user = "adpoint"
    password = kv.get_secret_value("MsSqlPassword")
    # config.get_parameter(datasource, entity, "sql_target_schema")
    schema = get_target_object("schema", entity, datasource)
    # config.get_parameter(datasource, entity, "sql_target_table")
    table = get_target_object("table", entity, datasource)

    conn = f"""Driver={driver};Server=tcp:{server},1433;Database={database};
            Uid={user};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""

    params = urllib.parse.quote_plus(conn)
    conn_str = 'mssql+pyodbc:///?autocommit=true&odbc_connect={}'.format(
        params)
    engine = create_engine(conn_str, fast_executemany=True, echo=False)
    connection = engine.connect()

    dataframe = pd.read_sql_table(
        table_name=table,
        schema=schema,
        con=engine).head(0)

    dataframe = dataframe.append(data, ignore_index=True, sort=True)

    begin_time = dt.now()

    dataframe.to_sql(name=table, schema=schema, con=connection,
                     if_exists="append", index=False, method='multi', chunksize=80)

    processing_time = dt.now() - begin_time
    minutes = divmod(processing_time.seconds, 60)

    rows = len(data.index)

#    except Exception:
#        exc_type, exc_obj, exc_tb = sys.exc_info()
#        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#
#        logger.log.error(
#            "{}::{}::{}::5::{}::{}::{}::Filename: {}. Line_no: {}. {}, {}".format(customer, entity, datasource, None, None, None, fname, exc_tb.tb_lineno, exc_type, exc_obj))
#
#    else:
#        logger.log.info(
#            "{}::{}::{}::3::{}::{}::{}::Data to stage".format(customer, entity, datasource, None, rows, minutes[1]))


def delete_from_stage_table(customer, datasource, entity, date_from, date_to, user_email):

    driver = "{ODBC Driver 17 for SQL Server}"
    server = "baseadpoint.database.windows.net"
    database = user_email
    user = "adpoint"
    password = kv.get_secret_value("MsSqlPassword")
    # config.get_parameter(datasource, entity, "sql_target_schema")
    schema = get_target_object("schema", entity, datasource)
    # config.get_parameter(datasource, entity, "sql_target_table")
    table = get_target_object("table", entity, datasource)

    conn = f"""Driver={driver};Server=tcp:{server},1433;Database={database};
    Uid={user};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""

    params = urllib.parse.quote_plus(conn)
    conn_str = 'mssql+pyodbc:///?autocommit=true&odbc_connect={}'.format(
        params)
    engine = create_engine(conn_str, fast_executemany=True, echo=False)
    connection = engine.connect()
    connection.execute("EXECUTE delete_date_range '{}', '{}', '{}', '{}'".format(
        schema, table, date_from, date_to))


def get_data_from_table(table, schema):
    driver = "{ODBC Driver 17 for SQL Server}"
    server = "baseadpoint.database.windows.net"
    database = "adpoint"
    user = "adpoint"
    password = kv.get_secret_value("MsSqlPassword")

    conn = f"""Driver={driver};Server=tcp:{server},1433;Database={database};
    Uid={user};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""

    conn = f"""Driver={driver};Server=tcp:{server},1433;Database={database};
    Uid={user};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""

    params = urllib.parse.quote_plus(conn)
    conn_str = 'mssql+pyodbc:///?autocommit=true&odbc_connect={}'.format(
        params)
    engine = create_engine(conn_str, fast_executemany=True, echo=False)
    connection = engine.connect()

    dataframe = pd.read_sql_table(
        table_name=table,
        schema=schema,
        con=engine)

    return dataframe
