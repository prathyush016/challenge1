import pymongo
import csv
import json
import logging


logging.basicConfig(filename="mongo.log", format='%(asctime)s %(message)s', filemode='w', level=logging.DEBUG)

try:
 client = pymongo.MongoClient("mongodb+srv://prathyush:prathyush@cluster0.s3unoqt.mongodb.net/?retryWrites=true&w=majority")
 db = client.test
 database=client['prathyush']
 collection=database['scrapper']
 collection.drop()
except:
    logging.error(f'error in establishing a connection with Mongo DB Atlas. Details{database}/{collection}')
 

jsonArray = []
rowcount = 0

try:
    with open("course_details.txt", "r") as txt_file:
      csv_reader = csv.DictReader(txt_file, dialect="excel", delimiter="|", quoting=csv.QUOTE_NONE)
      for row in csv_reader:
        rowcount += 1
        jsonArray.append(row)
      for i in range(rowcount):
        jsonString = json.dumps(jsonArray[i], indent=1, separators=(",", ":"))
        jsonfile = json.loads(jsonString)
        try:
            collection.insert(jsonfile, check_keys=False)
        except:
            logging.error(f"not able to insert {jsonString} to Mongo DB")
    print("Finished")
except:
    logging.error(f"Issue pushing the data from {txt_file} to Mongo DB for the collection {collection} at {database}")
