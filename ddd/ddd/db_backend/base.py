import os
import struct
from datetime import datetime, timedelta, timezone as dt_timezone
import pyodbc
import mssql.base


def handle_datetimeoffset(dto_value):
    # Raw bytes from SQL Server for datetimeoffset
    tup = struct.unpack("<6hI2h", dto_value)
    return datetime(
        tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6] // 1000,
        dt_timezone(timedelta(hours=tup[7], minutes=tup[8]))
    )


class DatabaseWrapper(mssql.base.DatabaseWrapper):
    def get_new_connection(self, conn_params):
        connection_string = os.environ.get('DB_CONN_STR')
        conn = pyodbc.connect(connection_string)
        conn.add_output_converter(-155, handle_datetimeoffset)  # SQL_SS_TIMESTAMPOFFSET
        return conn