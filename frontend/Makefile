.PHONY: help  # Shows this message
help:
	@grep '^.PHONY: .* #' Makefile | sed 's/\.PHONY: \(.*\) # \(.*\)/\1	\2/' | expand -t20


.PHONY: clean  # Cleaning artefacts
clean:
	find . | grep -E "(dist$$|node_modules$$)" | xargs rm -rf


.PHONY: install  # Install
install:
	@echo "Install"
	@exec yarn install


.PHONY: check  # Runs linters
check:
	@echo "Run linters"
	@exec yarn run lint
	@exec yarn run biome-lint


.PHONY: fix  # Runs linters and fixes auto-fixable errors
fix:
	@echo "Fix linters"
	@exec yarn run lint --fix
	@exec yarn run biome-check


.PHONY: lint  # Runs linters
lint:
	@echo "Run linters"
	@exec yarn run lint
	@exec yarn run biome-lint


.PHONY: test  # Runs tests
test:
	@echo "Run tests"
	@exec yarn run coverage


.PHONY: dev  # Run dev server
dev:
	@exec yarn run dev --host 0.0.0.0 --port 3030


.PHONY: remove_cache  # Remove cache
remove_cache:
	rm -rf node_modules/.cache


.PHONY: build  # Build prod server
build:
	@exec yarn run build
