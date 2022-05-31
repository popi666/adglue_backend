#zmena
from requests import post
import configurator as conf
import data_to_blob as blob
import data_to_sql as sql
import json
import pandas as pd
from datetime import datetime as dt
import config_keyvault as kv

def login(access_token, customer):
    rest_login_link = conf.get_parameter(customer, "datasource", "sklik", "rest_login")
    response = post(rest_login_link,json=(access_token))
    res = response.json()
    if res["status"] == 200:
        global session
        session = res["session"]
        return True
    else:
        return False

def read_entity_data(customer, entity, date_from, date_to):
    rest_create_report_link = conf.get_parameter(customer, "datasource", "sklik", "entity", entity, "rest_create_report")
    rest_read_report_link = conf.get_parameter(customer, "datasource", "sklik", "entity", entity, "rest_read_report")
    access_token = kv.get_secret_value("SKLAuthToken")
    display_columns = tuple(conf.get_parameter(customer, "datasource", "sklik", "entity", entity, "display_columns"))
    if login(access_token, customer):
        #First step - create report based on input parameters
        response = post(rest_create_report_link, json=[{"session":session},
        {"dateFrom":date_from,
        "dateTo":date_to},
        {"statGranularity":"daily"}
        ])
        report_id = response.json()['reportId']
        row_count = response.json()['totalCount']

        #Second step - read report with data
        max_limit = 5000
        d1 = dt.strptime(date_from, '%Y-%m-%d')
        d2 = dt.strptime(date_to, '%Y-%m-%d')
        days_to_download = d2 - d1
        limit = max_limit//days_to_download.days
        offset = 0
        if limit >= row_count:
            response = post(rest_read_report_link, json=[{"session":session},
            report_id,
            {"offset":offset,
            "limit":limit,   #pri vetsim cisle uz nevrati zadny vysledek
            "allowEmptyStatistics":False,
            "displayColumns":display_columns
            }])
            return response.json()
        else:
            while limit < row_count:
                response = post(rest_read_report_link, json=[{"session":session},
                report_id,
                {"offset":offset,
                "limit":limit,
                "allowEmptyStatistics":False,
                "displayColumns":display_columns
                }])
                data = data + response
                row_count = row_count-limit
                offset = offset + limit + 1
            return data
    else:
        return False

def clean_data_for_sql_input(entity, data):
    if entity == "ads":
        normalized_data = pd.json_normalize(data = data, record_path=["report", "stats"], meta=[["report", "adType"], ["report", "id"], ["report", "name"], ["report", "adStatus"], ["report", "campaign", "id"], ["reportId"]])
        normalized_data["date"] = pd.to_datetime(normalized_data["date"], format="%Y%m%d")
        normalized_data["insertDatetime"] = dt.now()
        normalized_data.rename(columns={"report.adType":"adType", "report.id":"id", "report.name":"name", "report.adStatus":"adStatus", "report.campaign.id":"campaignId"}, inplace=True)
    if entity == "campaigns":
        normalized_data = pd.json_normalize(data=data, record_path=["report", "stats"], meta=[["report", "actualClicks"], ["report", "totalClicksFrom"], ["report", "totalBudget"], ["report", "endDate"], ["report", "name"], ["report", "totalBudgetFrom"], ["report", "totalClicks"], ["report", "id"], ["report", "startDate"], ["report", "createDate"], ["reportId"]])
        #normalized_data.to_csv("g:\\My Drive\\Adpoint\\Solution\\python_solution\\output.csv")
        normalized_data.rename(columns={"report.actualClicks":"actualClicks", "report.totalClicksFrom":"totalClicksFrom", "report.totalClicksFrom":"totalClicksFrom", "report.totalBudget":"totalBudget", "report.endDate":"endDate", "report.name":"name", "report.totalBudgetFrom":"totalBudgetFrom","report.totalClicks":"totalClicks", "report.id":"id", "report.startDate":"startDate", "report.createDate":"createDate"}, inplace=True)
        normalized_data["date"] = pd.to_datetime(normalized_data["date"], format="%Y%m%d")
        normalized_data["totalClicksFrom"] = pd.to_datetime(normalized_data["totalClicksFrom"])
        normalized_data["endDate"] = pd.to_datetime(normalized_data["endDate"])
        normalized_data["totalBudgetFrom"] = pd.to_datetime(normalized_data["totalBudgetFrom"])
        normalized_data["startDate"] = pd.to_datetime(normalized_data["startDate"])
        normalized_data["createDate"] = pd.to_datetime(normalized_data["createDate"])
        normalized_data["insertDatetime"] = dt.now()
    return normalized_data
    

def process_sklik_data_to_stage(customer, entity, date_from, date_to):
    data = read_entity_data(customer, entity, date_from, date_to)
    blob_name = customer + "\\sklik\\" + str(dt.now().date()) + "\\" + data['reportId'] + ".json"
    data_dump = json.dumps(data)
    blob.save_data_to_blob(customer, data_dump, blob_name)
    normalized_data = clean_data_for_sql_input(entity, data)
    sql.save_data_to_sql(normalized_data, customer, "sklik", entity)
    print ("Sklik {} data has been processed".format(entity))