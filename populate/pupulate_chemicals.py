from pymongo import MongoClient
import json
import uuid
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient()
db=client.biomedicalrelation
# Issue the serverStatus command and print the results
# serverStatusResult=db.command("serverStatus")
# pprint(serverStatusResult)
diseases= db.diseases
# with open('../data/diseases.json', 'r') as outfile:
#     data = json.load(outfile)['diseases']
#     [diseases.insert({'name':disease[1],
#                      'alternative':disease[0],
#                      'description':disease[2]})
#      for disease in data if len(disease)>2]
# diseases.find()


with open('../data/diagnoses.json', 'r') as outfile:
    data = json.load(outfile)['codes']

diseases.find()