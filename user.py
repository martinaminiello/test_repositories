import json
import os
import shutil
import subprocess
import sys
from repo_manager import Repository, FILE_JSON_NAME, onerror

from github import Github, Auth


class User:
    def __init__(self, token):
        self.token = token
        self.auth = Auth.Token(token)
        self.github = Github(auth=self.auth)
        self.user = self.github.get_user()
        self.username = self.user.login
        self.user_url = f"https://github.com/{self.username}/"
        self.user_dir = f"{self.username}_workspace"

        os.makedirs(self.user_dir, exist_ok=True)


    def get_git_remote_url(self, repo_path, repo_name):
        url = f"https://{self.username}:{self.token}@github.com/{self.username}/{repo_name}.git"
        subprocess.run(["git", "remote", "set-url", "origin", url], cwd=repo_path, check=True)
        return url

    def user_exit(self):
        shutil.rmtree(self.user_dir, onerror=onerror)
        self.github.close()
        sys.exit()

    def access(self):
        if os.path.exists(f"{FILE_JSON_NAME}"):
            with open(f"{FILE_JSON_NAME}", "r") as file:
                if file.read(2) != '[]':
                    file.seek(0)
                    records = json.load(file)
                    print(records)

                    for record in records:

                        if self.username == record["user"]:
                            return "open clone"
                    else:
                      return "first access"
        else:

            json.dumps([], indent=4)  # if json doesn't exist
            return "first access"