# Variablen
PACKAGE=pydantic_tracking
VERSION=$(shell hatch version)
PYPROJECT=pyproject.toml

# Setup & Umgebung
.PHONY: install
install:
	hatch env create
	hatch shell

# Testen
.PHONY: test
test:
	hatch run test

# Linting mit Ruff (optional)
.PHONY: lint
lint:
	hatch run ruff check src/ tests/

# Formatierung mit Ruff
.PHONY: format
format:
	hatch run ruff format src/ tests/

# Veröffentlichungs-Check
.PHONY: build
build:
	hatch build

.PHONY: check
check:
	hatch build --check

# Veröffentlichung zu PyPI (Voraussetzung: `~/.pypirc`)
.PHONY: publish
publish: check
	hatch publish

# Versionsbump
.PHONY: bump-patch
bump-patch:
	hatch version patch

.PHONY: bump-minor
bump-minor:
	hatch version minor

.PHONY: bump-major
bump-major:
	hatch version major

# Cleanup
.PHONY: clean
clean:
	rm -rf dist/ build/ *.egg-info
