import os
import pymysql
import requests
import pandas as pd

from main import HOST_NAME, db_user, db_password, db_name, db_table_name

connection = pymysql.connect(
    host=HOST_NAME,
    user=db_user,
    password=db_password,
    database=db_name
)

try:
    with connection.cursor() as cursor:
        sql = f"SELECT * FROM {db_table_name}"
        cursor.execute(sql)
        
        results = cursor.fetchall()
        
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
        df.to_csv('out.csv')
finally:
    connection.close()