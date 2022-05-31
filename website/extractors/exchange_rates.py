from sqlalchemy import create_engine
import urllib
import pandas as pd
import config_keyvault as kv
import logginglogger as logger
import sys
import os.path
# test
# from config_sql import get_config


def get_data(date):

    url = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt;jsessionid=106D78886DE6D2B38AE2BF2349B4FC27?date={}".format(
        date.strftime('%d.%m.%Y'))
    
    logger.log.info(
        "{}::{}::ČNB::2::{}::{}::{}::Api request".format(None, "exchange_rates", None, None, None))

    try:
        df_header = pd.read_csv(url, nrows=0)
        df_date = pd.to_datetime(df_header.columns[0].split(" ")[0], dayfirst=True).date()

        if date == df_date:
            df = pd.read_csv(url, sep='|', skiprows=1, usecols= ["kód","množství","kurz"])
            df.insert(0, "date", pd.to_datetime(date))
            return df
        else:
            logger.log.warning(
                "{}::{}::ČNB::6::{}::{}::{}::Data for selected date not available".format(None, "exchange_rates", None, None, None))
            return False
    
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logger.log.error(
            "{}::{}::ČNB::4::{}::{}::{}::Filename: {}. Line_no: {}. {}, {}".format(None, "exchange_rates", None, None, None, fname, exc_tb.tb_lineno, exc_type, exc_obj))


def normalize_data(df):

    df.insert(1, "Valid_To", pd.to_datetime('2099-12-31'))
    df["kurz"] = df["kurz"].str.replace(",", ".").astype("float")
    normalized_data = df.rename(columns= {"date":"Valid_From", "kód":"Currency_Code", "množství":"Amount", "kurz":"Exchange_Rate"})
    return normalized_data


def save_rates_to_sql(data, config, datasource, entity):

    driver = "{ODBC Driver 17 for SQL Server}"
    server = "baseadpoint.database.windows.net"
    database = "adpoint"
    user = "adpoint"
    password = kv.get_secret_value("MsSqlPassword")
    # zatial namapované na testovaciu tabulku 
    schema = config.get_parameter(datasource, entity, "sql_target_schema")
    table = config.get_parameter(datasource, entity, "sql_target_table")
    procedure = "historization_exchange_rates"
    
    conn = f"""Driver={driver};Server=tcp:{server},1433;Database={database};
    Uid={user};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""

    params = urllib.parse.quote_plus(conn)
    conn_str = 'mssql+pyodbc:///?autocommit=true&odbc_connect={}'.format(
        params)

    engine = create_engine(conn_str, fast_executemany=True, echo=False)
    connection = engine.connect()

    try:
        dataframe = pd.read_sql_table(
            table_name=table,
            schema=schema,
            con=engine).head(0)

        dataframe_dates = pd.read_sql_table(
            table_name=table,
            schema=schema,
            con=engine)["Valid_From"].unique()

        date = data["Valid_From"][0]


        if pd.Series(dataframe_dates).isin([date]).any():
            engine.execute(f"DELETE FROM {schema}.{table} WHERE [Valid_From]= '{date}'")
            dataframe = dataframe.append(data, ignore_index=True, sort=True)
        else:
            dataframe = dataframe.append(data, ignore_index=True, sort=True)

        # push data to SQL
        dataframe.to_sql(name=table, schema=schema, con=connection,
                        if_exists="append", index=False)

        logger.log.info(
                "{}::{}::ČNB::3::{}::{}::{}::Data to stage".format(None, "exchange_rates", None, None, None))


        # execute SQL stored procedure
        logger.log.info(
                "{}::{}::ČNB::7::{}::{}::{}::SQL stored procedure execution - start".format(None, "exchange_rates", None, None, None))

        engine.execute(f"exec {schema}.{procedure} '{date}'")

        logger.log.info(
                "{}::{}::ČNB::7::{}::{}::{}::SQL stored procedure execution - finish".format(None, "exchange_rates", None, None, None))

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logger.log.error(
            "{}::{}::ČNB::4::{}::{}::{}::Filename: {}. Line_no: {}. {}, {}".format(None, "exchange_rates", None, None, None, fname, exc_tb.tb_lineno, exc_type, exc_obj))


def process_exchange_rates_to_sql(date, config, datasource, entity):

    logger.log.info(
            "{}::{}::ČNB::1::{}::{}::{}::Launch of connector".format(None, "exchange_rates", None, None, None))
    
    data = get_data(date)
    final_data = normalize_data(data)
    save_rates_to_sql(final_data, config, datasource, entity)



# test
# date = pd.to_datetime("2022-02-17").date()
# config= get_config()
# 
# process_exchange_rates_to_sql(date, config=config, datasource='cnb', entity='exchange_rates')