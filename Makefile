DOCKER ?= docker
IMAGE ?= 13kb/d2tp
VERSION ?= $(shell poetry version -s)

.PHONY: help
help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

clean: ## Remove image
	$(DOCKER) image rm "$(IMAGE)"

image: ## Build image
	$(DOCKER) build --pull -t "$(IMAGE):$(VERSION)" -t "$(IMAGE):latest" .

publish: image ## Publish image to docker registry
	$(DOCKER) push "$(IMAGE):$(VERSION)"
	$(DOCKER) push "$(IMAGE):latest"
