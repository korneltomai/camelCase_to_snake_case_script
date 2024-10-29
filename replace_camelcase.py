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


def get_matches_from_files(source, file_paths):
    matches_in_files = {}

    line_number = 0
    for file in file_paths:
        with open(file) as f:
            matches_in_file = []
            for line in f:
                line_number += 1
                matches_in_line = re.findall("\\W(?:[A-Z][a-z]*)+\\W|\\W[a-z]+(?:[A-Z][a-z]*)+\\W", line)
                if matches_in_line:
                    for match in matches_in_line:
                        matches_in_file.append((line_number, match[1:-1], line))
        if matches_in_file:
            rel_file_path = os.path.relpath(file, source)
            matches_in_files[rel_file_path] = matches_in_file

    return matches_in_files


def print_matches(matches_in_files):
    index = 1
    print("―" * os.get_terminal_size().columns)
    for file, matches_in_file in matches_in_files.items():
        for match in matches_in_file:
            print(f"{index}. {file} {match}")
            index += 1
    print("―" * os.get_terminal_size().columns)


def get_ranges_from_user():
    input_ranges = input("Select matches to replace by providing at least one range in a 'index:index' format, separated by a whitespace: ")
    ranges = re.findall("[0-9]+:[0-9]+", input_ranges)

    while not input_ranges or not len(ranges) == len(input_ranges.split()):
        if not input_ranges:
            input_ranges = input("Please enter at least one range: ")
            ranges = re.findall("[0-9]+:[0-9]+", input_ranges)
            continue
        if not len(ranges) == len(input_ranges.split()):
            input_ranges = input("One or more of the ranges are invalid. Please enter at least on valid range: ")
            ranges = re.findall("[0-9]+:[0-9]+", input_ranges)
            continue

    return ranges


def get_length_of_all_matches(matches_in_files):
    length = 0
    for _, matches_in_file in matches_in_files.items():
        length += len(matches_in_file)
    return length


def get_match_by_index(matches_in_files, index):
    current_index = 0
    list_index = 0

    for file, matches_in_file in matches_in_files.items():
        for match in matches_in_file:
            if current_index == index:
                return file, match
            list_index += 1
            current_index += 1
        list_index = 0

    return None


def get_selected_matches(matches_in_files):
    selected_matches = {}

    valid_input = False
    while not valid_input:
        ranges = get_ranges_from_user()

        match_ranges = []
        for r in ranges:
            indexes = [int(index) for index in r.split(":")]
            for index in indexes:
                if index < 1 or index > get_length_of_all_matches(matches_in_files):
                    print(f"The index '{index}' is out of the range. Please try again.")
                    valid_input = False
                    break
            else:
                match_ranges.append(tuple(indexes))
                valid_input = True
            if not valid_input:
                break
        if not valid_input:
            continue

        for match_range in match_ranges:
            index1, index2 = match_range
            for index in range(index1 - 1, index2):
                file, match = get_match_by_index(matches_in_files, index)
                if file not in selected_matches:
                    selected_matches[file] = [match]
                else:
                    selected_matches[file].append(match)

        valid_input = True

    return selected_matches


def to_snake_case(camel_case):
    parts = re.findall("^[A-Z]?[a-z]*|[A-Z][a-z]+|[A-Z]+", camel_case)
    snake_case = "_".join(parts).lower()
    return snake_case


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
    matches_in_files = get_matches_from_files(source_path, file_paths)

    print_matches(matches_in_files)
    selected_matches = get_selected_matches(matches_in_files)
    print_matches(selected_matches)


if __name__ == "__main__":
    main()
