#!/bin/bash

# Function to display the help menu
show_help() {
    echo "Usage: $(basename "$0") [FILE...] or [-h | --help]"
    echo
    echo "Removes all lines in the specified files that begin with optional"
    echo "spaces or tabs followed immediately by '#@'."
    echo
    echo "Options:"
    echo "  -h, --help    Display this help message and exit"
    echo
    echo "Example:"
    echo "  $(basename "$0") path/to/file1.py file2.py"
}

# Check if no arguments were provided
if [ $# -eq 0 ]; then
    echo "Error: No files specified." >&2
    show_help
    exit 1
fi

# Check for help flags
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# Initialize an error tracker
has_error=0

# Loop through all arguments passed to the script
for TARGET_FILE in "$@"; do
    # Check if the target is actually a file
    if [ ! -f "$TARGET_FILE" ]; then
        echo "Error: '$TARGET_FILE' does not exist or is not a regular file. Skipping..." >&2
        has_error=1
        continue
    fi

    # Create a temporary file safely
    TEMP_FILE=$(mktemp)

    # Process the file
    sed '/^[[:space:]]*#@/d' "$TARGET_FILE" > "$TEMP_FILE"

    # Overwrite the original file with the cleaned contents
    mv "$TEMP_FILE" "$TARGET_FILE"

    echo "Successfully cleaned: $TARGET_FILE"
done

# Exit with a non-zero status if any file failed to process
if [ $has_error -eq 1 ]; then
    exit 1
else
    exit 0
fi
