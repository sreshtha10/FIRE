from langchain_ollama.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
import json
import re

def setup_reviewer():
    try:
        # replace it with the model of your choice like ChatOpenAI if you have $$ lol
        llm = ChatOllama(model="deepseek-coder-v2:latest")

        prompt = PromptTemplate(
            input_variables=["title","description","diff_content","comments"],
            template="""
                You are a Senior Software Engineer assigned to review a Pull Request.

                **PR Details:**
                - Title: {title}
                - Description: {description}
                - Existing Comments: {comments}
                - Diff Content:
                {diff_content}

                Your task is to review the code **thoroughly** and provide feedback based on the following criteria:
                1. **Logical Correctness** - Does the code perform what it's supposed to?
                2. **Code Quality** - Is it clean, readable, and maintainable?
                3. **Potential Bugs** - Any edge cases, regressions, or flaws?

                ### Output Format:
                Respond with a **strict JSON object**. Do not include markdown, explanations, or additional text outside the JSON structure.

                ```json
                {
                "has_comments": true or false,
                "review_comments": [
                    "First comment if needed.",
                    "Second comment if needed."
                ]
                }
            """
        )

        def analyze_code(title, description, diff_content, comments):
            formatted_prompt = prompt.format(title=title, description=description, diff_content=diff_content, comments=comments)
            response = llm.invoke(formatted_prompt)
            return response.content
        
        return analyze_code
    except:
        return None
    


def invoke_reviewer(reviewer_input):
    pass