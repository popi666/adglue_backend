from sqlalchemy import create_engine 
import pandas as pd
import os.path
import logginglogger as logger
import config_keyvault as kv
import sys
import urllib
from datetime import datetime as dt

test_path =  r"C:\Users\Josef Alb\Desktop\adpoint\test\prezentace22022022"

def get_customer_data(directory_path):
    os.chdir(directory_path)
    session_df_xlsx = pd.DataFrame()
    session_df_csv = pd.DataFrame()
    files = os.listdir(directory_path)
    for file in files:
        ext = os.path.splitext(file)[-1].lower()
        if ext in (".xlsx",".xls"): 
            buffer_df_xslx = pd.read_excel(file)
            column_mapping_xlsx = {buffer_df_xslx.columns[0] : 'product_customer_id', buffer_df_xslx.columns[1] : 'product_name', buffer_df_xslx.columns[2]: 'product_category_id', buffer_df_xslx.columns[3] : 'product_category',
            buffer_df_xslx.columns[4] : 'valid_from', buffer_df_xslx.columns[5]: 'valid_to'}
            renamed_buffer_df_xslx = buffer_df_xslx.rename(columns = column_mapping_xlsx)
            session_df_xlsx = session_df_xlsx.append(renamed_buffer_df_xslx, ignore_index = True)
        elif ext == (".csv"):
            buffer_df_csv = pd.read_csv(file, encoding = 'iso-8859-1', sep = ';')
            column_mapping_csv = {buffer_df_csv.columns[0] : 'product_customer_id', buffer_df_csv.columns[1] : 'product_name', buffer_df_csv.columns[2]: 'product_category_id', buffer_df_csv.columns[3] : 'product_category',
            buffer_df_csv.columns[4] : 'valid_from', buffer_df_csv.columns[5]: 'valid_to'}
            renamed_buffer_df_csv = buffer_df_csv.rename(columns = column_mapping_csv)
            session_df_csv = session_df_csv.append(renamed_buffer_df_csv,ignore_index = True)  
        else:
            print(f"Unsupported format {ext}")
    frames = [session_df_xlsx, session_df_csv]
    session_df = pd.DataFrame()
    session_df = pd.concat(frames)
    return session_df

def save_customer_data_to_sql(customer_dataframe):
    driver = "{ODBC Driver 17 for SQL Server}"
    server = "baseadpoint.database.windows.net"
    database = "adpoint"
    user = "adpoint"
    password = kv.get_secret_value("MsSqlPassword")
    schema = "nutraceutics_stage" 
    table = "products"
    conn = f"""Driver={driver};Server=tcp:{server},1433;Database={database};
    Uid={user};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""
    params = urllib.parse.quote_plus(conn)
    conn_str = 'mssql+pyodbc:///?autocommit=true&odbc_connect={}'.format(
        params)
    engine = create_engine(conn_str, fast_executemany=True, echo=False)
    connection = engine.connect()
    try:
        dataframe = pd.read_sql_table(
        table_name = table,
        schema = schema,
        con = engine).head(0)
        dataframe = dataframe.drop(columns=["product_id"])
        dataframe = dataframe.append(customer_dataframe, ignore_index=True, sort=True)
        dataframe[['valid_from','valid_to']] = dataframe[['valid_from','valid_to']] .apply(pd.to_datetime)
        begin_time = dt.now()
        dataframe.to_sql(name = table, schema = schema, con=connection, if_exists="append", index=False)
        rows = len(dataframe.index)
        processing_time = dt.now() - begin_time
        minutes = divmod(processing_time.seconds, 60)
        begin_time = dt.now()
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.log.error("{}::{}::CustomerInput::4::{}::{}::{}::Filename: {}. Line_no: {}. {}, {}".format("nutraceutics", "products", None, None, None, fname, exc_tb.tb_lineno, exc_type, exc_obj))
    else:
        logger.log.info("{}::{}::CustomerInput::3::{}::{}::{}::Data to stage".format("nutraceutics", "products", None, rows, minutes[1]))

# customer_data = get_customer_data(test_path)
# dataframe_customer = get_customer_data(test_path)
# dataframe = dataframe_customer
# print(dataframe)

# save_customer_data_to_sql(customer_data)
# driver = "{ODBC Driver 17 for SQL Server}"
# server = "baseadpoint.database.windows.net"
# database = "adpoint"
# user = "adpoint"
# password = kv.get_secret_value("MsSqlPassword")
# schema = "nutraceutics_stage" 
# table = "products"

# conn = f"""Driver={driver};Server=tcp:{server},1433;Database={database};
# Uid={user};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""

# params = urllib.parse.quote_plus(conn)
# conn_str = 'mssql+pyodbc:///?autocommit=true&odbc_connect={}'.format(
#     params)
# engine = create_engine(conn_str, fast_executemany=True, echo=False)
# connection = engine.connect()

# try:
#     dataframe = pd.read_sql_table(
#     table_name = table,
#     schema = schema,
#     con = engine).head(0)
#     dataframe = dataframe.drop(columns=["product_id"])
#     dataframe = dataframe.append(dataframe_customer, ignore_index=True, sort=True)
#     dataframe[['valid_from','valid_to']] = dataframe[['valid_from','valid_to']] .apply(pd.to_datetime)
#     begin_time = dt.now()
#     dataframe.to_sql(name = table, schema = schema, con=connection, if_exists="append", index=False)
#     rows = len(dataframe.index)
#     processing_time = dt.now() - begin_time
#     minutes = divmod(processing_time.seconds, 60)
#     begin_time = dt.now()
# except Exception:
#     exc_type, exc_obj, exc_tb = sys.exc_info()
#     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#     logger.log.error("{}::{}::CustomerInput::4::{}::{}::{}::Filename: {}. Line_no: {}. {}, {}".format("nutraceutics", "products", None, None, None, fname, exc_tb.tb_lineno, exc_type, exc_obj))
# else:
#     logger.log.info("{}::{}::CustomerInput::3::{}::{}::{}::Data to stage".format("nutraceutics", "products", None, rows, minutes[1]))

# def process_customer_data_to_sql(data_path):
logger.log.info(
    "{}::{}::CustomerInput::1::{}::{}::{}::Launch of connector".format(None, 'products', None, None, None))
# data = get_customer_data(data_path)
   #save_customer_data_to_sql(data)

#process_customer_data_to_sql(test_path)