from admin.config import *
import psutil
import os
import datetime

mounted_folder = testSystem


def disk_space():
    # Get the disk usage statistics
    disk_usage = psutil.disk_usage(mounted_folder)

    # Print the available space in GB
    available_gb = disk_usage.free / (1024.0 ** 3)
    return available_gb


def mongodb_ping():
    try:
        client.admin.command('ping')
        return {"message": "MongoDB server is running"}
    except:
        return {"message": "MongoDB server is not available"}


# Creates category. Takes string as input. Checks if category exists. Creates a table with the same name in
# database and folder with the same name in the category folder.
def category_creator(category):
    # Checking if folder for the provided category/data set exists
    category_exists = os.path.exists(data_directory + category_directory + category)
    if category_exists:
        return 412, "Category already exists"
    fileDataDB.create_collection(category)
    os.mkdir(data_directory + category_directory + category)
    return "Category created"


def category_deleter(category):
    folder_path = data_directory + category_directory + category
    category_exists = os.path.exists(folder_path)
    if not category_exists:
        return 412, "Category does not exist"
    try:
        os.system(f'rm -rf {folder_path}')
        fileDataDB.drop_collection(category)
        return "Category deleted"
    except:
        print(f"Error deleting category.")


def filter_deleter(timestamp: datetime.datetime):
    result = filterColl.delete_many({"timestamp": {'$lt': timestamp}})
    return f"Deleted {result.deleted_count} documents."


# filter_deleter(datetime.datetime(2024, 2, 2))
