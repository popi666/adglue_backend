import sqlalchemy as sal
from sqlalchemy import create_engine
import configurator as conf
import urllib
import pandas as pd
from datetime import datetime
import os
import socket

def log_to_db(customer, code_block, log_message):
    driver = conf.get_parameter(customer, "target", "mssql", "driver")
    server = conf.get_parameter(customer, "target", "mssql", "server")
    database = conf.get_parameter(customer, "target", "mssql", "database")
    user = conf.get_parameter(customer, "target", "mssql", "user")
    password = conf.get_parameter(customer, "target", "mssql", "password")
    log_db_schema = conf.get_parameter(customer, "target", "mssql", "log_db_schema")
    extractor_log_table = conf.get_parameter(customer, "target", "mssql", "extractor_log_table")

    conn = f"""Driver={driver};Server=tcp:{server},1433;Database={database};
    Uid={user};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""

    params = urllib.parse.quote_plus(conn)
    conn_str = 'mssql+pyodbc:///?autocommit=true&odbc_connect={}'.format(params)
    engine = create_engine(conn_str, fast_executemany=True, echo=False)
    connection = engine.connect()

    dataframe = pd.read_sql_table(
    table_name=extractor_log_table,
    schema=log_db_schema,
    con=engine).head(0)
    
    now = datetime.now()
    run_by_user = os.getlogin()
    run_by_machine = socket.gethostname()

    dataframe = dataframe.drop(columns=["Id"])

    log_data = pd.DataFrame([[now, run_by_user, run_by_machine, code_block, log_message]], columns=["Time", "RunByUser", "RunByMachine", "Extractor", "LogMessage"])

    dataframe = dataframe.append(log_data, ignore_index=True, sort=True)

    dataframe.to_sql(name = extractor_log_table, schema=log_db_schema, con=connection, if_exists="append", index=False)

log_to_db("nutraceutics", "nejaky_extraktor", "popis_chyby")





