.PHONY: dev-setup
dev-setup:
	@pip install -e '.[test]'

.PHONY: test
test:
	@pytest
