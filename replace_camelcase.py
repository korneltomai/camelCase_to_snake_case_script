import sys
import re
import os

def validate_extensions(extensions):
    for ext in extensions:
        if not re.search("^\\.[a-zA-Z]+$", ext):
            return False
    return True


def get_source_files(source_path, extensions):
    file_paths = []
    for root, dirs, files in os.walk(source_path):
        for file in files:
            if file.endswith(tuple(extensions)):
                file_paths.append(os.path.join(root, file))
    return file_paths


def check_files_for_camelcase(file_paths):
    matches = []
    line_number = 0
    for file in file_paths:
        with open(file) as f:
            for line in f:
                line_number += 1
                match = re.search("\\W[a-zA-Z]+([A-Z][a-z]*)+\\W", line)
                if match:
                    matches.append(tuple([file, line_number, match.group()[1:-1], line]))
    return matches


def main(source, extensions):
    source_path = os.path.join(os.getcwd(), source)
    file_paths = get_source_files(source_path, extensions)
    matches = check_files_for_camelcase(file_paths)

    for match in matches:
        print(match)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        raise Exception("Invalid arguments. Please provide a valid path to a source directory and at least one file extension to scan.")

    source = args[0]
    extensions = args[1:]

    if not os.path.exists(source):
        raise Exception("Invalid source directory.")
    if not validate_extensions(extensions):
        raise Exception("Invalid extension(s).")

    main(source, extensions)
