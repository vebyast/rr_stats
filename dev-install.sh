#!/usr/bin/env bash

# Build
poetry build
# Install using the new version
LATEST_VERSION=$(ls dist/*.whl | tail -n 1)
pipx install --force "${LATEST_VERSION}"
