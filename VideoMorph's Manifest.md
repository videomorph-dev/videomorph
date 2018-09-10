# VideoMorph's Manifest

VideoMorph is a Video Converter written in Python 3, using ffmpeg as back-end
and PyQt5 for the Graphical User Interface.

## Goal

Unlike other video converters, VideoMorph focuses on a single goal:
make video conversion simple, with an easy to use GUI and allowing
the user to convert to the currently most popular video formats.

VideoMorph GUI is simple and clean, focused on usability, removing annoying
options rarely used.
VideoMorph is a video converter, just that. If you want a video editor,
VideoMorph isn't for you.

## Committers

Member of VideoMorph Development Team that have the capability to commit
changes into the repo are:

- [Ozkar L. Garcell](https://github.com/codeshard)
- [Leodanis Pozo Ramos](https://github.com/lpozo)
- [Leonel Salazar Videaux](https://github.com/leonel-lordford)

## Commit procedure

General Commit procedure to be used:

1. Work on new features, bug fixes and other changes on a separated local
 branch.
1. Once the work is ready, push the whole branch to videomorph-dev.
1. Create a Pull Request over videomorph-dev/develop.
1. Committers must review the changes and approve them.
1. Once changes have been approved, merge the Pull Request into develop branch.
1. If temporary branch is not going to be used again, delete it form
 videomorph-dev

## Contribute procedure

External contributors must:

- Work on modifications
- Push modifications to their forked repo
- Make a Pull Request against videomorph-dev/develop branch

### Branch naming conventions

General conventions for branch naming are:

- The names for branches that committer are going to push up to the repo will
 stick to the following convention:

    ```name_i000_topic```

- Where **``name``** corresponds to the GitHub user name of committer
- **``i000``** represents the issue number the branch is dealing with
- **``topic``**, stands for a descriptive name that reflects the main goal of
 the branch. e.g:

    ```john_i024_feature_mov_format```

- If there is no issue to map the branch then **``i000``** will be used.

## Coding Style and Docstrings

- VideoMorph's code will follow the coding style guide lines described
 in [PEP8](https://www.python.org/dev/peps/pep-0008/)
- Same way, Docstrings in VideoMorph's code will follow the guide lines
 described in [PEP257](https://www.python.org/dev/peps/pep-0257/)
- Tools like **``pylint``**, **``pepe8``**, **``flake``** and others will be
 used to ensure that coding style guides are met.

## Commit messaging style

General rules for writing commit messages:

1. Separate subject from body with a blank line
1. Limit the subject line to 50 characters
1. Capitalize the subject line
1. Do not end the subject line with a period
1. Use the imperative mood in the subject line
1. Wrap the body at 72 characters
1. Use the body to explain what and why vs. how

        Add support for MOV format

        Add support for MOV format with several quality to give more
        default conversion options to the user.

Keep in mind that not all commits require a explanatory body, sometimes with
the subject line is enough.
For more details see: [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)

## General policies

- Use the Release Page on GitHub to publish all the releases of VideoMorph
- Use the official Blog to post about new releases, new features and other
 news
- Use Telegram's Channel as the main communication channel for discussing all
 the topics related to VideoMorph development
- All the code will be strictly tested before pushing it to GitHub, adding the
 corresponding tests to proper file under **``test``** directory
- No merge will be done until the code successfully pass all the tests
 predefine on GitHub repo (Travis CI, CodeCov, etc.), unless the dev-team decide something else.
