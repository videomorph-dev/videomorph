#!/usr/bin/env python3
"""Script to remove copyright and license headers from Python files."""

import re
from pathlib import Path


def remove_license_header(file_path):
    """Remove license header from a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Pattern 1: Remove Apache license headers (comprehensive)
        # This catches various forms of Apache license headers
        apache_patterns = [
            # Complete Apache license block
            r"^(#!/usr/bin/env python3\s*\n)?(# -\*- coding: utf-8 -\*-\s*\n)?(?:#[^\n]*\n)*#[^\n]*Apache License[^\n]*\n(?:#[^\n]*\n)*#[^\n]*limitations under the License\.[^\n]*\n\n?",
            # Partial Apache license (like in videomorph.py)
            r"^(?:#[^\n]*\n)*#\s*You may obtain a copy of the License at\s*\n(?:#[^\n]*\n)*#\s*limitations under the License\.\s*\n\n?",
            # License URL pattern
            r"^(?:#[^\n]*\n)*#\s*http://www\.apache\.org/licenses/LICENSE-2\.0\s*\n(?:#[^\n]*\n)*#\s*limitations under the License\.\s*\n\n?",
            # Generic copyright/license header
            r"^(#!/usr/bin/env python3\s*\n)?(# -\*- coding: utf-8 -\*-\s*\n)?(?:#[^\n]*Copyright[^\n]*\n)(?:#[^\n]*\n)*(?:#[^\n]*license[^\n]*\n)?(?:#[^\n]*\n)*",
        ]

        for pattern in apache_patterns:
            new_content = re.sub(
                pattern,
                "",
                content,
                flags=re.DOTALL | re.MULTILINE | re.IGNORECASE,
            )
            if new_content != content:
                content = new_content
                break

        # Pattern 2: Remove any remaining license-related lines at the start
        lines = content.split("\n")
        cleaned_lines = []
        skip_mode = True

        for line in lines:
            stripped = line.strip()

            # Check if this line contains license-related content
            license_keywords = [
                "license",
                "copyright",
                "apache",
                "licensed under",
                "you may obtain a copy",
                "without warranty",
                "limitations under the license",
                "http://www.apache.org/licenses",
            ]

            if skip_mode:
                # Skip lines that contain license content or are just comments
                is_license_line = any(
                    keyword in stripped.lower() for keyword in license_keywords
                )
                is_comment_or_empty = (
                    stripped.startswith("#") or stripped == ""
                )

                if not is_license_line and not (
                    is_comment_or_empty and not stripped.startswith('"""')
                ):
                    skip_mode = False
                    cleaned_lines.append(line)
                # Special case: keep docstrings and imports
                elif (
                    stripped.startswith('"""')
                    or stripped.startswith("import ")
                    or stripped.startswith("from ")
                ):
                    skip_mode = False
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)

        final_content = "\n".join(cleaned_lines)

        # Clean up multiple empty lines at the start
        final_content = re.sub(r"^\n+", "", final_content)

        # Write back if changed
        if final_content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_content)
            print(f"Removed header from: {file_path}")
            return True
        else:
            print(f"No header found in: {file_path}")
            return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to process all Python files in the videomorph project."""
    # Find all Python files in the videomorph project only (not in venv)
    project_root = Path(__file__).parent
    python_files = []

    # Get files from videomorph package
    videomorph_dir = project_root / "videomorph"
    if videomorph_dir.exists():
        python_files.extend(videomorph_dir.rglob("*.py"))

    # Get files from tests
    tests_dir = project_root / "tests"
    if tests_dir.exists():
        python_files.extend(tests_dir.rglob("*.py"))

    # Get setup.py if exists
    setup_py = project_root / "setup.py"
    if setup_py.exists():
        python_files.append(setup_py)

    # Exclude this script itself
    python_files = [f for f in python_files if f.name != "clean_headers.py"]

    print(f"Found {len(python_files)} Python files")

    processed = 0
    for py_file in python_files:
        if remove_license_header(py_file):
            processed += 1

    print(f"Processed {processed} files successfully")


if __name__ == "__main__":
    main()
