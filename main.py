import os
from dotenv import load_dotenv

import utils
from repo_manager import Repository
from user import User

def print_main_menu():
    print("Choose one of the following operations: ")
    print("[1] add new directory to the repository")
    print("[2] delete directory")
    print("[3] add new file to the repository")
    print("[4] delete file")
    print("[5] save changes to github")
    print("[6] create new repository")
    print("[7] choose another project")
    print("[8] exit")



def print_menu_no_previous_projects():

        print("Choose one of the following operations: ")
        print("[1] create new repository")
        print("[2] exit")


def get_user_choice(valid_choices):
    choice = input("Answer: ")
    if choice in valid_choices:
        return choice
    print("Invalid option. Try again.")
    return get_user_choice(valid_choices)

def menu(repository):

    while True:
        print_main_menu()
        answer = get_user_choice({'1', '2', '3', '4', '5', '6', '7','8'})
        if answer == '8':
            repository.user.user_exit()
        elif answer == '3':
            repository.add_new_file()
        elif answer == '4':
            repository.delete_file()
        elif answer == '5':
            repository.save_file_changes()
        elif answer == '1':
            repository.create_new_subdirectory()
        elif answer == '2':
            repository.delete_subdirectory()
        elif answer == '6':
            repository.create_new_repo()
        elif answer == '7':
            repository.choose_another_project()



def run():
    #authentication
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise Exception("Token not found!")
    #token=input("Enter access token: ")
    u=User(token)
    repository=Repository(u)

    print(f"User {u.username} logged in successfully")
    print("Welcome to GitFileSystem tool!")


    action=u.access()
    print(action)

    if action== "first access":
        print_menu_no_previous_projects()
        answer = get_user_choice({'1', '2'})
        if answer=='1':
            repository.create_new_repo()
            u.get_git_remote_url(repository.get_last_repo_path(), repository.get_repo_name())
            menu(repository)
        elif answer=='2':
            u.user_exit()

    else:
        repository.open_latest_project()
        u.get_git_remote_url(repository.get_last_repo_path(),repository.get_repo_name())
        menu(repository)

if __name__ == "__main__":
    run()





