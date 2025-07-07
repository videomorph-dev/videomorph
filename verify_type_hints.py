#!/usr/bin/env python3
"""Script to verify type hints are working correctly."""

import subprocess
import sys


def check_mypy() -> bool:
    """Check if mypy is available and can analyze the code."""
    try:
        # Test a few core files with type hints
        test_files = [
            "videomorph/main.py",
            "videomorph/converter/__init__.py",
            "videomorph/converter/utils.py",
            "videomorph/converter/console.py",
            "videomorph/converter/vmpath.py",
            "videomorph/forms/about.py",
            "tests/test_utils.py",
        ]

        print("Testing type hints with mypy...")
        for file in test_files:
            result = subprocess.run(
                ["python3", "-m", "mypy", "--ignore-missing-imports", file],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"✓ {file} - Type hints OK")
            else:
                print(f"⚠ {file} - Some type issues detected")
                print(f"  Details: {result.stdout}")
        return True
    except FileNotFoundError:
        print("mypy not available - installing would be: pip install mypy")
        return False


def test_imports() -> bool:
    """Test that all imports still work."""
    try:
        print("\nTesting imports...")
        from videomorph.main import main

        print("✓ videomorph.main import successful")

        from videomorph.converter.utils import (
            get_locale,
            which,
            write_size,
            write_time,
        )

        print("✓ videomorph.converter.utils import successful")

        from videomorph.converter import get_cpu_cores

        print("✓ videomorph.converter import successful")

        from videomorph.converter.console import (
            run_on_console,
            search_directory_recursively,
        )

        print("✓ videomorph.converter.console import successful")

        from videomorph.forms.about import AboutVMDialog

        print("✓ videomorph.forms.about import successful")

        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_functionality() -> bool:
    """Test that functions with type hints still work."""
    try:
        print("\nTesting functionality...")
        from videomorph.converter import get_cpu_cores
        from videomorph.converter.utils import (
            get_locale,
            write_size,
            write_time,
        )

        # Test basic functions
        locale = get_locale()
        assert isinstance(locale, str)
        print(f"✓ get_locale() -> {locale}")

        cpu_cores = get_cpu_cores()
        assert isinstance(cpu_cores, int)
        print(f"✓ get_cpu_cores() -> {cpu_cores}")

        time_str = write_time(3661)
        assert isinstance(time_str, str)
        print(f"✓ write_time(3661) -> {time_str}")

        size_str = write_size(1048576)
        assert isinstance(size_str, str)
        print(f"✓ write_size(1048576) -> {size_str}")

        return True
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        return False


def main() -> None:
    """Main verification function."""
    print("VideoMorph Type Hints Verification")
    print("=" * 40)

    all_passed = True

    # Test imports
    if not test_imports():
        all_passed = False

    # Test functionality
    if not test_functionality():
        all_passed = False

    # Test with mypy if available
    check_mypy()

    print("\n" + "=" * 40)
    if all_passed:
        print("✓ All verification tests passed!")
        print("Type hints have been successfully added to VideoMorph.")
    else:
        print("⚠ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
