import os
import sys
from glob import glob
import argparse
import json
from datetime import datetime
import base64
import random
import time
from copy import deepcopy

import pymysql

from main import get_db, HOST_NAME, db_user, db_password, db_name
import pandas as pd

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
        technique_confusions = df.groupby('technique_name').apply(lambda group: (group['gt_idx'] != group['choice_idx']).mean())
        technique_confusions = technique_confusions.sort_values(ascending=False)

        print('Technique confusions:')
        print(technique_confusions)

        print('Technique confusions in LaTeX format:')
        print((technique_confusions * 100).to_latex(float_format="{:.1f} \\%".format))

finally:
    connection.close()
