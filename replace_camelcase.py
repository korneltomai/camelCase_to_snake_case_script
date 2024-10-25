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


def get_matches_from_file(source, file_paths):
    matches = []
    line_number = 0
    for file in file_paths:
        with open(file) as f:
            for line in f:
                line_number += 1
                matches_in_line = re.findall("\\W[a-zA-Z]+(?:[A-Z][a-z]*)+\\W", line)
                if matches_in_line:
                    for match in matches_in_line:
                        matches.append(tuple([os.path.relpath(file, source), line_number, match[1:-1], line]))
    return matches


def print_matches(matches):
    index = 1
    print("―" * os.get_terminal_size().columns)
    for match in matches:
        print(f"{index}. {match}")
        index += 1
    print("―" * os.get_terminal_size().columns)


def get_selected_matches(matches):
    match_indexes = []
    input_ranges = input("Select matches to replace by providing at least one range in a 'index:index' format, separated by a comma (,): ")
    while not matches:
        input_ranges = input("Please enter at least one range: ")

    matches = re.findall("[0-9]+:[0-9]+", input_ranges)
    for match in matches:
        match_indexes.append(tuple(match.split(":")))
    return match_indexes


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        raise Exception("Invalid arguments. Please provide a valid path to a source directory and at least one file extension to scan.")

    source = args[0]
    extensions = args[1:]

    if not os.path.exists(source):
        raise Exception("Invalid source directory.")
    if not validate_extensions(extensions):
        raise Exception("Invalid extension(s).")

    source_path = os.path.join(os.getcwd(), source)
    file_paths = get_source_files(source_path, extensions)
    matches = get_matches_from_file(source_path, file_paths)

    print_matches(matches)
    selected_matches = get_selected_matches(matches)
    print(selected_matches)


if __name__ == "__main__":
    main()
