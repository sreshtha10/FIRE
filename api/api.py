from fastapi import FastAPI, HTTPException
import dotenv
import os
from pydantic import BaseModel

dotenv.load_dotenv()

fi_base_url = os.getenv("FI_BASE_URL")
re_base_url = os.getenv("RE_BASE_URL")

app = FastAPI()

class RequestedFix(BaseModel):
    file_url:str
    github_token:str

class RequestedReview(BaseModel):
    pr_url:str
    github_token:str    

class RequestedFIRE(BaseModel):
    repo_url:str
    github_token:str
    scrutiny: int

@app.post('/fix')
async def fix(data:RequestedFix):
    pass

@app.post('/review')
async def review(data:RequestedReview):
    pass

@app.post('/fire')
async def fire(data:RequestedFIRE):
    pass

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port="8080")