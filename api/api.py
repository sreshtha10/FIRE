from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os 
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scripts.github import copy_file_contents, create_pr, get_pr_details, post_pr_review
from fi_agent.agent import invoke_agent
from re_agent.reviewer import invoke_reviewer
import logging

logging.basicConfig(filename="../logs/api.log", format='%(asctime)s %(message)s', filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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
            logging.info("##Pulling file from github failed")
            raise HTTPException(status_code=500, detail="Could not read the file contents. Ensure the token is valid and with the necessary access")

        logging.info('#Pulled file from github')
        result = invoke_agent(file_contents=file_contents)

        if not result:
            logging.info('###Agent failed to process the file contents')
            raise HTTPException(status_code=500,detail="Agent failed to analyze the code")

        logging.info('#Agent generated the response')
        has_solution,solution = result

        if has_solution == False:
            logging.info('#No code changes recommeded by agent')
            return {
                "has_solution": has_solution,
                "solution": "No improvements needed in your code."
            }
        
        logging.info("#Author doesn't know how to code lol...agent has recommeded some changes")
        pr_result = await create_pr(modified_code=solution, file_url=file_url, github_token=github_token)
        if not pr_result:
            logging.info('#PR creation failed.')
            raise HTTPException(
                status_code=500,
                detail="Failed to create pull request. Please check the file URL and GitHub token permissions."
            )
        
        logging.info('#Successfully created PR..GG')

        return {
            "has_solution": has_solution,
            "solution": solution,
            "pr_url": pr_result['html_url']
        }

    except HTTPException as he:
        # Re-raise HTTP exceptions as-is
        raise he
    except Exception as e:
        # Convert other exceptions to HTTPException with proper message
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post('/review')
async def review(data:RequestedReview):
    try:
        pr_url = data.pr_url
        github_token = data.github_token

        reviewer_input = await get_pr_details(github_token=github_token, pr_url=pr_url)

        if not reviewer_input:
            raise HTTPException(
                    status_code=500,
                    detail="Failed to pull PR details. Ensure the token and its permissions are valid."
                )

        review_comments = invoke_reviewer(reviewer_input=reviewer_input)

        response = await post_pr_review(review_comments)

        if not response:
            raise HTTPException(
                status_code=500,
                detail="Failed to post review comments. Ensure the token and its permissions are valid."
            )
        
        return {
            "review_comments":review_comments
        }

    except HTTPException as he:
        raise he
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    

@app.post('/fire')
async def fire(data:RequestedFIRE):
    pass

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port="8080")