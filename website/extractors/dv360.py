import data_to_blob as blob
import data_to_sql as sql
import configurator as conf
import requests
import json
from datetime import datetime as dt
import pandas as pd
import logginglogger as logger
import urllib.request
import os.path
import sys
import config_keyvault as kv


def get_oauth_token(config):

    client_id = kv.get_secret_value("DV360ClientId")
    client_secret = kv.get_secret_value("DV360ClientSecret")
    refresh_token = kv.get_secret_value("DV360AuthToken")
    grant_type = config.get_parameter(
        'dv360', 'ads', 'grant_type')

    url = "https://www.googleapis.com/oauth2/v3/token?client_id={}&client_secret={}&refresh_token={}&grant_type={}".format(
        client_id, client_secret, refresh_token, grant_type)

    payload = {}
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload)

    bearer_token = response.json()["token_type"] + \
        " " + response.json()["access_token"]

    return bearer_token


def create_query_and_id_ads(date_from, date_to, config):

    url = "https://www.googleapis.com/doubleclickbidmanager/v1.1/query"

    payload = json.dumps({
        "kind": "doubleclickbidmanager#query",
        "params": {
            "type": "TYPE_GENERAL",
            "groupBys": [
                "FILTER_PARTNER",
                "FILTER_PARTNER_NAME",
                "FILTER_PARTNER_STATUS",
                "FILTER_DATE",
                "FILTER_MEDIA_PLAN",
                "FILTER_MEDIA_PLAN_NAME",
                "FILTER_ADVERTISER",
                "FILTER_ADVERTISER_NAME",
                "FILTER_ADVERTISER_CURRENCY",
                "FILTER_CREATIVE",
                "FILTER_CREATIVE_ID"
            ],
            "filters": [
                {
                    "type": "FILTER_PARTNER",
                    "value": "703604047"
                }
            ],
            "metrics": [
                "METRIC_IMPRESSIONS",
                "METRIC_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS",
                "METRIC_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS",
                "METRIC_CLICKS",
                "METRIC_TOTAL_MEDIA_COST_ADVERTISER",
                "METRIC_MEDIA_COST_ADVERTISER",
                "METRIC_REVENUE_ADVERTISER",
                "METRIC_RICH_MEDIA_VIDEO_PLAYS",
                "METRIC_RICH_MEDIA_VIDEO_COMPLETIONS",
                "METRIC_RICH_MEDIA_VIDEO_FIRST_QUARTILE_COMPLETES",
                "METRIC_RICH_MEDIA_VIDEO_MIDPOINTS",
                "METRIC_RICH_MEDIA_VIDEO_THIRD_QUARTILE_COMPLETES",
                "METRIC_TOTAL_CONVERSIONS",
                "METRIC_CTR"
            ]
        },
        "metadata": {
            "title": "Adpoint reporting",
            "format": "CSV",
            "dataRange": "CUSTOM_DATES",
            "sendNotification": False,
            "running": False,
            "googleCloudStoragePathForLatestReport": ""
        },
        "reportDataStartTimeMs": date_from,
        "reportDataEndTimeMs": date_to,
        "queryId": 0,
        "schedule": {
            "frequency": "ONE_TIME"
        }
    })
    headers = {
        'Authorization': get_oauth_token(config),
        'developer-token': kv.get_secret_value("DV360DevToken"),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    query_id = response.json()['queryId']

    return query_id


def create_query_and_id_campaigns(date_from, date_to, config):

    url = "https://www.googleapis.com/doubleclickbidmanager/v1.1/query"

    payload = json.dumps({
        "kind": "doubleclickbidmanager#query",
        "params": {
            "type": "TYPE_GENERAL",
            "groupBys": [
                "FILTER_PARTNER",
                "FILTER_PARTNER_NAME",
                "FILTER_PARTNER_STATUS",
                "FILTER_DATE",
                "FILTER_MEDIA_PLAN",
                "FILTER_MEDIA_PLAN_NAME",
                "FILTER_ADVERTISER",
                "FILTER_ADVERTISER_NAME",
                "FILTER_ADVERTISER_CURRENCY"
            ],
            "filters": [
                {
                    "type": "FILTER_PARTNER",
                    "value": "703604047"
                }
            ],
            "metrics": [
                "METRIC_IMPRESSIONS",
                "METRIC_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS",
                "METRIC_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS",
                "METRIC_CLICKS",
                "METRIC_TOTAL_MEDIA_COST_ADVERTISER",
                "METRIC_MEDIA_COST_ADVERTISER",
                "METRIC_REVENUE_ADVERTISER",
                "METRIC_RICH_MEDIA_VIDEO_PLAYS",
                "METRIC_RICH_MEDIA_VIDEO_COMPLETIONS",
                "METRIC_RICH_MEDIA_VIDEO_FIRST_QUARTILE_COMPLETES",
                "METRIC_RICH_MEDIA_VIDEO_MIDPOINTS",
                "METRIC_RICH_MEDIA_VIDEO_THIRD_QUARTILE_COMPLETES",
                "METRIC_TOTAL_CONVERSIONS",
                "METRIC_CTR"
            ]
        },
        "metadata": {
            "title": "Adpoint reporting",
            "format": "CSV",
            "dataRange": "CUSTOM_DATES",
            "sendNotification": False,
            "running": False,
            "googleCloudStoragePathForLatestReport": ""
        },
        "reportDataStartTimeMs": date_from,
        "reportDataEndTimeMs": date_to,
        "queryId": 0,
        "schedule": {
            "frequency": "ONE_TIME"
        }
    })
    headers = {
        'Authorization': get_oauth_token(config),
        'developer-token': kv.get_secret_value("DV360DevToken"),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    query_id = response.json()['queryId']

    return query_id


def delete_query(query_id, config):

    url = "https://www.googleapis.com/doubleclickbidmanager/v1.1/query/{}".format(
        query_id)

    payload = {}
    headers = {
        'Authorization': get_oauth_token(config),
        'developer-token': kv.get_secret_value("DV360DevToken"),
        'Content-Type': 'application/json'
    }

    requests.request("DELETE", url, headers=headers, data=payload)


def get_report_ads(customer, date_from, date_to, config):

    begin_time = dt.now()

    query_id = create_query_and_id_ads(date_from, date_to, config)

    url = "https://www.googleapis.com/doubleclickbidmanager/v1.1/queries/{}/reports".format(
        query_id)

    payload = {}
    headers = {
        'Authorization': get_oauth_token(config),
        'developer-token': kv.get_secret_value("DV360DevToken"),
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    reports = pd.json_normalize(response.json()['reports'])
    reports_url = reports['metadata.googleCloudStoragePath'][0]

    df_reports = pd.read_csv(reports_url)

    # vymazuje sa poslednych 24 stlpcov - 23 su metadata a 24. je sumarizcny
    df_reports.drop(df_reports.tail(24).index, inplace=True)

    file = urllib.request.urlopen(reports_url)
    b = file.length

    processing_time = dt.now() - begin_time
    minutes = divmod(processing_time.seconds, 60)

    logger.log.info(
        "{}::{}::DV360::2::{}::{}::{}::Api request".format(customer, "ads", b, None, minutes[1]))

    delete_query(query_id, config)

    #df_reports.drop(['Date','Partner','Partner Status','Campaign','Advertiser','Advertiser Currency','Creative','Click Rate (CTR)'], axis=1, inplace=True)

    #df_reports = df_reports.reindex(sorted(df_reports.columns), axis=1)

    return df_reports


def get_report_campaigns(customer, date_from, date_to, config):

    begin_time = dt.now()

    query_id = create_query_and_id_campaigns(date_from, date_to, config)

    url = "https://www.googleapis.com/doubleclickbidmanager/v1.1/queries/{}/reports".format(
        query_id)

    payload = {}
    headers = {
        'Authorization': get_oauth_token(config),
        'developer-token': kv.get_secret_value("DV360DevToken"),
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    reports = pd.json_normalize(response.json()['reports'])
    reports_url = reports['metadata.googleCloudStoragePath'][0]

    df_reports = pd.read_csv(reports_url)

    file = urllib.request.urlopen(reports_url)
    b = file.length

    processing_time = dt.now() - begin_time
    minutes = divmod(processing_time.seconds, 60)

    logger.log.info(
        "{}::{}::DV360::2::{}::{}::{}::Api request".format(customer, "campaign", b, None, minutes[1]))

    # vymazuje sa poslednych 24 stlpcov - 23 su metadata a 24. je sumarizcny
    df_reports.drop(df_reports.tail(15).index, inplace=True)

    delete_query(query_id, config)

#df_reports.drop(['Date','Partner','Partner Status','Campaign','Advertiser','Advertiser Currency','Creative','Click Rate (CTR)'], axis=1, inplace=True)

#df_reports = df_reports.reindex(sorted(df_reports.columns), axis=1)

    return df_reports


def process_dv360_data_to_stage(customer, entity, date_from, date_to, config):

    logger.log.info(
        "{}::{}::DV360::1::{}::{}::{}::Launch of connector".format(customer, entity, None, None, None))
    try:

        date_to_dt = dt.strptime(date_to, "%Y-%m-%d")
        date_from_dt = dt.strptime(date_from, "%Y-%m-%d")

        date_to_ms = int(dt.timestamp(date_to_dt) * 1000)
        date_from_ms = int(dt.timestamp(date_from_dt) * 1000)

        if entity == "ads":
            data = get_report_ads(
                customer, date_from_ms, date_to_ms, config)
        else:
            data = get_report_campaigns(
                customer, date_from_ms, date_to_ms, config)

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logger.log.error(
            "{}::{}::DV360::4::{}::{}::{}::Filename: {}. Line_no: {}. {}, {}".format(customer, entity, None, None, None, fname, exc_tb.tb_lineno, exc_type, exc_obj))

    else:
        #blob_name = customer + "\\facebook\\" + str(dt.now().date()) + "\\" + request_id + ".json"
        #blob.save_data_to_blob(customer, data_dump, blob_name)
        #sql.delete_from_stage_table(customer, "google_ads", entity, date_from, date_to, config)
        sql.save_data_to_sql(data, customer, "dv360", entity, config)
