#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e
# Function to log messages to the console
log() {
    echo "[SCRIPT] $1"
}
# Get the first argument passed to the script or use python3 as the default
PYTHON_BIN="${1:-python3}"
log "Using python: $PYTHON_BIN"

# Go into backend folder
log "cd into ./backend"

# Check that the version of python being used is 3.5 or newer
log "Make sure we use python 3.5 or newer"
$PYTHON_BIN -c "import sys; assert sys.version_info >= (3, 5), 'Python 3.5 or newer is required to build. Currently using: {}'.format(sys.version_info)"

 

# Clear files in dist
log "Clear dist folder"
rm -rf dist/* || true

 

# Remove the existing virtual environment
log "rm venv"
rm -rf venv/ || true

 

# Create a new virtual environment
log "Creating venv"
virtualenv --python $PYTHON_BIN venv

 

# Update package tools in the virtual environment
log "Update package tools in venv"
venv/bin/pip install -U pip setuptools wheel build

 

# Build wheel distribution for backend
log "Building wheel"
# Change directory to where setup.py is located
venv/bin/python -m build --no-isolation --wheel


 

# Copy the built wheel to the expected location
log "Copy wheels to: ../ansible/playbooks/files/"
cp dist/*.whl ansible/roles/backend/files/
log "######################################################### NEW BUILD CREATED, AND COPIED TO ANSIBLE FILES DIRECTORY IN ORDER TO BE DEPLOYED   ################################################"

# # log in to docker
# docker login --username volkan.akcora@gmail.com --password hlktvurkxllu996 docker.io

# # clean the current images
# #docker rmi all --force

# # run docker file to build a new image
# docker build -t stockcollector -f docker --no-cache .


# #tag the docker image
# docker tag stockcollector volkanakcora96/stock_collector:latest

# #push the image to the docker hub
# docker push volkanakcora96/stock_collector:latest
