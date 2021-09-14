MKF_CWD := $(shell pwd)

.PHONY: \
  all clean release checks static-checks \
  typechecks tests lint lint-shell lint-python

all: typechecks tests lint release

clean:
	@rm -f ./result*

checks: static-checks tests

static-checks: typechecks lint

typechecks:
	@mypy .

tests:
	@pytest

lint: lint-python lint-shell

lint-shell:
	@shellcheck -x -P \
	  ./contrib/pseudo-test-env.sh \
	  $(shell find ./test_lib/data/cmd_cases -mindepth 1 -executable -type f)

lint-python:
	@flake8

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
