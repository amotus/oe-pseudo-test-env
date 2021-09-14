MKF_CWD := $(shell pwd)

.PHONY: all clean release typechecks tests lint lint-shell

all: typechecks tests lint release

clean:
	rm -f ./result*

typechecks:
	mypy . $(shell find ./tests -name "test_*.py")

tests:
	pytest

lint: lint-shell

lint-shell:
	shellcheck -x -P \
	  $(shell find ./bin -mindepth 1 -executable -type f)

release:
	nix-build release.nix -A default

release-local:
	nix-build release.nix -A defaultLocal

shell-dev:
	nix-shell release.nix -A shell.dev

shell-installed:
	nix-shell release.nix \
	  -A shell.installed

shell-installed-pure:
	nix-shell release.nix \
	  -A shell.installed \
	  --pure --keep "XDG_RUNTIME_DIR"

shell-build:
	nix-shell release.nix -A default
