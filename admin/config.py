import pymongo

# storage server paths
serverMount = "/research/baskar"
testSystem = "/"
ADMIM_credentials = {
    "ronak": "ronakpass",
    "devesh": "deveshpass"
}
# Credentials for connecting to database
client = pymongo.MongoClient("mongodb://localhost:27017/")
userDataDB = client["userData"]
fileDataDB = client["dataManagementSystem"]
filterColl = userDataDB["filters"]
systemDB = client["systemDB"]
categoryCollection = systemDB["categories"]

# location of directories

# It contains all the data
# data_directory = "/Data/"
data_directory = "./../Data/"

# Location of directory inside data directory containing all the logs
logs_directory = "logs/"

# Location of directory inside data directory containing all the data sets
category_directory = "Categories/"


JWT_SECRET_KEY = "backend_story"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_MINUTES = 30