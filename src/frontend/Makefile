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
	mv ./build/static/js/main*.js ./build/static/js/main.min.js
	mv ./build/static/css/main*.css ./build/static/css/main.min.css
	rm -rf ./static/js
	rm -rf ./static/css
	cp -rf build/static/js/ static/js/
	cp -rf build/static/css/ static/css/

.PHONY: fix
fix:
	yarn run tslint --fix --project .
	yarn run pretty-quick

.PHONY: kill
kill:
	kill -9 $$(lsof -t -i:3030)
