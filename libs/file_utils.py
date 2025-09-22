import os


def get_valid_file(prompt: str) -> str:
    """Gets the path to an existing file from the user"""
    while True:
        file_path = input(prompt).strip('"').strip("'")
        if os.path.isfile(file_path):
            return file_path
        else:
            print(f" Path '{file_path}' does not exist. Try again \n")
