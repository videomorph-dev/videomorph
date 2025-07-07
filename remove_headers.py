#!/usr/bin/env python3
"""Script to remove copyright headers from Python files."""

import re
from pathlib import Path


def remove_copyright_header(file_path):
    """Remove copyright header from a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Pattern to match copyright header - from start of file to end of Apache license
        # Includes shebang, encoding, file name, copyright, and license text
        pattern = r"^(#!/usr/bin/env python3\s*\n)?(# -\*- coding: utf-8 -\*-\s*\n)?#?\s*\n?# File.*?\n#?\s*\n?#\s*VideoMorph.*?\n.*?# limitations under the License\.\s*\n\n?"

        # Alternative pattern for simpler headers
        simple_pattern = r"^(#!/usr/bin/env python3\s*\n)?(# -\*- coding: utf-8 -\*-\s*\n)?(#\s*\n)?# File.*?\n#?\s*\n?#\s*VideoMorph.*?\n.*?# limitations under the License\.\s*\n\n?"

        # Try the main pattern first
        new_content = re.sub(
            pattern, "", content, flags=re.DOTALL | re.MULTILINE
        )

        # If no change, try the simple pattern
        if new_content == content:
            new_content = re.sub(
                simple_pattern, "", content, flags=re.DOTALL | re.MULTILINE
            )

        # If still no change, try a more aggressive pattern
        if new_content == content:
            # Look for any block starting with # -*- coding and ending with License.
            aggressive_pattern = r"^(#!/usr/bin/env python3\s*\n)?(# -\*- coding: utf-8 -\*-.*?License\.\s*\n)\n?"
            new_content = re.sub(
                aggressive_pattern, "", content, flags=re.DOTALL | re.MULTILINE
            )

        # Write back if changed
        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Removed header from: {file_path}")
            return True
        else:
            print(f"No header found in: {file_path}")
            return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to process all Python files."""
    # Find all Python files
    project_root = Path(__file__).parent
    python_files = list(project_root.rglob("*.py"))

    # Exclude this script itself
    python_files = [f for f in python_files if f.name != "remove_headers.py"]

    print(f"Found {len(python_files)} Python files")

    processed = 0
    for py_file in python_files:
        if remove_copyright_header(py_file):
            processed += 1

    print(f"Processed {processed} files successfully")


if __name__ == "__main__":
    main()
