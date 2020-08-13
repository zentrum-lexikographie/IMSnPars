.PHONY: dev-setup
dev-setup:
	@pip install -r requirements-dev.txt

.PHONY: test
test:
	@pytest
