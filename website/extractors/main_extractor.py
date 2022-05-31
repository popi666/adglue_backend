#from logging import error, exception
#from time import strftime
#import sklik
from . import google_ads
#import data_to_sql as db
from datetime import date, datetime, timedelta
#import dv360
#import logginglogger as logger
#import facebook
#from config_sql import get_config
#import google_auth

days_to_load = 30
date_to = date.today() - timedelta(days=1)
date_from = date_to - timedelta(days=days_to_load)
date_to = date_to.strftime("%Y-%m-%d")
date_from = date_from.strftime("%Y-%m-%d")

# logger.start_session(customer="nutraceutics")


def main(user_email):

    #config = get_config()
    # Uloží data za posledních days_to_load dní do blob storage v surové podobě a do stage MSSQL databáze
    google_ads.process_google_ads_data_to_stage(
        customer="nutraceutics", entity="campaign", date_from=date_from, date_to=date_to, user_email=user_email)
    # google_ads.process_google_ads_data_to_stage(
    #    customer="nutraceutics", entity="ad_group_ad", date_from=date_from, date_to=date_to, config=config)

    # facebook.process_facebook_data_to_stage(
    #    customer="nutraceutics", entity="campaigns", date_from=date_from, date_to=date_to, config=config)
    # dv360.process_dv360_data_to_stage(
    #    customer="nutraceutics", entity="ads", date_from=date_from, date_to=date_to, config=config)


# if __name__ == "__main__":
# main()  # sys.argv[1])
