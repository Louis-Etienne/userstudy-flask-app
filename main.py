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

db_user = os.environ.get('CLOUD_SQL_USERNAME', 'root')
db_password = os.environ.get('CLOUD_SQL_PASSWORD', 'user-study-wacv-888')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME', 'userstudy_results')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
HOST_NAME = '34.42.129.192'

app = Flask(__name__)
currentUid = 0
random.seed(42)

IMAGE_FOLDER_NAME = 'techniques_png'
GT_FOLDER = 'GT_emission_envmap'
NUMBER_IMAGES_PER_TECHNIQUE = 20

listTechniques = glob(IMAGE_FOLDER_NAME + '/*/')
listTechniques = [x  for x in listTechniques if not GT_FOLDER in x]
number_techniques = len(listTechniques)
total_number_images = NUMBER_IMAGES_PER_TECHNIQUE * number_techniques

GT_ALL_IMAGES = glob(os.path.join(IMAGE_FOLDER_NAME, GT_FOLDER, "*"))
numberOfPairsShown = total_number_images

# from pprint import pprint
# pprint(pairs)



def secure_filename(filename):
    return filename.replace("/", "_").replace("\\", "_").strip()

def connect_to_database():
    host = HOST_NAME
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

@app.route(f"/{IMAGE_FOLDER_NAME}/<path:filename>", methods=['GET'])
def get_pic(filename):
    return send_from_directory(f"{IMAGE_FOLDER_NAME}", filename, as_attachment=True)


def getPairAtPos(pairs, pos, userid):
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

def getRandomPairs(currentUid):
    # Get the pairs
    random.seed(currentUid)
    GT_choice_images = random.sample(GT_ALL_IMAGES, total_number_images)
    random.shuffle(GT_choice_images)
    pairs = []
    for i,technique in enumerate(listTechniques):
        head_technique = technique[len(IMAGE_FOLDER_NAME)+1: -1]
        offset = i * NUMBER_IMAGES_PER_TECHNIQUE
        for j in range(20):
            GT_path = GT_choice_images[offset + j]
            pairs.append([GT_path, GT_path.replace(GT_FOLDER, head_technique)])
    
    # Shuffle the pairs
    random.shuffle(pairs)
    for p in pairs:
        if random.random() > 0.5:
            tmp = p[1]
            p[1] = p[0]
            p[0] = tmp
            
    return pairs

@app.route("/requestInitialData", methods=['GET'])
def reqInitial():
    global currentUid
    currentUid += 1
    
    pairs = getRandomPairs(currentUid)
    
    firstPair = getPairAtPos(pairs, 0, currentUid)
    return json.dumps({'myId': currentUid,
                        'pos': 0,
                        'total': numberOfPairsShown,
                        'isLast': False,
                        'imgsrc1': "{}".format(firstPair[0]),
                        'imgsrc2': "{}".format(firstPair[1]),
                        'pairs': pairs})

@app.route("/sendUserChoice", methods=['GET'])
def reqChoice():
    clientId = request.args.get('myid', type=int)
    pos = request.args.get('pos', type=int)
    choice = request.args.get('picked', type=int)
    pairs = request.args.get('pairs')
    pairs = pairs.split(',')   
    pairs = [[pairs[i], pairs[i+1]] for i,x in enumerate(pairs) if i%2==0]
    image1, image2 = getPairAtPos(pairs, pos, clientId)
    print(pairs)
    split_im1 = image1.split("\\")
    split_im2 = image2.split("\\")
    # For linux path system
    if split_im1[0] == image1:
        split_im1 = image1.split('/')
        split_im2 = image2.split('/')
    crop = split_im1[2][:-4]
    if GT_FOLDER in image1:
        GT_position = 1
        technique_crop = split_im2[1]
    else:
        GT_position = 2
        technique_crop = split_im1[1]

    with get_db().cursor() as cur:
        data = (clientId, datetime.now(), request.remote_addr, GT_position, choice, crop, technique_crop)
        cur.execute("INSERT INTO userstudy VALUES ({}, '{}', '{}', {}, {}, '{}', '{}')".format(*data))

    get_db().commit()

    if pos + 1 == numberOfPairsShown:
        return json.dumps({'myId': clientId,
                            'pos': pos + 1,
                            'total': numberOfPairsShown,
                            'isLast': True,
                            'imgsrc1': f"{IMAGE_FOLDER_NAME}/blank.png",
                            'imgsrc2': f"{IMAGE_FOLDER_NAME}/blank.png",
                            'pairs': pairs})
    else:
        nextPair = getPairAtPos(pairs, pos+1, clientId)
        return json.dumps({'myId': clientId,
                            'pos': pos + 1,
                            'total': numberOfPairsShown,
                            'isLast': False,
                            'imgsrc1': "{}".format(nextPair[0]),
                            'imgsrc2': "{}".format(nextPair[1]),
                            'pairs': pairs})

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
