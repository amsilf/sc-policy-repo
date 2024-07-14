import git
import os
import shutil
import string
import random
import requests
import json

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def fix_violation(violation_path, violation_reason):
    f_with_violation = open(violation_path, "a")
    # FIXME: ask ChatGPT about the fix
    f_with_violation.write(id_generator())
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
        "title": 'Compliance violation fix',
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

def fix_misconfigurations(repo_path, newbranch, violation_path, violation_reason, username, repo_name, git_token, local_repo="./test"):
    repo = checkout_and_create_branch(repo_path, newbranch, local_repo)
    fix_violation(local_repo + "/" + violation_path, violation_reason)
    push_changes(repo)
    create_pr(username, repo_name, newbranch, git_token)

def main():
    repo = ''
    newbranch = ''

    username = ''
    repo_name = ''
    git_token = ''

    fix_misconfigurations(repo, newbranch, "", "", username, repo_name, git_token)

    return

if __name__=="__main__": 
    main() 