DOCKER ?= docker
IMAGE ?= d2tp
VERSION ?= $(shell poetry version -s)

.PHONY: help
help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

clean: ## Remove image (env var: IMAGE)
	$(DOCKER) image rm "$(IMAGE)"

image: ## Build image (env vars: IMAGE, VERSION)
	$(DOCKER) build --build-arg "D2TP_VERSION=$(VERSION)" -t "$(IMAGE):$(VERSION)" .
	$(DOCKER) tag "$(IMAGE):$(VERSION)" "$(IMAGE):latest"
