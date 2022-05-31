#from . import data_to_blob as blob
from . import data_to_sql as sql
import requests
import json
from datetime import datetime as dt
import pandas as pd
#import logginglogger as logger
import sys
import os
from . import config_keyvault as kv


def get_oauth_token():
    client_id = kv.get_secret_value("GADClientId")
    client_secret = kv.get_secret_value("GADClientSecret")
    refresh_token = kv.get_secret_value("GADAuthToken")
    # grant_type = config.get_parameter(
    #    'google_ads', 'ad_group_ad', 'grant_type')
    grant_type = "refresh_token"
    url = "https://www.googleapis.com/oauth2/v3/token?client_id={}&client_secret={}&refresh_token={}&grant_type={}".format(
        client_id, client_secret, refresh_token, grant_type)

    payload = {}
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload)

    bearer_token = response.json()["token_type"] + \
        " " + response.json()["access_token"]

    return bearer_token

# Slouží pro vygenerování CustomerId, které je součástí config.json


def get_accessible_customers():
    url = "https://googleads.googleapis.com/v8/customers:listAccessibleCustomers"

    payload = {}
    headers = {
        'Authorization': get_oauth_token(),
        'developer-token': kv.get_secret_value("GADDevToken"),
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.json()["resourceNames"])


def get_all_accounts_under_account():

    top_level_customer_id = "6142249537"

    url = "https://googleads.googleapis.com/v8/customers/{}/googleAds:searchStream".format(
        top_level_customer_id)

    payload = json.dumps({
        "query": """SELECT customer_client.client_customer,
                customer_client.level,
                customer_client.manager,
                customer_client.descriptive_name,
                customer_client.currency_code,
                customer_client.time_zone,
                customer_client.id
                FROM customer_client
                WHERE customer_client.manager <> true"""
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': get_oauth_token(),
        'developer-token': kv.get_secret_value("GADDevToken"),
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()

# aktuálně vyvíjeno na customer_id 4096538239 (Nutraceutics CZ)


def get_report(customer, entity, date_from, date_to):

    begin_time = dt.now()

    url = "https://googleads.googleapis.com/v8/customers/4096538239/googleAds:searchStream"
    query = ""
    if entity == "ad_group_ad":
        query = """SELECT ad_group.id,
                ad_group.name,
                ad_group.status,
                ad_group.type,
                campaign.id,
                customer.currency_code,
                segments.date,
                customer.id,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.ctr,
                metrics.interactions,
                metrics.interaction_rate,
                metrics.conversions,
                metrics.cost_per_conversion,
                metrics.video_views,
                metrics.video_view_rate,
                metrics.video_quartile_p75_rate,
                metrics.video_quartile_p50_rate,
                metrics.video_quartile_p25_rate,
                metrics.video_quartile_p100_rate,
                metrics.average_time_on_site,
                ad_group_ad.ad.id,
                ad_group_ad.ad.name,
                ad_group_ad.status,
                ad_group_ad.ad.type
                FROM ad_group_ad
                WHERE segments.date
                BETWEEN '{}' AND '{}'""".format(date_from, date_to)
    elif entity == "campaign":
        query = """SELECT campaign.id,
                campaign.name,
                campaign.status,
                campaign.start_date,
                campaign.end_date,
                campaign.advertising_channel_type,
                campaign.advertising_channel_sub_type,
                customer.currency_code,
                segments.date,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.ctr,
                metrics.interactions,
                metrics.interaction_rate,
                metrics.conversions,
                metrics.cost_per_conversion,
                campaign_budget.amount_micros,
                metrics.video_quartile_p100_rate,
                metrics.video_quartile_p25_rate,
                metrics.video_quartile_p50_rate,
                metrics.video_quartile_p75_rate,
                metrics.video_view_rate,
                metrics.video_views,
                metrics.average_time_on_site,
                customer.id FROM campaign
                WHERE segments.date BETWEEN '{}' AND '{}'""".format(date_from, date_to)
    else:
        raise Exception(
            "Invalid entity name. Only 'ad_group_ad' and 'campaign' allowed")

    payload = json.dumps({
        "query": query
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': get_oauth_token(),
        'developer-token': kv.get_secret_value("GADDevToken"),
        'login-customer-id': "6142249537"
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    response_json = response.json()
    b = sys.getsizeof(json.dumps(response_json))

    processing_time = dt.now() - begin_time
    minutes = divmod(processing_time.seconds, 60)

   # logger.log.info(
   #     "{}::{}::GAD::2::{}::{}::{}::Api request".format(customer, entity, b, None, minutes[1]))

    return response_json


def clean_data_for_sql_input(entity, data):
    if entity == "ad_group_ad":
        normalized_data = pd.json_normalize(
            data=data, record_path=["results"], meta=["requestId"])
        normalized_data = normalized_data.drop(columns=["customer.resourceName",
                                                        "campaign.resourceName",
                                                        "adGroup.resourceName",
                                                        "adGroupAd.resourceName",
                                                        "adGroupAd.ad.resourceName"])
        normalized_data.rename(columns={"customer.id": "account_id",
                                        "customer.currencyCode": "currency_code",
                                        "campaign.id": "campaign_id",
                                        "adGroup.status": "adgroup_status",
                                        "adGroup.type": "adgroup_type",
                                        "adGroup.id": "adgroup_id",
                                        "adGroup.name": "adgroup_name",
                                        "metrics.clicks": "clicks",
                                        "metrics.videoViews": "video_views",
                                        "metrics.conversions": "conversions",
                                        "metrics.costMicros": "cost",
                                        "metrics.ctr": "ctr",
                                        "metrics.impressions": "impressions",
                                        "metrics.interactionRate": "interaction_rate",
                                        "metrics.interactions": "interactions",
                                        "adGroupAd.status": "ad_status",
                                        "adGroupAd.ad.type": "ad_type",
                                        "adGroupAd.ad.id": "ad_id",
                                        "segments.date": "date",
                                        "metrics.averageTimeOnSite": "average_time_on_site_sec",
                                        "metrics.costPerConversion": "cost_per_conversion",
                                        "metrics.videoQuartileP100Rate": "video_quartile_100pct_rate",
                                        "metrics.videoQuartileP25Rate": "video_quartile_25pct_rate",
                                        "metrics.videoQuartileP50Rate": "video_quartile_50pct_rate",
                                        "metrics.videoQuartileP75Rate": "video_quartile_75pct_rate",
                                        "adGroupAd.ad.name": "ad_name",
                                        "requestId": "request_id", },
                               inplace=True)
        normalized_data["date"] = pd.to_datetime(
            normalized_data["date"], format="%Y-%m-%d")
        normalized_data["insert_datetime"] = dt.now()
        request_id = normalized_data["request_id"][0]
        return normalized_data, request_id
    elif entity == "campaign":
        normalized_data = pd.json_normalize(
            data=data, record_path=["results"], meta=["requestId"])
        normalized_data = normalized_data.drop(columns=["customer.resourceName",
                                                        "campaign.resourceName",
                                                        "campaignBudget.resourceName"])
        normalized_data.rename(columns={"customer.id": "account_id",
                                        "customer.currencyCode": "currency_code",
                                        "campaign.status": "campaign_status",
                                        "campaign.advertisingChannelType": "advertising_channel_type",
                                        "campaign.name": "campaign_name",
                                        "campaign.id": "campaign_id",
                                        "campaignBudget.amountMicros": "budget",
                                        "campaign.startDate": "start_date",
                                        "campaign.endDate": "end_date",
                                        "metrics.clicks": "clicks",
                                        "metrics.videoViews": "video_views",
                                        "metrics.conversions": "conversions",
                                        "metrics.costMicros": "cost",
                                        "metrics.costPerConversion": "cost_per_conversion",
                                        "metrics.ctr": "ctr",
                                        "metrics.impressions": "impressions",
                                        "metrics.interactionRate": "interaction_rate",
                                        "metrics.interactions": "interactions",
                                        "segments.date": "date",
                                        "metrics.videoQuartileP100Rate": "video_quartile_100pct_rate",
                                        "metrics.videoQuartileP25Rate": "video_quartile_25pct_rate",
                                        "metrics.videoQuartileP50Rate": "video_quartile_50pct_rate",
                                        "metrics.videoQuartileP75Rate": "video_quartile_75pct_rate",
                                        "campaign.advertisingChannelSubType": "advertising_channel_subtype",
                                        "requestId": "request_id",
                                        "metrics.videoViewRate": "video_view_rate",
                                        "metrics.averageTimeOnSite": "average_time_on_site_sec"},
                               inplace=True)
        normalized_data["date"] = pd.to_datetime(
            normalized_data["date"], format="%Y-%m-%d")
        normalized_data["start_date"] = pd.to_datetime(
            normalized_data["start_date"], format="%Y-%m-%d")
        normalized_data["end_date"] = pd.to_datetime(
            normalized_data["end_date"], format="%Y-%m-%d")
        normalized_data["insert_datetime"] = dt.now()
        request_id = normalized_data["request_id"][0]
        return normalized_data, request_id
    else:
        raise Exception(
            "Invalid entity name. Only 'ad_group_ad' and 'campaign' allowed")


def process_google_ads_data_to_stage(customer, entity, date_from, date_to, user_email):

    # logger.log.info(
    #    "{}::{}::GAD::1::{}::{}::{}::Launch of connector".format(customer, entity, None, None, None))

    try:

        data = get_report(customer, entity,
                          date_from, date_to)
        normalized_data, request_id = clean_data_for_sql_input(entity, data)
        blob_name = customer + "\\google_ads\\" + \
            str(dt.now().date()) + "\\" + request_id + ".json"
        data_dump = json.dumps(data)
        #blob.save_data_to_blob(customer, data_dump, blob_name)

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        # logger.log.error(
        #    "{}::{}::GAD::4::{}::{}::{}::Filename: {}. Line_no: {}. {}, {}".format(customer, entity, None, None, None, fname, exc_tb.tb_lineno, exc_type, exc_obj))

    else:
        sql.delete_from_stage_table(
            customer, "google_ads", entity, date_from, date_to, user_email)
        sql.save_data_to_sql(normalized_data, customer,
                             "google_ads", entity, user_email)
