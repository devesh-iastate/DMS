import pymongo
import os

# Credentials for connecting to database

client = pymongo.MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000"
                             "&appName=mongosh+1.6.1")
userDataDB = client["userData"]
fileDataDB = client["dataManagementSystem"]
filterColl = userDataDB["filters"]
systemDB = client["systemDB"]
categoryCollection = systemDB["categories"]

# location of directories

# It contains all the data
data_directory = "/Data/"

# Location of directory inside data directory containing all the data sets
category_directory = "Categories/"

# Stores pointers for number of ids, used while creating new filters
pointers_directory = "pointers/"

# Location of directory inside data directory containing temporary files generated during zipping and uploading
temp_directory = "temp/"