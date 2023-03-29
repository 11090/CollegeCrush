import json
import os
import csv
import sys
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = "MayankRao16Cornell.edu"
MYSQL_PORT = 3306
MYSQL_DATABASE = "kardashiandb"

mysql_engine = MySQLDatabaseHandler(MYSQL_USER,MYSQL_USER_PASSWORD,MYSQL_PORT,MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

# Sample search, the LIKE operator in this case is hard-coded, 
# but if you decide to use SQLAlchemy ORM framework, 
# there's a much better and cleaner way to do this
def sql_search(episode):
    query_sql = f"""SELECT * FROM episodes WHERE LOWER( title ) LIKE '%%{episode.lower()}%%' limit 10"""
    keys = ["id","title","descr"]
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys,i)) for i in data])

def search_similarity(data, queries, size,region):
    arr = []
    inputs = queries.split(',')
    dic = {}
    region_dic = {}
    region_dic['east'] = set(['WA','OR','ID','MT','WY','CA','NV','UT','AZ','NM','CO'])
    region_dic['midwest'] = set(['ND','SD','NE','KS','MN','IA','MO','WI','IL','IN','MI','IN','OH'])
    region_dic['east'] = set(['PA','NY','NJ','VT','NH','ME','MA','CT','RI'])
    region_dic['south'] = set(['TX','OK','AR','LA','MS','TN','KY','AL','GA', 'FL','WV',
                               'NC','VA','MD','DE','NC','SC'])
    print(inputs, file=sys.stderr)
    for i in inputs:
        if len(i) == 2:
            dic['state'] = i
        else:
            dic['city'] = i
    s = set(['small','medium','large'])
    for colleges in data:
        if (size not in s) or (size == "small" and int(colleges['tot_enroll']) <= 5000) or (size == "medium" and int(colleges['tot_enroll']) <= 15000 and int(colleges['tot_enroll']) >= 5000) or (size == "large" and int(colleges['tot_enroll']) > 15000):
            if 'city' in dic and colleges['city'].lower() == dic['city'].lower() and int(colleges['tot_enroll'])>1000:
                arr.append(({'title': colleges['name'], 'location': colleges['city']+", "+colleges['state'],'enrolled':colleges['tot_enroll'],'website': colleges['website']}))
            if queries.upper() == colleges['state']:
                arr.append(({'title': colleges['name'], 'location': colleges['city']+", "+colleges['state'],'enrolled':colleges['tot_enroll'],'website': colleges['website']}))
    newlist = sorted(arr, key=lambda d: d['title']) 
    return newlist
@app.route("/")
def home():
    return render_template('base.html',title="sample html")

@app.route("/colleges")
def college_search():
    text = request.args.get("title")
    with open('colleges.json','r') as f:
        data = json.load(f)
    data2 = {}
    with open('file.csv', encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            key = rows['No']
            data2[key] = rows
    result = search_similarity(data, text, request.args.get("size"),request.args.get("region"))
    return result

# app.run(debug=True)