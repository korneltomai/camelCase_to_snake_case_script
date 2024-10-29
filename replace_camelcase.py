import shutil
import sys
import re
import os

BACKUP_FOLDER = "backup"

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

    for file in file_paths:
        line_number = 0
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


def get_ranges_from_user(amount_of_matches):
    ranges = []

    input_ranges = input("Select matches to replace by providing at least one range in a 'index:index' format, separated by a whitespace: ").split()

    valid_input = False
    while not valid_input:
        if not input_ranges:
            input_ranges = input("Please enter at least one range: ").split()
            continue

        for r in input_ranges:
            try:
                indexes = [int(index) for index in r.split(":")]
            except ValueError:
                input_ranges = input("Ranges can only contain positive whole numbers. Please enter a valid range: ").split()
                break

            for index in indexes:
                if index < 1 or index > amount_of_matches:
                    input_ranges = input(f"The index '{index}' is out of the range. Please enter at least on valid range: ").split()
                    valid_input = False
                    break

                if indexes[0] > indexes[1]:
                    input_ranges = input(f"The starting index can't be bigger than the ending index. In '{indexes[0]}:{indexes[1]}'."
                                         f" Please enter at least on valid range: ").split()
                    valid_input = False
                    break
                else:
                    ranges.append(tuple(indexes))
                    valid_input = True
            if not valid_input:
                break

    return ranges


def get_amount_of_all_matches(matches_in_files):
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

    amount_of_matches = get_amount_of_all_matches(matches_in_files);
    match_ranges = get_ranges_from_user(amount_of_matches)

    for match_range in match_ranges:
        index1, index2 = match_range
        for index in range(index1 - 1, index2):
            file, match = get_match_by_index(matches_in_files, index)
            if file not in selected_matches:
                selected_matches[file] = [match]
            else:
                selected_matches[file].append(match)

    return selected_matches


def to_snake_case(camel_case):
    parts = re.findall("^[A-Z]?[a-z]*|[A-Z][a-z]+|[A-Z]+", camel_case)
    snake_case = "_".join(parts).lower()
    return snake_case


def create_subdirectories(file_paths):
    for path in file_paths:
        dir_path, _ = os.path.split(path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


def backup_affected_files(selected_matches, source_path):
    rel_paths = list(selected_matches.keys())
    full_paths = [os.path.join(source_path, rel_path) for rel_path in rel_paths]

    dest_path = os.path.join(os.getcwd(), BACKUP_FOLDER)
    full_dest_paths = [os.path.join(dest_path, rel_path) for rel_path in rel_paths]

    for source_file, dest_file in zip(full_paths, full_dest_paths):
        dest_dir, _ = os.path.split(dest_file)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        try:
            shutil.copy(source_file, dest_file)
        except PermissionError:
            print("Permission denied.")
        except:
            print("Error occurred while copying file.")


def replace_camelcase_in_files(selected_matches, source_path):
    rel_paths = list(selected_matches.keys())
    full_paths = [os.path.join(source_path, rel_path) for rel_path in rel_paths]

    for rel_path, file_path in zip(rel_paths, full_paths):
        with open(file_path, "r+") as f:
            lines = f.readlines()
            f.seek(0)
            for match in selected_matches[rel_path]:
                line_number, matched_word, _ = match
                lines[line_number - 1] = lines[line_number - 1].replace(matched_word, to_snake_case(matched_word))
            f.writelines(lines)


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

    backup_affected_files(selected_matches, source_path)
    replace_camelcase_in_files(selected_matches, source_path)


if __name__ == "__main__":
    main()
