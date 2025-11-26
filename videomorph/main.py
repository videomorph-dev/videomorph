import sys
from pathlib import Path

from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication, QMessageBox

from videomorph.converter import LOCALE
from videomorph.converter.vmpath import LIBRARY_PATH, resource_path
from videomorph.forms.videomorph import VideoMorphMW


def load_translation(
    locale: str,
    translator: QTranslator,
    resolver=resource_path,
) -> Path | None:
    """Attempt to load a translation file for the given locale."""
    try:
        i18n_dir = resolver("i18n")
    except (KeyError, OSError) as exc:
        print(f"Warning: Translation path lookup failed: {exc}", file=sys.stderr)
        return None

    candidates = [
        i18n_dir / f"videomorph_{locale}.qm",
        i18n_dir / f"videomorph_{locale[:2]}.qm",
    ]

    for translation in candidates:
        if not translation.exists():
            continue

        path_str = translation.__str__()
        filename = translation.stem
        directory = translation.parent.__str__()

        if translator.load(path_str) or translator.load(filename, directory):
            return translation

    if not locale.lower().startswith("en"):
        print("Warning: No translation loaded.", file=sys.stderr)
    return None


def main() -> None:
    """Main app function."""
    app = QApplication([])
    app_translator = QTranslator()
    loaded_translation = load_translation(LOCALE, app_translator)
    if loaded_translation:
        app.installTranslator(app_translator)

    # Create the Main Window
    main_win = VideoMorphMW()

    # Check for conversion library and run
    if LIBRARY_PATH:
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
