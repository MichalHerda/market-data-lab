import os


def get_valid_file(prompt: str) -> str:
    """Gets the path to an existing file from the user"""
    while True:
        file_path = input(prompt).strip('"').strip("'")
        if os.path.isfile(file_path):
            return file_path
        else:
            print(f" Path '{file_path}' does not exist. Try again \n")


def get_valid_folder(prompt: str) -> str:
    """Asks the user for a path to an existing folder"""
    while True:
        folder = input(prompt).strip('"').strip("'")
        if os.path.isdir(folder):
            return folder
        else:
            print(f" Folder '{folder}' does not exist. Please try again.\n")


def list_structure(base_folder: str) -> dict:
    """Builds a dictionary: {subfolder: [files]}"""
    structure = {}
    for root, dirs, files in os.walk(base_folder):
        # Relative path with respect to the base folder
        rel_path = os.path.relpath(root, base_folder)
        if rel_path == ".":
            rel_path = ""  # root folder
        structure[rel_path] = sorted(files)
    return structure


def compare_folders(folder1: str, folder2: str):
    struct1 = list_structure(folder1)
    struct2 = list_structure(folder2)

    folders1 = set(struct1.keys())
    folders2 = set(struct2.keys())

    # Compare subfolders
    only_in_1 = folders1 - folders2
    only_in_2 = folders2 - folders1

    if only_in_1:
        print("\n📂 Folders only in folder 1:")
        for f in sorted(only_in_1):
            print("  ", f)

    if only_in_2:
        print("\n📂 Folders only in folder 2:")
        for f in sorted(only_in_2):
            print("  ", f)

    # Compare files in common folders
    common_folders = folders1 & folders2
    for f in sorted(common_folders):
        files1 = set(struct1[f])
        files2 = set(struct2[f])

        diff1 = files1 - files2
        diff2 = files2 - files1

        if diff1 or diff2:
            print(f"\n📁 Differences in folder '{f or '/'}':")
            if diff1:
                print("   Files only in folder 1:", ", ".join(sorted(diff1)))
            if diff2:
                print("   Files only in folder 2:", ", ".join(sorted(diff2)))

    print("\n✅ Comparison finished.")
