"""This module contains the main function for VideoMorph."""

import sys

from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication, QMessageBox

from .converter import LOCALE
from .converter.console import run_on_console
from .converter.vmpath import LIBRARY_PATH, resource_path
from .forms.videomorph import VideoMorphMW


def main() -> None:
    """Main app function."""
    # Create the app
    app = QApplication(sys.argv)

    # Setup app translator
    app_translator = QTranslator()

    try:
        i18n_dir = resource_path("i18n")
        i18n_file = i18n_dir / f"videomorph_{LOCALE[:2]}.qm"

        if i18n_file.exists():
            trans = i18n_dir / f"videomorph_{LOCALE}"
            if app_translator.load(trans.__str__()):
                app.installTranslator(app_translator)
            else:
                print(
                    f"Warning: Failed to load translation file: {trans}",
                    file=sys.stderr,
                )
    except (KeyError, OSError) as e:
        print(f"Warning: Translation setup failed: {e}", file=sys.stderr)

    # Create the Main Window
    main_win = VideoMorphMW()

    # Check for conversion library and run
    if LIBRARY_PATH:
        if len(sys.argv) > 1:  # If it is running from console
            run_on_console(app, main_win)
        else:  # Or is running on GUI
            main_win.show()
            sys.exit(app.exec())
    else:
        # Create error message for missing ffmpeg library
        error_msg = main_win.tr(
            "VideoMorph could not find the ffmpeg library on your system.\n\n"
            "Please install ffmpeg and make sure it is available in your PATH,\n"
            "or place the ffmpeg executable in the application directory."
        )

        msg_box = QMessageBox(
            QMessageBox.Icon.Critical,
            main_win.tr("Error!"),
            error_msg,
            QMessageBox.StandardButton.NoButton,
            main_win,
        )
        msg_box.addButton("&Ok", QMessageBox.ButtonRole.AcceptRole)
        if msg_box.exec() == QMessageBox.ButtonRole.AcceptRole:
            app.quit()  # Use app.quit() instead of qApp.closeAllWindows()
