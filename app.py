from urllib.request import Request
from loguru import logger

import uvicorn
from fastapi import FastAPI, responses, HTTPException
from logger_decorator import logger_decorator, Ctx, set_request_id, get_request_id_


app = FastAPI()



@app.middleware("http")
async def log_request(request: Request, call_next):
    set_request_id()  # инициализируем request_id
    response: responses.StreamingResponse = await call_next(request)
    return response

@logger_decorator()
def q():
    logger.info(f"request_id A {get_request_id_()}")
    return 'a'

@app.get('/')
@logger_decorator()
async def a():
    print('request_id!!!', get_request_id_())
    logger.info(f"request_id {get_request_id_()}")
    x = True
    q()
    if x:
        raise HTTPException(status_code=400, detail="X-Token header invalid")

    return 'ok'

if __name__ == '__main__':
    uvicorn.run(app=app, port=8087)