from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os 
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scripts.github import copy_file_contents, create_pr, get_pr_details, post_pr_review
from fi_agent.agent import invoke_agent
from re_agent.reviewer import invoke_reviewer

app = FastAPI()

class RequestedFix(BaseModel):
    file_url:str
    github_token:str

class RequestedReview(BaseModel):
    pr_url:str
    github_token:str    


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
        
        pr_result = await create_pr(modified_code=solution, file_url=file_url, github_token=github_token)
        if not pr_result:
            raise HTTPException(
                status_code=500,
                detail="Failed to create pull request. Please check the file URL and GitHub token permissions."
            )

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

        has_comments, review_comments, approve = invoke_reviewer(reviewer_input=reviewer_input)
        
        await post_pr_review(github_token=github_token, pr_url=pr_url, comments=review_comments, isApproved=approve)

        return {
            "has_comments":has_comments,
            "review_comments":review_comments,
            "approve":approve
        }

    except HTTPException as he:
        raise he
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    

@app.post('/fire')
async def fire(data: RequestedFix):
    try:
        fix_response = await fix(data)

        pr_url = fix_response.get('pr_url')
        if not pr_url:
            raise HTTPException(status_code=500, detail="PR creation failed, cannot proceed with review.")

        review_request = RequestedReview(pr_url=pr_url, github_token=data.github_token)
        review_response = await review(review_request)

        return {
            "fix": fix_response,
            "review": review_response
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port="8080")