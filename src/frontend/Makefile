.PHONY: clean
clean:
	rm -rf node_modules

.PHONY: remove-cache
remove-cache:
	rm -rf node_modules/.cache

.PHONY: install
install:
	yarn install

.PHONY: dev
dev:
	PORT=3030 yarn run start

.PHONY: lint
lint:
	yarn run tslint --project .
	yarn run pretty-quick --check

.PHONY: build
build:
	yarn run build


.PHONY: fix
fix:
	yarn run tslint --fix --project .
	yarn run pretty-quick

.PHONY: kill
kill:
	kill -9 $$(lsof -t -i:3030)
