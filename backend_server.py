######################################################################################################################
#-------------------------------------------------BACKEND SERVER-----------------------------------------------------#
######################################################################################################################
from embed import embed
from query import query
from fastapi import FastAPI
import uvicorn
backend_server = FastAPI()

@backend_server.post("/chatbot")
async def chatbot(payload: dict):
# Your chatbot logic goes here
    print(payload["collection_name"])
    response = query(payload)
    return {"response": response}
 
@backend_server.get("/")
async def read_root():
    return {"Hello": "World"}


config = uvicorn.Config(backend_server, host="0.0.0.0", port=5555, log_level="info", reload=True)
server = uvicorn.Server(config)
server.run()
