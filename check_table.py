import os
import pymysql
import requests
import pandas as pd

db_user = os.environ.get('CLOUD_SQL_USERNAME', 'root')
db_password = os.environ.get('CLOUD_SQL_PASSWORD', 'user-study-wacv-888')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME', 'userstudy_results')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
HOST_NAME = '34.42.129.192'

connection = pymysql.connect(
    host=HOST_NAME,
    user=db_user,
    password=db_password,
    database=db_name
)

try:
    with connection.cursor() as cursor:
        sql = "SELECT * FROM userstudy"
        cursor.execute(sql)
        
        results = cursor.fetchall()
        
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
        print(df)
finally:
    connection.close()