from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os 
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scripts.github import copy_file_contents, create_pr
from fi_agent.agent import invoke_agent

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
    try:

        file_url = data.file_url
        github_token = data.github_token
        file_contents = copy_file_contents(file_url=file_url, github_token=github_token)

        if not file_contents:
            raise HTTPException(status_code=500, detail="Could not read the file contents. Ensure the token is valid and with the necessary access")

        result = invoke_agent(file_contents=file_contents)

        if not result:
            raise HTTPException(status_code=500,detail="Agent failed to analyze the code")

        has_solution,solution = result

        if has_solution == False:
            return {
                "has_solution": has_solution,
                "solution": "No improvements needed in your code."
            }
        else:
            create_pr(modified_code=solution, github_token=github_token)
            return {
                "has_solution": has_solution,
                "solution": solution
            }
    except Exception as e:
        raise HTTPException(status_code=500,detail=e)


@app.post('/review')
async def review(data:RequestedReview):
    pass

@app.post('/fire')
async def fire(data:RequestedFIRE):
    pass

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port="8080")