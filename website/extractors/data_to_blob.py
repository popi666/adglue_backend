import configurator as conf
from azure.storage import blob
from azure.storage.blob import BlobClient
import config_keyvault as kv

def save_data_to_blob(customer, data, blob_name):
    account_url = conf.get_parameter(customer, "target", "blob", "account_url")
    container_name = conf.get_parameter(customer, "target", "blob", "container_name")
    credential = kv.get_secret_value("BlobCredential")
    blob = BlobClient(
        account_url=account_url,
        container_name=container_name,
        blob_name=blob_name,
        credential=credential)

    blob.upload_blob(data)
