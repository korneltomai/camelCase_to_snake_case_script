A python script for replacing selected camelCase or CamelCase into snake_case in any source file.

# Usage:
### 1. Run the script
  You can provide as many extensions as you want, separated by whitespaces.
   ```
   python replace_camelcase.py [source directory] [extension1] [extension2] [extension3] ...
   ```

### 2. Enter the matches you want to replace
  You can select matches by providing the ranges of match indexes, indicated on the very left side before each match.
  You can provide as many ranges as you want, separated by whitespaces, in a [starting_index:ending_index] format.

  For example, to replace the first 3 and the 5th match, you would type in '1:3 5:5'.
