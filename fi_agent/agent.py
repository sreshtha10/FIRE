from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate

def setup_agent():
    try:
        llm = ChatOllama(model="deepseek-coder-v2:latest")

        prompt = PromptTemplate(
            input_variables=["file_contents"],
            template=
            """
            You are a Senior Software Developer. Given the file contents below:
            {file_contents}
            1. Analyze the file and find some potential bugs or issues.
            2. Propose and rewrite the affected file with a clear solution
            3. Stop after providing a clear solution.

            IMPORTANT: In your response if you can't find the solution with high confidence then return False at first line. If there is a potential rewrite then return True in the first line following the code from second line.
            """
        )

        def analyze_code(file_contents:str):
            formatted_prompt = prompt.format(file_contents=file_contents)
            response = llm.invoke(formatted_prompt)
            return response.content
        
        return analyze_code
    except:
        return None
    



def process_agent_response(response:str) -> tuple[bool,str]:
    try:
        lines = response.strip().split('\n')
        has_solution = lines[0].strip().lower() == 'true'
        solution = '\n'.join(lines[1:]).strip()
        return has_solution,solution
    except:
        return False,""
    

def invoke_agent(file_contents:str):
    analyzer = setup_agent()
    if analyzer:
        response = analyzer(file_contents=file_contents)
        return process_agent_response(response=response)
    else:
        return None