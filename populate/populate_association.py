from pymongo import MongoClient
import json
import uuid
from pprint import pprint

client = MongoClient()
db=client.biomedicalrelation

association= db.association
documents= db.documents

drugs= db.drugs



[doc for doc in documents.find({'annotations.diseases': "hypoplasia"},{"_id":False})]
[doc for doc in documents.find({'annotations.diseases': {"$regex":"immuno"}},{"_id":False})]

[doc['annotations'] for doc in documents.find({"$or":[
    {'annotations.diseases': {"$regex":"glycoprotein"}},
    {'annotations.chemicals': {"$regex":"water"}},
    {'annotations.organisms': {"$regex":"zika"}},
]},{"_id":False})]

[doc['annotations'] for doc in documents.find(
    {'annotations.chemicals': {"$regex":"glycopro"}},
{"_id":False})]


[doc for doc in documents.find({},{"_id":False})]
[doc['annotations'] for doc in documents.find({},{"_id":False})]

list(drugs.find({'generic_name':{'$regex':'Acetamino'}},{"_id":False}))