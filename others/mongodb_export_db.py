from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json

url = 'mongodb+srv://access:c4NEuKn8FOg8KH2x@cluster0.dsq15p4.mongodb.net/?retryWrites=true&w=majority'

mongoclient = MongoClient(url, server_api=ServerApi('1'))
db = mongoclient["collection"]
collection = db["blacklist"]

documents = collection.find()

data = []

for document in documents:
    document['_id'] = str(document['_id'])
    data.append(document)

output_file = 'output.json'

with open(output_file, 'w') as f:
    json.dump(data, f)

mongoclient.close()
