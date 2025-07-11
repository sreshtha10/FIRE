from langchain_ollama.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
import json
import re

class ReviewDataModel:

    def __init__(self, diff_file , title, description, comments):
        self.diff_file = diff_file
        self.title = title
        self.description = description
        self.comments = comments

def setup_reviewer():
    try:
        # replace it with the model of your choice like ChatOpenAI if you have $$ lol
        llm = ChatOllama(model="deepseek-coder-v2:latest")

        prompt = PromptTemplate(
            input_variables=["title","description","diff_content","comments"],
            template="""
                You are a Senior Software Engineer assigned to review a Pull Request.

                PR Details:
                - Title: {title}
                - Description: {description}
                - Existing Comments: {comments}
                - Diff Content:
                {diff_content}

                Your task is to review the code thoroughly and provide feedback based on the following criteria:
                1. Logical Correctness - Does the code perform what it's supposed to?
                2. Code Quality - Is it clean, readable, and maintainable?
                3. Potential Bugs - Any edge cases, regressions, or flaws?

                Output Format (strict JSON object, not a string or markdown block):
                
                {{
                "has_comments": true or false,
                "review_comments": [
                    "First comment if needed.",
                    "Second comment if needed."
                ],
                "approve": true or false based on the review
                }}
            """
        )

        def analyze_code(title, description, diff_content, comments):
            formatted_prompt = prompt.format(title=title, description=description, diff_content=diff_content, comments=comments)
            response = llm.invoke(formatted_prompt)
            return response.content
        
        return analyze_code
    except:
        return None
    

def processed_reviewer_response(response:str):
    # Remove Markdown code block fencing
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip(), flags=re.IGNORECASE | re.MULTILINE)

    # Parse the JSON string
    data = json.loads(cleaned)

    has_comments= data.get('has_comments',False)
    review_comments= data.get('review_comments',[])
    approve=data.get('approve',False)

    return has_comments, review_comments, approve



def invoke_reviewer(reviewer_input:ReviewDataModel):
    try:
            
        analyzer = setup_reviewer()
        if analyzer:
            response = analyzer(
                title=reviewer_input.title, 
                description=reviewer_input.description, 
                diff_content=reviewer_input.diff_file,
                comments=reviewer_input.comments
            )
            
            return processed_reviewer_response(response=response)
        
    except Exception as e:
        return None