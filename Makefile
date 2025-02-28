# Makefile for Liberty SDK
# @Author: dongruihu
# @Date: 2025/02/28

# Specify variables here.
PROJECT = liberty_sdk
VERSION = v1.0

# Targets
.PHONY: build release test clean all

# Usage:
# $ make test TEST_MODULE=parser
test:
	@echo "[`date`] Running Python unittest under test directory ..."
	@python3 -m unittest $(TEST_MODULE)