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
drugs= db.drugs

# with open('../data/drugs.json', 'r') as outfile:
#     data = json.load(outfile)['drugs']
#     [drugs.insert({
#     'id':str(uuid.uuid1()) ,
#     'generic_name':dr,
#     'adverse_reactions':"",
#     'description': "" }) for dr in data]
# drugs.find()

#
# with open('../data/drug-label-0001-of-0008.json', 'r') as outfile:
#     data = json.load(outfile)['results']
#     [drugs.insert({'id': med['id'],
#       'generic_name': med['openfda']['brand_name'][0],
#       'adverse_reactions': "",
#       'description': ""}) for
#      med in data if med['openfda']]
    # [drugs.insert({ 'id':str(uuid.uuid1())[:6] , 'generic_name':dr, 'description': "" }) for dr in data]

# drugs.find()

drugsstems= db.drugsstems
with open('../data/drugNameStems.json', 'r') as outfile:
    data = json.load(outfile)['stems']
    [drugsstems.insert({'id':str(uuid.uuid1())[:8],
                        'stem': stem})
     for stem in data]
drugsstems.find()


