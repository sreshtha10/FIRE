from langchain_ollama.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
import json
import re

def setup_agent():
    try:
        # replace it with the model of your choice like ChatOpenAI if you have $$ lol
        llm = ChatOllama(model="deepseek-coder-v2:latest")

        prompt = PromptTemplate(
            input_variables=["file_contents"],
            template="""
                You are a Senior Software Developer. Given the file contents below:
                {file_contents}

                1. Analyze the file and find potential bugs or issues.
                2. Propose and rewrite the affected file with a clear solution.
                3. Stop after providing a clear solution.

                Output Format (strict JSON object, not a string or markdown block):

                {{
                "has_solution": true or false,
                "solution": [ "line 1 of code", "line 2 of code", ... ]
                }}

                IMPORTANT:
                - Output should be pure JSON, no markdown, no extra text.
                - If you can't confidently find a solution, set "has_solution" to false.
                - Only include the modified full code under "solution" as a list of strings.
            """
        )

        def analyze_code(file_contents:str):
            formatted_prompt = prompt.format(file_contents=file_contents)
            response = llm.invoke(formatted_prompt)
            return response.content
        
        return analyze_code
    except:
        return None
    
def process_agent_response(response: str) -> tuple[bool, str]:
    try:
        # Remove Markdown code block fencing
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip(), flags=re.IGNORECASE | re.MULTILINE)

        # Parse the JSON string
        data = json.loads(cleaned)

        has_solution = data.get("has_solution", False)
        solution_lines = data.get("solution", [])
        solution = "\n".join(solution_lines).strip()

        return has_solution, solution

    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {e}"
    except Exception as e:
        return False, f"Error processing response: {e}"    

def invoke_agent(file_contents:str):
    analyzer = setup_agent()
    if analyzer:
        response = analyzer(file_contents=file_contents)
        print('RAW response',response)
        return process_agent_response(response=response)
    else:
        return None