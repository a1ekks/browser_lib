import uvicorn
from config import app_host, app_port


if __name__ == '__main__':
    uvicorn.run("app:api", host=app_host, port=app_port, workers=4, reload=True)
