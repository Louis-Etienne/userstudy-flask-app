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

from flask import Flask
from flask import render_template, request, send_file, send_from_directory, g

import pymysql

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

def secure_filename(filename):
    return filename.replace("/", "_").replace("\\", "_").strip()


app = Flask(__name__)
currentUid = 0

random.seed(42)
listImages = [x[4:] for x in glob("pic/background/*.jpg")]
pairs = [[x, x.replace("background", "distorted")[:-3] + "jpg"] for x in listImages]
sentinel = ["background/sentinel.jpg", "distorted/sentinel.jpg"]

from pprint import pprint
pprint(pairs)

# First shuffling, we will shuffle them again (per user)
random.shuffle(pairs)
for p in pairs:
    if random.random() > 0.5:
        tmp = p[1]
        p[1] = p[0]
        p[0] = tmp

numberOfPairsShown = 54

def connect_to_database():
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        db = pymysql.connect(user=db_user, password=db_password,
                                unix_socket=unix_socket, db=db_name)
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        host = '127.0.0.1'
        db = pymysql.connect(user=db_user, password=db_password,
                                host=host, db=db_name)
    return db

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/", methods=['GET'])
def get_instructions():
    return send_file("instructions.html")

@app.route("/start", methods=['GET'])
def get_study():
    return send_file("layout.html")

@app.route("/pic/<path:filename>", methods=['GET'])
def get_pic(filename):
    return send_from_directory("pic", filename, as_attachment=True)


def getPairAtPos(pos, userid):
    # If not using sentinels
    pairsclone = deepcopy(pairs)[:numberOfPairsShown]

    # If using sentinels
    # pairsclone = deepcopy(pairs)[:numberOfPairsShown-1]
    # pairsclone.append(sentinel)

    random.seed(userid)
    random.shuffle(pairsclone)
    for p in pairsclone:
        if random.random() > 0.5:
            tmp = p[1]
            p[1] = p[0]
            p[0] = tmp
    return pairsclone[pos]

@app.route("/requestInitialData", methods=['GET'])
def reqInitial():
    global currentUid

    currentUid += 1
    firstPair = getPairAtPos(0, currentUid)
    return json.dumps({'myId': currentUid,
                        'pos': 0,
                        'total': numberOfPairsShown,
                        'isLast': False,
                        'imgsrc1': "pic/{}".format(firstPair[0]),
                        'imgsrc2': "pic/{}".format(firstPair[1])})

@app.route("/sendUserChoice", methods=['GET'])
def reqChoice():
    clientId = request.args.get('myid', type=int)
    pos = request.args.get('pos', type=int)
    choice = request.args.get('picked', type=int)

    image1, image2 = getPairAtPos(pos, clientId)

    if "sentinel" in image1:
        cropName = 'sentinel'
    else:
        cropName = image1[-37:-4]

    if "background" in image1:
        image1 = "background"
        image2 = "distorted"
    else:
        image1 = "distorted"
        image2 = "background"

    with get_db().cursor() as cur:
        data = (clientId, datetime.now(), request.remote_addr, cropName, image1, image2, choice)
        cur.execute("INSERT INTO userstudy VALUES ({}, '{}', '{}', '{}', '{}', '{}', {})".format(*data))

    get_db().commit()

    if pos + 1 == numberOfPairsShown:
        return json.dumps({'myId': clientId,
                            'pos': pos + 1,
                            'total': numberOfPairsShown,
                            'isLast': True,
                            'imgsrc1': "pic/blank.png",
                            'imgsrc2': "pic/blank.png"})
    else:
        nextPair = getPairAtPos(pos+1, clientId)
        return json.dumps({'myId': clientId,
                            'pos': pos + 1,
                            'total': numberOfPairsShown,
                            'isLast': False,
                            'imgsrc1': "pic/{}".format(nextPair[0]),
                            'imgsrc2': "pic/{}".format(nextPair[1])})

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
    return r


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web server for the user study')
    parser.add_argument('--port', help='port if using virtual net', type=int, default=8001)
    args = parser.parse_args()

    app.run(host='127.0.0.1', port=args.port, debug=False, use_reloader=False)
