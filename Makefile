# Makefile for Liberty SDK
# @Author: dongruihu
# @Date: 2025/02/28

# Specify variables here.
PROJECT = liberty_sdk
VERSION = 1.0.1

TEST_RELEASE_ENV = /Users/bytedance/test_release

# Targets
.PHONY: build release test clean all

# Usage:
# $ make test
test:
	@echo "[`date`] Running Python unittest under directory 'unit_test'..."
	@python3 -m unittest -v unit_test.test_parser

build:
	@echo "[`date`] Building ${PROJECT}(v${VERSION})..."
	@sed "s/VERSION_INFO/${VERSION}/g" templates/example__init__.txt > liberty_sdk/__init__.py
	@sed "s/APP_NAME/${PROJECT}/g; s/VERSION_INFO/${VERSION}/g" templates/example_setup.py > setup.py
	@python3 setup.py bdist_wheel
	@echo "[`date`] Done."

test_install:
	source ${TEST_RELEASE_ENV}/venv/bin/activate; python3 -m pip install --force-reinstall /Users/bytedance/PycharmProjects/liberty_tool/dist/liberty_sdk-${VERSION}-py3-none-any.whl

clean:
	@rm -rf *.log tmp/*