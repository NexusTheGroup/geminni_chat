SHELL := /bin/bash

SECRETS_FILE := $(shell if [ -f .secrets.local ]; then echo .secrets.local; else echo .secrets.example; fi)

.PHONY: ci
ci:
	@command -v actionlint >/dev/null || { echo "actionlint is not installed" >&2; exit 1; }
	actionlint
	@command -v act >/dev/null || { echo "act is not installed" >&2; exit 1; }
	ACT_CMD="act pull_request --secret-file $(SECRETS_FILE) -P ubuntu-latest=catthehacker/ubuntu:act-latest"; \
	echo "Running $$ACT_CMD"; \
	$$ACT_CMD
