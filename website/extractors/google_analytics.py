from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import config_keyvault as kv
import pandas as pd
import json
from itertools import chain
import data_to_sql as sql
import logginglogger as logger
import os.path
import sys
from datetime import datetime as dt
# odmazat - len pre potreby testu
# from datetime import date, datetime, timedelta 
# from config_sql import get_config


def initialize_analyticsreporting():

    client_secret = kv.get_secret_value('GAClientSecret')
    client_secret_obj = json.loads(client_secret)

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(client_secret_obj)
    # Build the service object
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


def get_report(analytics, customer, view_id, date_from, date_to):

    begin_time = dt.now()
    
    response = analytics.reports().batchGet(
        body={
          'reportRequests': [
          {
            'viewId': view_id,
            'dateRanges': [{'startDate': date_from, 'endDate': date_to}],
            'metrics': [
                {'expression': 'ga:users'},
                {'expression': 'ga:newusers'},
                {'expression': 'ga:sessions'},
                {'expression': 'ga:pageviews'},
                {'expression':'ga:pageviewsPerSession'},
                {'expression': 'ga:bounces'},
                {'expression':'ga:sessionDuration'}],
            'dimensions': [
                {'name': 'ga:date'},
                {'name': 'ga:source'},
                {'name': 'ga:medium'}]
          }]
        }
    ).execute()

    processing_time = dt.now() - begin_time
    minutes = divmod(processing_time.seconds, 60)

    logger.log.info(
        "{}::{}::google_analytics::2::{}::{}::{}::Api request".format(customer, "n/a", None, None, minutes[1]))

    return response  


def parse_response(response):

    # get headers and rows into lists
    for report in response.get('reports', []):
  
        column_header = report.get('columnHeader', {})

        dimension_headers = column_header.get('dimensions', [])
        metric_headers_list = column_header.get('metricHeader', {}).get('metricHeaderEntries', [])
        metric_headers = []
    
        for x in metric_headers_list:
            metric_headers.append(x['name'])
    
        rows = report.get('data', {}).get('rows', [])

    # get dimension and metric values into DataFrames
    dimensions = []

    for row in rows:
        dimensions.append(row['dimensions'])

    metrics = []

    for row in rows:
        metrics.append(row['metrics'])
    
    metric_values = pd.DataFrame(list(chain.from_iterable(metrics)))

    df_dim = pd.DataFrame(dimensions, columns = dimension_headers )
    df_met = pd.DataFrame(metric_values['values'].to_list(), columns= metric_headers)

    # Create output table - merge dimensions and metrics - normalize data 
    output_df = df_dim.join(df_met)
    output_df = output_df.apply(pd.to_numeric, errors = "ignore")
    output_df["ga:date"] = pd.to_datetime(output_df["ga:date"], format='%Y%m%d')

    cln_columns = []

    for c in output_df.columns:
        c = c.replace("ga:", "")
        c = c.capitalize()
        cln_columns.append(c)

    output_df.columns = cln_columns

    return output_df


def process_ga_data_to_sql(view_id, customer, entity, date_from, date_to, config):

    logger.log.info(
        "{}::{}::google_analytics::1::{}::{}::{}::Launch of connector".format(customer, entity, None, None, None))

    try:
        analytics = initialize_analyticsreporting()
        response = get_report(analytics, customer, view_id, date_from, date_to)
        data = parse_response(response)
    
    except Exception:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logger.log.error(
            "{}::{}::google_analytics::4::{}::{}::{}::Filename: {}. Line_no: {}. {}, {}".format(customer, entity, None, None, None, fname, exc_tb.tb_lineno, exc_type, exc_obj))

    else:
        sql.delete_from_stage_table(
            customer, "google_analytics", entity, date_from, date_to, config)
        sql.save_data_to_sql(
            data, customer, "google_analytics", entity, config)


#-------------------------------------------------------------------------
# TEST
#-------------------------------------------------------------------------
# 
# days_to_load = 30
# date_to = date.today() - timedelta(days=1)
# date_from = date_to - timedelta(days=days_to_load)
# date_to = date_to.strftime("%Y-%m-%d")
# date_from = date_from.strftime("%Y-%m-%d")
# config = get_config()
# 
# process_ga_data_to_sql(
#     view_id='228976717', customer="BaseInsight", entity="n/a", date_from=date_from, date_to=date_to, config=config)