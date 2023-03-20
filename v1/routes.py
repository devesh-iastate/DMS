import json
from v1.filemanager import *
import zipfile
from io import BytesIO
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, HTTPException
from v1.models import *
import logging
from v1.config import *


logging.basicConfig(filename='../data.log', filemode='w', format='%(asctime)s;%(name)s;%(levelname)s;%(message)s')
router = APIRouter()


# This function will create filter for the user
@router.post('/filter', tags=["stable"])
async def create_filter(item: Filter):
    # input_json = json.loads(input_json)
    try:
        category = item.category_id
        train_size = item.train_size
        sample_size = item.sample_size
        test_size = item.test_size
        validation_size = item.validation_size
        user = item.user
        code, response = filter_creator(category, train_size, test_size, validation_size, sample_size, user)
        if type(code) == int:
            logging.warning(" Error in creating filter for user: " + user + " with error code: " + str(
                code) + " and error message: " + response)
            raise HTTPException(status_code=code, detail=response)
        return response
    except Exception as e:
        logging.warning(e)
        return e


# This endpoint will fetch the list of the users who created filters
@router.get('/fetch/users', tags=["stable"])
async def fetch_users():
    try:
        return list_users()
    except Exception as e:
        logging.warning(e)
        return e


# This endpoint will fetch list of filter ids for a user
@router.post('/fetch/ids', tags=["stable"])
async def fetch_ids(item: User):
    # input_json = json.loads(input_json)
    user_name = item.username
    # return user_name
    return list_ids(user_name)


# This endpoint will zip file for a filter id
@router.post("/fetch/data", tags=["stable"])
async def image_from_id_meta(item: DataFilter):
    try:
        filter_id = item.filter_id
        data_type = item.data_type
        fetch_meta_data = item.fetch_meta_data
        # Get filenames from the database
        file_list, meta_data = files_aggregator(filter_id, data_type, fetch_meta_data)
        # If file list type is string, then it is error message from backend
        if type(file_list) == int:
            logging.warning(" Error in fetching data for filter id: " + str(filter_id) + " with error code: " + str(
                file_list) + " and error message: " + meta_data)
            raise HTTPException(status_code=file_list, detail=meta_data)

        # meta_data = {"key": "value"}
        return zip_files(file_list, meta_data, filter_id)
    except Exception as e:
        logging.warning(e)
        return e


# This function will serve a ZIP folder for a list of files
def zip_files(file_list, meta_data, filter_id):
    try:
        io = BytesIO()
        zip_sub_dir = "final_archive"
        zip_filename = "%s.zip" % (zip_sub_dir + str(filter_id))
        with zipfile.ZipFile(io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip:
            for fpath in file_list:
                file_name = fpath.rsplit('/', 1)[1]
                zip.write(fpath, file_name)
            if type(meta_data) != bool:
                if os.path.exists("meta_data.txt"):
                    os.remove("meta_data.txt")
                with open('meta_data.txt', 'w') as meta_file:
                    meta_file.write(json.dumps(meta_data))
                zip.write("meta_data.txt")
            # close zip
            zip.close()
        return StreamingResponse(
            iter([io.getvalue()]),
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": f"attachment;filename=%s" % zip_filename}
        )
    except Exception as e:
        logging.warning(e)
        return e


# This endpoint will provide the list of datasets and number of files in it
@router.get('/categories/list', tags=["stable"])
async def categories():
    try:
        code, response = list_categories()
        if type(code) == int:
            logging.warning(
                " Error in fetching categories with error code: " + str(code) + " and error message: " + response)
            raise HTTPException(status_code=code, detail=response)
        return response
    except Exception as e:
        logging.warning(e)
        return e

# @router.post('/categories/search')
# async def categories(item: SearchParameters):
#     category_name = item.category_name
#     return filter_categories(category_name)


# This endpoint will initiate a new dataset
# @router.post('/categories/create')
# async def category_creator(item: DataCategory):
#     category = item.category_name
#     create_category(category)
#     return "Done"


# @app.route('/upload', methods=['POST'])
# def uploader():
#     if 'file' not in request.files:
#         resp = jsonify({'message': 'No file part in the request'})
#         resp.status_code = 400
#         return resp
#     file = request.files['file']
#     if file.filename == '':
#         resp = jsonify({'message': 'No file selected for uploading'})
#         resp.status_code = 400
#         return resp
#     fname = file.filename
#     category = fname.split('@')[0]
#     id = fname.split('@', 2)[1]
#     name = fname.split('@', 2)[2]
#     path = os.path.join(data_directory, temp_directory, name)
#     file.save(path)
#     if name.rsplit('.', 1)[1] == "zip":
#         return bulk_uploader(path, category)
#     return file_uploader(path, id, category)
