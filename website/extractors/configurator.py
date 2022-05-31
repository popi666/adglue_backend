import json
import os
from azure.storage import blob
from azure.storage.blob import BlobClient

from pandas._config import config

config_file = os.path.abspath('') + "\\config.json"
# blob = BlobClient(
#         # account_url="https://baseadpoint.blob.core.windows.net/pythonsrc/config.json?sp=racwdyti&st=2021-12-13T12:45:49Z&se=2021-12-31T21:45:49Z&spr=https&sv=2020-08-04&sr=b&sig=CYSApFlbnOzcpYOfFjiqoVckPNKLunC3tDTgltav808%3D",
#         # container_name="pythonsrc",
#         # blob_name="config.json",
#         # credential="sp=racwdyti&st=2021-12-13T12:45:49Z&se=2021-12-31T21:45:49Z&spr=https&sv=2020-08-04&sr=b&sig=CYSApFlbnOzcpYOfFjiqoVckPNKLunC3tDTgltav808%3D")
#         account_url= "https://baseadpoint.blob.core.windows.net/adpoint?sp=rw&st=2021-10-20T16:30:39Z&se=2021-12-31T01:30:39Z&spr=https&sv=2020-08-04&sr=c&sig=RVRcXoSdSWPd33wlHNmVicbJPZCgrvPm2WeetXoUsHw%3D",
#         container_name= "adpoint",
#         blob_name="nutraceutics/google_ads/2021-11-24/35cDS2QK8M21gDh4LzOIYA.json",
#         credential= "sp=rw&st=2021-10-20T16:30:39Z&se=2021-12-31T01:30:39Z&spr=https&sv=2020-08-04&sr=c&sig=RVRcXoSdSWPd33wlHNmVicbJPZCgrvPm2WeetXoUsHw%3D")

# download_stream = blob.get_blob_properties()

# config_data = blob.download_blob()

'''
Load configuration base on input parameters
'''
def get_parameter(*args):
    with open(config_file) as f:
        data = json.load(f)
        try:
            for x in args:
                data = data[x]
            return(data)
        except:
            raise Exception('Wrong input configuration parameters')

#print(download_stream)

