import pymssql
import time
import logging
import config_keyvault as kv


class LogDBHandler(logging.Handler):

    def __init__(self, sql_conn, sql_cursor, db_tbl_log, session):
        logging.Handler.__init__(self)
        self.sql_cursor = sql_cursor
        self.sql_conn = sql_conn
        self.db_tbl_log = db_tbl_log
        self.session = session

    def emit(self, record):
        # Set current time
        tm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        # Clear the log message so it can be put to db via sql (escape quotes)
        self.log_msg = record.msg
        self.log_msg = self.log_msg.strip()
        self.log_msg = self.log_msg.replace('\'', '\'\'')
        self.log_msg_splitted = self.log_msg.split("::")
        self.customer = self.log_msg_splitted[0]
        self.entity = self.log_msg_splitted[1]
        self.datasource = self.log_msg_splitted[2]
        self.id_msg = self.log_msg_splitted[3]
        self.file_size = self.log_msg_splitted[4]
        self.n_rows = self.log_msg_splitted[5]
        self.duration = self.log_msg_splitted[6]
        self.msg = self.log_msg_splitted[7][:100]

        if self.file_size == 'None':
            file_size_str = 'Null' + ', '
        else:
            file_size_str = 'cast(\'' + \
                str(self.file_size) + '\' as numeric), '

        if self.n_rows == 'None':
            n_rows_str = 'Null' + ', '
        else:
            n_rows_str = 'cast(\'' + str(self.n_rows) + '\' as numeric), '

        if self.duration == 'None':
            duration_str = 'Null' + ', '
        else:
            duration_str = 'cast(\'' + str(self.duration) + '\' as int), '

        # Make the SQL insert
        sql = 'INSERT INTO ' + self.db_tbl_log + ' (log_level, ' + \
            'log_levelname, session, customer, entity, datasource, id_msg, duration, file_size, n_rows, log, created_at, created_by) ' + \
            'VALUES (' + \
            '' + str(record.levelno) + ', ' + \
            '\'' + str(record.levelname) + '\',cast(' + \
            '\'' + str(self.session) + '\' as int), ' + \
            '\'' + str(self.customer) + '\', ' + \
            '\'' + str(self.entity) + '\', ' + \
            '\'' + str(self.datasource) + '\', cast(' + \
            '\'' + str(self.id_msg) + '\' as int), ' + \
            str(duration_str) + str(file_size_str) + str(n_rows_str) + \
            '\'' + str(self.msg) + '\', ' + \
            '(convert(datetime2(7), \'' + tm + '\')), ' + \
            '\'' + str(record.name) + '\')'
        try:
            self.sql_cursor.execute(sql)
            self.sql_conn.commit()
        # If error - print it out on screen. Since DB is not working - there's
        # no point making a log about it to the database :)
        except pymssql.Error as e:
            print('CRITICAL DB ERROR! Logging to database not possible!')


db_server = 'baseadpoint.database.windows.net'
db_user = 'adpoint'
db_password = kv.get_secret_value("MsSqlPassword")
db_dbname = 'nutraceutics_extractors'
db_tbl_log = 'meta.ExtractorLog'

log_error_level = 'INFO'       # LOG error level (file)
log_to_db = True                    # LOG to database?

# Main settings for the database logging use
if (log_to_db):
    # Make the connection to database for the logger
    log_conn = pymssql.connect(db_server, db_user, db_password, db_dbname, 30)
    log_cursor = log_conn.cursor()

    sql = 'Select coalesce(max(session),0) + 1 from [meta].[ExtractorLog]'

    log_cursor.execute(sql)
    session = log_cursor.fetchone()

    logdb = LogDBHandler(log_conn, log_cursor, db_tbl_log, session=session[0])

# Set db handler for root logger
if (log_to_db):
    logging.getLogger('Adpoint_logger').addHandler(logdb)
# Register MY_LOGGER
log = logging.getLogger('Adpoint_logger')
log.setLevel(log_error_level)

log.info("{}::{}::""::0::{}::{}::{}::Session init".format(
    "nutraceutics", "", None, None, None))

# Example variable
#test_var = 'This is test message'

# Log the variable contents as an error
#log.error('This error occurred: %s' % test_var)
