import json
import os
import subprocess

import utils
import shutil

from github import GithubException



FILE_JSON_NAME = "users_latest_projects.json"


def onerror(func, path, exc_info):
    import stat

    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

class Repository:
    FILE_JSON_NAME = "users_latest_projects.json"
    def __init__(self, user):
        self.user = user

    def get_repo_name(self ):
        """ reads last created repo  name from json """
        if os.path.exists(FILE_JSON_NAME):
            with open(FILE_JSON_NAME, "r") as file:
                records = json.load(file)
                for record in records:
                    if self.user.username == record["user"]:
                        return record["last"]


    def get_last_repo_url(self):
        repo_name = self.get_repo_name()
        url_repo = self.user.user_url + repo_name
        return url_repo


    def get_last_repo_path(self):
        repo_name = self.get_repo_name()
        path = self.user.user_dir + '/' + repo_name
        print(path)
        return path


    def get_current_repo(self):
        username = self.user.username
        name = self.get_repo_name()
        repo = self.user.github.get_repo(username + '/' + name)
        return repo


    def save_latest_project(self, project):
        if os.path.exists(FILE_JSON_NAME):
            with open(FILE_JSON_NAME , "r") as file:
                try:
                    records = json.load(file)
                except json.JSONDecodeError:
                    records = []
        else:
            records = []

        found = False
        for record in records:
            if record["user"] == self.user.username:
                if project not in record["projects"]:
                    record["projects"].append(project)
                record["last"] = project
                found = True
                break

        if not found:
            records.append({"user": self.user.username, "projects": [project], "last":project})

        with open(FILE_JSON_NAME, "w") as file:
            json.dump(records, file, indent=4)

    def open_latest_project(self):
        """ checks json file to find latest project and clones it"""
        url_repo = self.get_last_repo_url()
        local_path = self.get_last_repo_path()
        repo = utils.clone(url_repo, local_path)
        return repo

    def choose_another_project(self):
        project_dirs = [
            name for name in os.listdir(self.user.user_dir)
            if os.path.isdir(os.path.join(self.user.user_dir, name))
        ]

        if len(project_dirs) < 2:
            print("No other projects available.")
            return

        print("Choose a project:")
        for i, name in enumerate(project_dirs):
            print(f"{i + 1}. {name}")

        try:
            index = int(input("Project: ")) - 1
            if index < 0 or index >= len(project_dirs):
                print("Invalid option!")
                self.choose_another_project()

            chosen_project = project_dirs[index]
            self.save_latest_project(chosen_project)
            full_path = os.path.abspath(os.path.join(self.user.user_dir, chosen_project))

            print(f"Chosen project: {chosen_project}")
            print(f"Path: {full_path}")

        except ValueError:
            print("Invalid input.")
            self.choose_another_project()



    def create_new_repo(self):
        repo_name = input("Insert repo name: ")
        try:
            # create repository on git
            repo = self.user.github.get_user().create_repo(name=repo_name)
        except GithubException as e:
            print(f"Status: {e.status}, Error: ", e)
            if e.status == 422:
                print(f"Repository already exists!")
                return

        # create directory in which the new repo will be cloned
        repo_url = f"{self.user.user_url}{repo_name}"
        path = os.path.join(self.user.user_dir, repo_name)
        os.makedirs(path, exist_ok=True)
        # add READ ME
        try:
            repo.create_file("README.txt", "readme", "")
        except GithubException as e:
            print("Failed to create README.txt:", e)
        # git clone
        utils.clone(repo_url, path)
        # track the new created project as latest
        self.save_latest_project(repo_name)


    def add_new_file(self):
        repo_path = self.get_last_repo_path()
        print("Select directory in which you want to create the new file")
        dir_path = self.find_directory()
        repo = self.get_current_repo()
        file_name = input("Input file name: ")
        file_path = os.path.join(dir_path, file_name)
        print(f"File path: ", file_path)
        parts = os.path.normpath(file_path).split(os.sep)

        idx = parts.index(self.get_repo_name())  # finds index of repo
        # builds github_path starting excluding repo dir
        github_path = os.path.join(*parts[idx + 1:]).replace("\\", "/")

        try:
            repo.create_file(github_path, f"added file {file_name}", "")
            subprocess.run(["git", "pull"], cwd=repo_path, check=True)
            print(f"File {file_name} was added successfully!")
        except GithubException as e:
            print(f"Status: {e.status}, Error: ", e)
            if e.status == 422:
                print(f"File {file_name} already exists!")

    def delete_file(self):
        self.user.get_git_remote_url(self.get_last_repo_path(),self.get_repo_name())
        repo_path = self.get_last_repo_path()
        file_name = input("Input file name to delete: ")
        matches = []
        for root, _, files in os.walk(repo_path):
            if file_name in files:
                if file_name != '.gitignore':
                 matches.append(os.path.join(root, file_name))
                else:
                    print("This file is a folder placeholder. Do not delete it.")
                    return
        if not matches:
            print(f" File {file_name} not found.")
            return

        if len(matches) == 1:
            file_path = matches[0]
            print(f"File found at: {file_path}")
        else:
            print(f"Multiple files named {file_name} found:")
            for i, path in enumerate(matches):
                print(f"[{i + 1}] {os.path.relpath(path, repo_path)}")
            try:
                choice = int(input("Select file number to delete: ")) - 1
                if choice < 0 or choice >= len(matches):
                    print("Invalid choice.")
                    return
                file_path = matches[choice]
            except ValueError:
                print("Invalid input.")
                return

        try:
            os.remove(file_path)
            utils.push(repo_path, f"removed file {file_name}")
            print(f"File {file_name} deleted successfully from {file_path}")
        except Exception as e:
            print(f"Error : {e}")

    def save_file_changes(self):
        repo_path = self.get_last_repo_path()
        commit_message = input("Input commit message: ")
        utils.push(repo_path, commit_message)

    def create_new_subdirectory(self):
        sub_dir_name = input("Input the new directory name: ")
        # the path of the chosen directory where to create the new subdir es. username_workspace\provaTest1\ed
        path_parent = self.find_directory()
        repo = self.get_current_repo()
        # to the parent relative path is added the new dir name
        full_sub_path = os.path.join(path_parent, sub_dir_name)

        if os.path.exists(full_sub_path):
            print(f"Directory {sub_dir_name} already exists in this path!")
            return

        parts = os.path.normpath(full_sub_path).split(os.sep)

        idx = parts.index(self.get_repo_name())  # finds index of repo
        # gitignore file must be added since github doesn't see empty directories
        github_path = os.path.join(*parts[idx + 1:], ".gitignore").replace("\\", "/")


        try:
            repo.create_file(github_path, f"created {sub_dir_name}", "")
            print(f"Folder {sub_dir_name} created on github with file .gitignore")
            repo_path = self.get_last_repo_path()
            print(f"Repo {repo_path}")
            utils.pull(repo_path)
        except GithubException as e:
            print("Creation error on github:", e)

    def delete_subdirectory(self):
        # otherwise git will ask fro credentials before deleting the directory
        self.user.get_git_remote_url(self.get_last_repo_path(),self.get_repo_name())
        print("Select the number of the directory you want to delete: ")
        try:
            dir_path = self.find_directory('2')
        except FileNotFoundError as e:
            print("No directories found:", e)
            return
        # the path of the  directory you want to delete
        dub_dir_name = os.path.basename(os.path.normpath(dir_path))
        shutil.rmtree(dir_path, onerror=onerror)
        utils.push(self.get_last_repo_path(), "Removed dir " + dub_dir_name)

    import os

    def find_directory(self, answer=None):
        repo_path = os.path.abspath(self.get_last_repo_path())
        workspace_root = os.path.abspath(os.path.join(repo_path, os.pardir, os.pardir))

        matches = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if '.git' not in os.path.join(root, d)]
            for dir_name in dirs:
                    matches.append(os.path.relpath(os.path.join(root, dir_name), start=repo_path))

        # user can't delete repo directory
        if answer != '2':
            matches.insert(0, ".")

        matches = [match for match in matches if os.path.isdir(os.path.join(repo_path, match))]


        relative_matches = [
            os.path.relpath(os.path.join(repo_path, match), start=workspace_root)
            for match in matches
        ]

        if relative_matches:
            for i, match in enumerate(relative_matches):
                print(f"{i + 1}. {match}")
            try:
                index = int(input("Choose parent directory: ")) - 1
                if index < 0 or index >= len(relative_matches):
                    print("Invalid option!")
                    return self.find_directory(answer)
                return relative_matches[index]
            except ValueError as e:
                print(f"Error: {e}")
                return self.find_directory(answer)
        else:
            raise FileNotFoundError("Directory not found.")
