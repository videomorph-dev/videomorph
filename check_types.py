#!/usr/bin/env python3
"""Script to check type hints functionality."""

from videomorph.converter.library import Library
from videomorph.converter.profile import Profile
from videomorph.converter.tasklist import TaskList
from videomorph.converter.utils import (
    get_locale,
    which,
    write_size,
    write_time,
)
from videomorph.converter.video import Video


def main():
    """Main function to test type hints."""

    # Test Video class
    print("Testing Video class...")
    try:
        video = Video("sample-video.mp4")
        print(f"  Video name: {video.get_name()}")
        print(f"  Video name with ext: {video.get_name(with_extension=True)}")
        print(f"  Video is valid: {video.is_valid()}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test Profile class
    print("\nTesting Profile class...")
    try:
        profile = Profile()
        print(f"  Profile initialized: {profile}")
        print(f"  Quality tag: {profile.quality_tag}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test Library class
    print("\nTesting Library class...")
    try:
        library = Library()
        print(f"  Library initialized: {library}")
        print(f"  Library path: {library.path}")
        print(f"  Prober path: {library.prober_path}")
    except Exception as e:
        print(f"  Error: {e}")

    # Test utility functions
    print("\nTesting utility functions...")
    try:
        locale = get_locale()
        print(f"  Locale: {locale}")

        dir_path = which("dir")
        print(f"  dir path: {dir_path}")

        time_str = write_time(3661)
        print(f"  Time (3661s): {time_str}")

        size_str = write_size(1024 * 1024)
        print(f"  Size (1MB): {size_str}")

    except Exception as e:
        print(f"  Error: {e}")

    # Test TaskList
    print("\nTesting TaskList class...")
    try:
        profile = Profile()
        task_list = TaskList(profile)
        print(f"  TaskList initialized: {task_list}")
        print(f"  TaskList length: {task_list.length}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\nAll type hint tests completed!")


if __name__ == "__main__":
    main()
