from fastapi.security import OAuth2PasswordBearer
from uvicorn import logging

from admin.tools import *
import zipfile
from io import BytesIO
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, HTTPException
import json
from datetime import datetime, timedelta
import jwt

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def token_verify(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Incorrect token")
    username = payload["username"]
    if username not in ADMIM_credentials:
        raise HTTPException(status_code=401, detail="Incorrect token")
    return True


# admin login
@router.post('/login', tags=["admin"])
async def login(username: str, password: str):
    if username in ADMIM_credentials and password == ADMIM_credentials[username]:
        user_data = {"username": username, "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)}
        # expiration_time = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
        token = jwt.encode(user_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        # Return the token to the user
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")


@router.get("/test", tags=["admin"])
async def test():
    return {"message": "test"}


@router.get("/disk_space", tags=["admin"])
async def space_available(token: str):
    try:
        token_verify(token)
    except Exception as e:
        return e
    return {"space_available": disk_space()}


@router.get("/mongodb/ping")
async def ping_mongodb(token: str):
    try:
        token_verify(token)
    except Exception as e:
        return e
    return mongodb_ping()


@router.post("/category/create", tags=["admin"])
async def create_category(category: str, token: str):
    try:
        token_verify(token)
    except Exception as e:
        return e
    return category_creator(category)


@router.post("/category/delete", tags=["admin"])
async def delete_category(category: str, token: str):
    try:
        token_verify(token)
    except Exception as e:
        return e
    return category_deleter(category)


@router.post("/filter/delete", tags=["admin"])
async def delete_filter(timestamp: str, token: str):
    try:
        token_verify(token)
    except Exception as e:
        return e
    date_entry = timestamp.split("-")
    timestamp = datetime.datetime(int(date_entry[0]), int(date_entry[1]), int(date_entry[2]))
    return filter_deleter(timestamp)


@router.get("/mongodb/ping", tags=["admin"])
async def ping_mongodb(token: str):
    try:
        token_verify(token)
    except Exception as e:
        return e
    return mongodb_ping()


@router.post("/logs/", tags=["admin"])
async def get_logs(timestamp: str, token: str):
    try:
        token_verify(token)
    except Exception as e:
        return e
    filelist = []
    log_files_location = os.path.join(data_directory, logs_directory, timestamp)
    for file in os.listdir(log_files_location):
        filelist.append(log_files_location + "/" + file)
    return zip_files(filelist, timestamp)


# This function will serve a ZIP folder for a list of files
def zip_files(file_list, timestamp):
    try:
        io = BytesIO()
        zip_sub_dir = "final_archive"
        zip_filename = "%s.zip" % ("logs_" + timestamp)
        with zipfile.ZipFile(io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip:
            for fpath in file_list:
                file_name = fpath.rsplit('/', 1)[1]
                zip.write(fpath, file_name)
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
