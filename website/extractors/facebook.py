import requests
import configurator as conf
import pandas as pd
import json
from datetime import datetime as dt
import data_to_sql as sql
# import data_to_blob as blob
import logginglogger as logger
import sys
import os
# test pre ucet 240270927886966
import config_keyvault as kv


def get_ads_stats(customer, date_from, date_to, config):

    begin_time = dt.now()

    access_token = kv.get_secret_value("FCBAuthToken")

    url = "https://graph.facebook.com/v12.0/act_240270927886966?fields=ads{" \
          "insights.time_range({'since':'" + date_from + "','until':'" + date_to + "'}).time_increment(1){" \
          "conversions,clicks,impressions," \
          "date_start,date_stop,ad_name,spend,account_currency},campaign_id,adset_id,created_time},account_id,name" \
          "&access_token=" + access_token

    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)

    response_json = response.json()
    b = sys.getsizeof(json.dumps(response_json))

    processing_time = dt.now() - begin_time
    minutes = divmod(processing_time.seconds, 60)

    logger.log.info(
        "{}::{}::Facebook::2::{}::{}::{}::Api request".format(customer, "ads", b, None, minutes[1]))

    return response_json


def get_campaigns_stats(customer, date_from, date_to, config):

    begin_time = dt.now()

    access_token = config.get_parameter(
        'facebook', 'ads', 'authorization_token')

    url = "https://graph.facebook.com/v12.0/act_240270927886966?fields=campaigns" \
          "{insights.time_range({'since':'" + date_from + "','until':'" + date_to + "'}).time_increment(1)" \
          "{clicks,campaign_name,conversions," \
          "impressions,spend,account_currency," \
          "date_start," \
          "date_stop},start_time,stop_time}," \
          "name,account_id" \
          "&access_token=" + access_token

    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)

    response_json = response.json()
    b = sys.getsizeof(json.dumps(response_json))

    processing_time = dt.now() - begin_time
    minutes = divmod(processing_time.seconds, 60)

    logger.log.info(
        "{}::{}::Facebook::2::{}::{}::{}::Api request".format(customer, "campaigns", b, None, minutes[1]))

    return response_json


def process_json_ad_stats(customer, date_from, date_to, config):

    response_json = get_ads_stats(
        customer, date_from, date_to, config)
    data_ads = response_json['ads']['data']
    df = pd.json_normalize(data_ads)
    df_insights = df[["insights.data", "id",
                      'campaign_id', 'adset_id', 'created_time']]
    df_insights.dropna(inplace=True)
    df_insights.reset_index(inplace=True)
    df_final = pd.DataFrame()

    for i in range(0, len(df_insights.index)):
        df_final = df_final.append(pd.json_normalize(
            df_insights.loc[i, "insights.data"]).assign(id=df_insights.loc[i, "id"],
                                                        campaign_id=df_insights.loc[i,
                                                                                    "campaign_id"],
                                                        adset_id=df_insights.loc[i,
                                                                                 "adset_id"],
                                                        created_time=df_insights.loc[i, "created_time"]))

    df_final['created_time'] = df_final['created_time'].str[:10]
    df_final['account_id'] = response_json['account_id']
    df_final['account_name'] = response_json['name']

    df_final = df_final.reindex(sorted(df_final.columns), axis=1)

    return df_final


def process_json_campaigns_stats(customer, date_from, date_to, config):

    response_json = get_campaigns_stats(
        customer, date_from, date_to, config)
    data_camp = response_json['campaigns']['data']
    df = pd.json_normalize(data_camp)

    if "stop_time" in df.columns:

        df_insights = df[["insights.data", "id", "stop_time", "start_time"]]
        df_insights.dropna(inplace=True)
        df_insights.reset_index(inplace=True)
        df_final = pd.DataFrame()

        for i in range(0, len(df_insights.index)):
            df_final = df_final.append(
                pd.json_normalize(df_insights.loc[i, "insights.data"]).assign(id=df_insights.loc[i, "id"],
                                                                              start_time=df_insights.loc[i,
                                                                                                         "start_time"],
                                                                              stop_time=df_insights.loc[i, "stop_time"]))
        df_final['start_time'] = df_final['start_time'].str[:10]
        df_final['stop_time'] = df_final['start_time'].str[:10]

    else:

        df_insights = df[["insights.data", "id", "start_time"]]
        df_insights.dropna(inplace=True)
        df_insights.reset_index(inplace=True)
        df_final = pd.DataFrame()

        for i in range(0, len(df_insights.index)):
            df_final = df_final.append(
                pd.json_normalize(df_insights.loc[i, "insights.data"]).assign(id=df_insights.loc[i, "id"],
                                                                              start_time=df_insights.loc[i,
                                                                                                         "start_time"],
                                                                              stop_time=pd.Series()))
        df_final['start_time'] = df_final['start_time'].str[:10]

    df_final['account_id'] = response_json['account_id']
    df_final['account_name'] = response_json['name']

    df_final = df_final.reindex(sorted(df_final.columns), axis=1)

    return df_final


def process_facebook_data_to_stage(customer, entity, date_from, date_to, config):

    logger.log.info(
        "{}::{}::facebook::1::{}::{}::{}::Launch of connector".format(customer, entity, None, None, None))

    try:

        if entity == "ads":
            data = process_json_ad_stats(
                customer, date_from, date_to, config)
        else:
            data = process_json_campaigns_stats(
                customer, date_from, date_to, config)

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logger.log.error(
            "{}::{}::facebook::4::{}::{}::{}::Filename: {}. Line_no: {}. {}, {}".format(customer, entity, None, None, None, fname, exc_tb.tb_lineno, exc_type, exc_obj))

    else:
        # blob_name = customer + "\\facebook\\" + str(dt.now().date()) + "\\" + request_id + ".json"
        # blob.save_data_to_blob(customer, data_dump, blob_name)
        # sql.delete_from_stage_table(customer, "facebook", entity, date_from, date_to)
        sql.save_data_to_sql(data, customer, "facebook", entity, config)
