import pandas as pd
import os


def get_valid_file(prompt: str) -> str:
    """Gets the path to an existing file from the user"""
    while True:
        file_path = input(prompt).strip('"').strip("'")
        if os.path.isfile(file_path):
            return file_path
        else:
            print(f" Path '{file_path}' does not exist. Try again \n")


if __name__ == "__main__":
    file = get_valid_file("Enter the file location: ")
    df = pd.read_csv(file)
