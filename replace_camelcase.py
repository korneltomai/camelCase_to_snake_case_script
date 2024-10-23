import sys
import re
import os

def validate_extensions(extensions):
    for ext in extensions:
        if not re.search("^\\.[a-zA-Z]+$", ext):
            return False
    return True


def main(source, extensions):
    print(f"Source: {source}\nExtensions: {extensions}")


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
