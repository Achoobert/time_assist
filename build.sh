#!/bin/bash
# Open Script Editor (you can find it using Spotlight Search) and create a new script.

# Set the directory containing the .scpt files
SCRIPT_DIR="./"  # Change to your target directory if needed

# Output directory (optional, change if desired)
OUTPUT_DIR="./"
mkdir -p "$OUTPUT_DIR"

# Loop through each .scpt file in the directory
for script in "$SCRIPT_DIR"/*.scpt; do
    # Skip if no .scpt files exist
    [ -e "$script" ] || continue

    # Extract filename without extension
    filename=$(basename -- "$script" .scpt)

    # Compile the AppleScript to an .app bundle
    osacompile -o "$OUTPUT_DIR/$filename.app" "$script"

    echo "Compiled: $script -> $OUTPUT_DIR/$filename.app"
done

echo "All scripts compiled successfully!"

