import git
import os
import shutil
import string
import random
import requests
import json
import sys

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# Variables
OPEN_AI_KEY = sys.argv[1]

newbranch = 'fix-branch-' + id_generator()

username = 'amsilf'
repo_name = 'sc-helm-app'
git_token = sys.argv[2]

repo = f'https://amsilf:{git_token}@github.com/amsilf/sc-helm-app.git'

violation_reason = "{\"result\":[{\"expressions\":[{\"value\":{\"play\":{\"deny\":[\"The number of replicas should be larger than2.Thecurrentnumberis1\"],\"number_of_replicas\":2}},\"text\":\"data\",\"location\":{\"row\":1,\"col\":1}}]}]}"
technology = "helm"

template = """  
    Fix the original code based on the violation output.

    The violation output is {reason}
    The targetr language is {tech}
    The original code is {source_code}

    Start the solution with a brief comment about the request.
    DO NOT output file extension at the beginning of the output.
    Output only the solution without any extra words. Output only a valud yaml, HCL, or Docker depends on a selected {tech}.
"""

def propose_the_fix_solution(violation_reason, technology, code):
    try:
        prompt = PromptTemplate.from_template(template)
        llm = ChatOpenAI(openai_api_key=OPEN_AI_KEY, model = "gpt-4o")
        output_parser = StrOutputParser()

        chain = prompt | llm | output_parser
        response = chain.invoke({ "reason": violation_reason, "tech": technology, "source_code": code })
        return response.replace('`', '')
    except Exception as e:
        print(f"An error occurred: {e}")       

def fix_violation(violation_path, violation_reason, technology):
    code = ""
    with open(violation_path) as f: code = f.read()
    solution = propose_the_fix_solution(violation_reason, technology, code)

    f_with_violation = open(violation_path, "w")
    f_with_violation.write(solution)
    f_with_violation.close()

    return

def checkout_and_create_branch(repo, newbranch, local_repo):
    if os.path.isdir(local_repo):
        shutil.rmtree(local_repo)

    repo = git.Repo.clone_from(repo, local_repo)
    repo.git.checkout('-b', newbranch)

    return repo

def push_changes(repo):
    try:       
        if repo.head.is_detached:
            repo.head.reset('HEAD')

        repo.git.add(update=True)
        repo.index.commit("Attempt to fix a violation")

        current_branch = repo.active_branch.name

        origin = repo.remote(name='origin')
        origin.push(current_branch)
    except Exception as e:
        print(f"An error occurred: {e}")

def create_pr(username, repo_name, newbranch, git_token):
    """Creates the pull request for the head_branch against the base_branch"""
    git_pulls_api = "https://api.github.com/repos/{0}/{1}/pulls".format(username, repo_name)
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer {0}".format(git_token),
        "X-GitHub-Api-Version": "2022-11-28"
    }

    payload = {
        "title": 'Compliance violation fix - ' + id_generator(),
        "body": 'An attempt to fix a compliance violation',
        "head": newbranch,
        "base": 'main',
    }

    r = requests.post(
        git_pulls_api,
        headers=headers,
        data=json.dumps(payload))

    if not r.ok:
        print("Request Failed: {0}".format(r.text))

def fix_misconfigurations(repo_path, newbranch, violation_path, violation_reason, technology, username, repo_name, git_token, local_repo="./tmp"):
    repo = checkout_and_create_branch(repo_path, newbranch, local_repo)
    fix_violation(local_repo + "/" + violation_path, violation_reason, technology)
    push_changes(repo)
    create_pr(username, repo_name, newbranch, git_token)
    
fix_misconfigurations(repo, newbranch, "sc-helm-chart/values.yaml", violation_reason, technology, username, repo_name, git_token)