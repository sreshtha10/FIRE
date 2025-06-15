import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from scripts.github import get_pr_details
import asyncio
from re_agent.reviewer import invoke_reviewer

from dotenv import load_dotenv


load_dotenv()

github_token = os.getenv("GITHUB_TOKEN")

re_input = asyncio.run(get_pr_details(pr_url="https://github.com/sreshtha10/Space-Wars/pull/4", github_token=github_token))

# testing reviewer agent
response = invoke_reviewer(reviewer_input=re_input)

print(response)