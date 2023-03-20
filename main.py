from fastapi import FastAPI
import uvicorn
from v1.routes import router as v1router
from v2.routes import router as v2router
from admin.routes import router as adminrouter
# import logging.config
#
# # setup loggers
# logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
#
# # get root logger
# logger = logging.getLogger(__name__)  # the __name__ resolve to "main" since we are at the root of the project.
#                                       # This will get the root logger since no logger in the configuration has this name.

# from v2.routes import router as v2router
app = FastAPI()



# Creates versioning of API endpoints
app.include_router(v1router, tags=["data_management"], prefix="/v1")
app.include_router(v2router, tags=["data_management"], prefix="/v2")
app.include_router(adminrouter, tags=["data_management"], prefix="/v1/admin")

if __name__ == '__main__':
    # cwd = pathlib.Path(__file__).parent.resolve()  .. log_config=f"{cwd}/log.ini"
    # app.run()
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True, )
