import sys
from pathlib import Path

from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication, QMessageBox, QWidget

from videomorph.converter import APP_NAME, LOCALE
from videomorph.converter.vmpath import LIBRARY_PATH, resource_path
from videomorph.forms.videomorph import VideoMorphMW


def _dialog_title(icon: QMessageBox.Icon) -> str:
    """Return a consistent message-box title for the provided icon."""
    titles = {
        QMessageBox.Icon.Critical: "Error!",
        QMessageBox.Icon.Warning: "Warning!",
        QMessageBox.Icon.Information: "Info!",
        QMessageBox.Icon.Question: "Info!",
    }
    return titles.get(icon, "Info!")


def _show_dialog(
    icon: QMessageBox.Icon,
    message: str,
    parent: QWidget | None = None,
    buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
) -> QMessageBox.StandardButton | None:
    """Display a modal dialog with consistent styling."""
    if QApplication.instance() is None:
        return None

    dialog = QMessageBox(icon, _dialog_title(icon), message, buttons, parent)
    return dialog.exec()


def _warn_user(
    log_message: str,
    dialog_message: str,
    parent: QWidget | None = None,
) -> None:
    """Log a warning and show a dialog when possible."""
    sys.stderr.write(f"{log_message}\n")
    _show_dialog(QMessageBox.Icon.Warning, dialog_message, parent)


def load_translation(
    locale: str,
    translator: QTranslator,
    resolver=resource_path,
    *,
    parent: QWidget | None = None,
) -> Path | None:
    """Attempt to load a translation file for the given locale."""
    try:
        i18n_dir = resolver("i18n")
    except (KeyError, OSError) as exc:
        _warn_user(
            f"Warning: Translation path lookup failed: {exc}",
            (
                "VideoMorph could not locate the translations directory.\n"
                "English will be used.\n\n"
                f"Details: {exc}"
            ),
            parent,
        )
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
        _warn_user(
            "Warning: No translation loaded.",
            (
                "VideoMorph could not load the selected language.\n"
                "English will be used instead."
            ),
            parent,
        )
    return None


def main() -> None:
    """Main app function."""
    app = QApplication(sys.argv)
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
            "Please install ffmpeg and make sure it is available in your PATH"
        )

        _show_dialog(QMessageBox.Icon.Critical, error_msg, main_win)
        app.quit()
