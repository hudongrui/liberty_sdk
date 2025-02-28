# Makefile for Liberty SDK
# @Author: dongruihu
# @Date: 2025/02/28

# Specify variables here.
PROJECT = liberty_sdk
VERSION = v1.0

# Targets
.PHONY: build release test clean all

# Usage:
# $ make test
test:
	@echo "[`date`] Running Python unittest under directory 'unit_test'..."
	@python3 -m unittest -v unit_test.test_parser

clean:
	@rm -rf *.log tmp/*