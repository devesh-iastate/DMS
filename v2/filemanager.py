import math
import random
from v2.config import *


# Returns the array of all the available datasets and number of files in each dataset
def list_categories():
    if not os.path.exists(data_directory):
        return "Data directory not reachable"
    datasets = []

    # Iterating through the folder containing all the datasets
    for dataset in os.listdir(data_directory + category_directory):
        dataset_path = os.path.join(data_directory + category_directory, dataset)

        # adding dataset and file count in response array
        if os.path.isdir(dataset_path):
            number_of_files = len(os.listdir(dataset_path))
            datasets.append(dataset + ":" + str(number_of_files))
    return datasets


def filter_categories(category_name):
    cursor = categoryCollection.find({"datasetName": {"$regex": category_name}}, {"_id": 0, "datasetName": 1})
    dataset_list = []
    for doc in cursor:
        dataset_list.append(doc["datasetName"])
    return dataset_list


# Returns the array of all the usernames who have created the filters
def list_users():
    users = list(filterColl.distinct("userName"))
    user_list = []
    for u in users:
        user_list.append(u)
    return user_list


# Returns the array of filter
def list_ids(user_name):
    ids = list(filterColl.find({"userName": user_name}, {"_id": 1}))
    filter_ids = []
    for filter_id in ids:
        filter_ids.append(filter_id["_id"])
    return filter_ids


# Creates filter and returns filter id as integer
def filter_creator(category, train_size, test_size, validation_size, sample_size, user):
    # checking if folder for provided category exists
    category_exists = os.path.exists(data_directory + category_directory + category)
    if not category_exists:
        return "Category not found."

    # checking number of files in the provided category
    count = len(os.listdir(data_directory + category_directory + category))

    # calculating the size of train, test and validation dataset for the function
    train_size = math.floor(count * train_size)
    test_size = math.floor(count * test_size)
    validation_size = math.floor(count * validation_size)
    if train_size + test_size + validation_size > count:
        return "Data size is " + str(count) + ". Please check proportions."

    # finding number of filters generated to generate id for new filter
    with open(data_directory + pointers_directory + 'id_count.txt') as f:
        current_id = f.read()
    new_id = int(current_id) + 1
    with open(data_directory + pointers_directory + 'id_count.txt', 'w') as f:
        f.write(str(new_id))

    # creating random array based on number of files as all the files are named based on incrementing number from 1
    # to n.
    file_array = list(range(1, count + 1))
    random.shuffle(file_array)

    # creating data set for test train  and validation
    train_array = file_array[0: train_size]
    test_array = file_array[train_size:train_size + test_size]
    validation_array = file_array[train_size + test_size: train_size + test_size + validation_size]

    # Inserting new filter to the database
    filterColl.insert_one({"_id": new_id, "dataSize": count, "testList": test_array, "trainList": train_array,
                           "testSize": len(test_array), "trainSize": len(train_array),
                           "validationSize": len(validation_array), "sampleSize": sample_size,
                           "category": category, "userName": user, "trainPointer": 0, "testPointer": 0,
                           "validationPointer": 0, "validationList": validation_array})
    responseDict = {"filter_id":new_id, "dataSize": count, "testSize": len(test_array), "trainSize": len(train_array),
                           "validationSize": len(validation_array), "sampleSize": sample_size}
    return responseDict


# Takes filter id and data_type(test/train) as input. Fetches the name of files in the batch of data and collects it
# from the dataset folder and zips the files and returns the location of the zipped folder that is created.
def files_aggregator(filter_id, data_type, fetch_meta_data):
    # checking what kind of data is required
    if data_type == 'test':
        listType = "testList"
        pointerType = "testPointer"
    elif data_type == 'train':
        listType = "trainList"
        pointerType = "trainPointer"
    elif data_type == 'validation':
        listType = "validationList"
        pointerType = "validationPointer"
    else:
        return "invalid data type. Please enter test/train/validation", "error"
    # obtaining information of filter id from database and validating information
    filter_data = list(filterColl.find({"_id": filter_id}, {"_id": 1, listType: 1, pointerType: 1,
                                                                "sampleSize": 1, "category": 1}))
    if len(filter_data) == 0:
        return "Filter id " + str(filter_id) + " not found", "error"
    filter_list = list(filter_data[0][listType])
    pointer = filter_data[0][pointerType]
    sample_size = filter_data[0]["sampleSize"]
    category = filter_data[0]["category"]
    if not os.path.exists(data_directory):
        return "Data directory not reachable", "error"
    category_folder = os.path.join(data_directory + category_directory, category)
    if not os.path.exists(category_folder):
        return "Category not found", "error"
    # Checking if end of epoch is reached. If yes, then reshuffling the dataset for the particular data type
    if pointer + sample_size > len(filter_list):
        random.shuffle(filter_list)
        # filterColl.update_one({"id": int(filter_id)}, {"$set": {listType: filter_list, pointerType: 0}})
        pointer = 0
    filterColl.update_one({"_id": int(filter_id)}, {"$set": {listType: filter_list, pointerType: pointer + 1}})
    # List of files to be loaded and zipped
    fetch_list = filter_list[pointer: pointer + sample_size]

    # Fetching name of all the files in the folder to fetch its type
    all_file_list = os.listdir(data_directory + category_directory + category)
    file_map = {'-1': 'test'}
    for f in all_file_list:
        curr_name = (f.rsplit('.'))
        if len(curr_name) == 2:
            file_map[curr_name[0]] = curr_name[1]

    # generating file list based on if file is present in the category folder.
    final_file_list = []
    filterColl.update_one({"_id": filter_id}, {"$set": {pointerType: pointer + sample_size}})
    for f in fetch_list:
        if str(f) in file_map:
            curr_file = os.path.join(category_folder + '/' + str(f) + '.' + file_map[str(f)])
            if os.path.exists(curr_file):
                final_file_list.append(curr_file)
    if not fetch_meta_data:
        return final_file_list, False
    meta_data = {}
    # file_ids = fetch_list.map(function(id) {return ObjectID(id); });
    for data in fileDataDB[category].find({"_id": {"$in": fetch_list}}, {"_id": 1, "meta_data": 1}):
        meta_data[data["_id"]] = data["meta_data"]
    return final_file_list, meta_data


# Creates category. Takes string as input. Checks if category exists. Creates a table with the same name in
# database and folder with the same name in the category folder.
def create_category(category):
    # Checking if folder for the provided category/data set exists
    category_exists = os.path.exists(data_directory + category_directory + category)
    if category_exists:
        return "category already exists"
    fileDataDB.create_collection(category)
    os.mkdir(data_directory + category_directory + category)
    return "Category created"
