
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


print(get_target_object("table", "campaign", "google_ads"))
