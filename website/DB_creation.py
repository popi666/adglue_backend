import subprocess
from os import listdir
from os.path import isfile, join

#customer = 'badumts'


def create_db_instance(customer):

    subprocess.call(["C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe",
                     ". \"C:/Users/Uživatel/Desktop/Projects/Adpoint/adpointgit/Back end/website/DB_create_instance\";", "&createDBinstance(\"{}\")".format(customer)])


def orderfunc(file):

    return 'schema' in file


def get_files_path():

    tables = 'DDL\Tables'
    views = 'DDL\Views'

    tablesfiles = [join(tables, f)
                   for f in listdir(tables) if isfile(join(tables, f))]
    viewsfiles = [join(views, f)
                  for f in listdir(views) if isfile(join(views, f))]

    tablesfiles.sort(reverse=True, key=orderfunc)

    files = tablesfiles + viewsfiles

    return files


def load_DDLS(customer, files):

    for file in files:

        subprocess.call(["C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe",
                         ". \"./DB_run_ddls\";", "&load_DDLs \"{}\" \"{}\"".format(customer, file)])


# create_db_instance("testcopy")
#load_DDLS(customer, get_files_path())
