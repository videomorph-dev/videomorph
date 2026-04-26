UV      := uv
PYTHON  := $(UV) run python
PYTEST  := $(UV) run pytest
RUFF    := $(UV) run ruff
VERSION := $(shell grep '^pkgver=' aur/PKGBUILD | cut -d= -f2)

.PHONY: help dev run test lint format qrc build clean deb exe aur-update

help:
	@echo "VideoMorph build targets:"
	@echo ""
	@echo "  dev          Create .venv and install all dependencies (uv)"
	@echo "  run          Launch VideoMorph"
	@echo "  test         Run tests with coverage report"
	@echo "  lint         Check code style (ruff)"
	@echo "  format       Auto-format code (ruff)"
	@echo "  qrc          Regenerate Qt resource file from qrc/"
	@echo "  build        Build sdist + wheel"
	@echo "  deb          Build Debian .deb package (Linux only)"
	@echo "  exe          Build standalone executable (PyInstaller)"
	@echo "  aur-update   Update aur/PKGBUILD and .SRCINFO for new version"
	@echo "  clean        Remove build artifacts and .venv"
	@echo ""

dev:
	$(UV) sync --all-groups

run:
	$(UV) run python bin/videomorph

test:
	QT_QPA_PLATFORM=offscreen $(PYTEST) tests/ \
		--cov=videomorph \
		--cov-report=term-missing \
		--cov-report=xml

lint:
	$(RUFF) check .
	$(RUFF) format --check .

format:
	$(RUFF) format .
	$(RUFF) check --fix .

qrc:
	cd qrc && pyrcc5 -o ../videomorph/forms/videomorph_qrc.py videomorph.qrc
	sed -i 's/from PyQt5 import QtCore/from PyQt6 import QtCore/' \
		videomorph/forms/videomorph_qrc.py

build: qrc
	$(UV) build

deb:
	$(PYTHON) setup.py --command-packages=stdeb.command bdist_deb

exe:
	$(UV) run pyinstaller videomorph.spec --clean

aur-update:
	@if [ -z "$(V)" ]; then echo "Usage: make aur-update V=1.6"; exit 1; fi
	sed -i "s/^pkgver=.*/pkgver=$(V)/" aur/PKGBUILD
	sed -i "s/^pkgrel=.*/pkgrel=1/" aur/PKGBUILD
	sed -i "s/pkgver = .*/pkgver = $(V)/" aur/.SRCINFO
	sed -i "s/pkgrel = .*/pkgrel = 1/" aur/.SRCINFO
	sed -i "s|videomorph-.*\.tar\.gz::|videomorph-$(V).tar.gz::|" aur/.SRCINFO
	sed -i "s|/tags/v.*\.tar\.gz|/tags/v$(V).tar.gz|" aur/.SRCINFO
	@echo "aur/ updated to v$(V) — commit and push tag to trigger CI"

clean:
	rm -rf build dist deb_dist *.egg-info .venv
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -f coverage.xml .coverage
