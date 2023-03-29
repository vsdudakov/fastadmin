.PHONY: clean
clean:
	rm -rf node_modules

.PHONY: remove-cache
remove-cache:
	rm -rf node_modules/.cache

.PHONY: dev
dev:
	GENERATE_SOURCEMAP=false PORT=3030 yarn run start

.PHONY: fix
fix:
	yarn run tslint --fix --project .
	yarn run pretty-quick

.PHONY: lint
lint:
	yarn run tslint --project .
	yarn run pretty-quick --check

.PHONY: test
test:
	yarn run test --coverage --watchAll=false

.PHONY: install
install:
	yarn install

.PHONY: build
build:
	GENERATE_SOURCEMAP=false yarn run build

.PHONY: kill
kill:
	kill -9 $$(lsof -t -i:3030)
