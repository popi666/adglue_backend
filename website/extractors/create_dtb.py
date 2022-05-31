from os import environ as env
from azure.identity import ClientSecretCredential
#from azure.keyvault.secrets import SecretClient
#from azure.identity import DefaultAzureCredential
from azure.mgmt.resource.resources import ResourceManagementClient
import azure.mgmt.sql
#import SqlManagementClient
# env variables (uložené credentials z AZURE Service Principal Application)
TENANT_ID = '32b05504-4594-4ff6-b8b4-2df23b2abadd'
CLIENT_ID = 'c2d21787-a0b7-4272-8cfc-1cc7c03c68d4'
CLIENT_SECRET = '1nbs5NBD7-r8I1AqPaFBq5S--3SgdESnFt'
#CLIENT_SECRET = 'Qepma6-jajxev-pejgak'
subscription = "90227f4e-d86e-4cb4-93bf-cdd0611978ee"


credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
resource_client = ResourceManagementClient(credential, subscription)
sql_client = azure.mgmt.sql.SqlManagementClient(credential, subscription)
# resource_client.providers.register('Microsoft.Sql')
#a = sql_client.servers.list()
# print(a)

resource_group_params = {'location': 'West Europe'}
resource_client.resource_groups.create_or_update(
    'janotest', resource_group_params)

server = sql_client.servers.create_or_update(
    'janotest',
    "janotesta",
    {
        'location': 'West Europe',
        'version': '12.0',  # Required for create
        'administrator_login': 'login',  # Required for create
        'administrator_login_password': 'tajneheslo'  # Required for create
    }
)

'''
async_db_create = sql_client.databases.create_or_update(
    'Adpoint',
    'baseadpoint',
    'Jancitestuje',
    {
        'location': 'West Europe'
    }
)
database = async_db_create.result()
'''

# for resource_group in resource_client.resource_groups.list():
#    print(f"Resource group: {resource_group.name}")

#_secret_client = SecretClient(vault_url= KEYVAULT_URI, credential= _credential)

# hodnota pre konkrétny Secret z KeyVault
# def get_secret_value(name):
#    return _secret_client.get_secret(name).value
