import os
import subprocess


def pull(path):
    try:
        subprocess.run(["git", "pull"],cwd=path, check=True)
    except subprocess.CalledProcessError as e:
        print("Error: ", e)

def clone(url, destination_path):
    is_empty=True
    for _, dirs, files in os.walk(destination_path):
            if dirs or files:
                is_empty = False
                break
    if not is_empty:
            print(f"Repository is not empty at {destination_path}!")
            return
    try:
        subprocess.run(["git","clone",url,destination_path])
    except subprocess.CalledProcessError as e:
        print(f"Error during git clone: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise



def push(repo_path, commit_message):

    try:
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, check=True)
        subprocess.run(["git", "push"], cwd=repo_path, check=True)
        print("All changes have been saved!")
    except subprocess.CalledProcessError as e:
        print("Error: ", e)
        print("Make sure you saved your changes on your local disk before you commit.")
