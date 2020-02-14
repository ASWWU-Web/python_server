#!/bin/bash
git pull
PROJECT_DIR=$(git rev-parse --show-toplevel)
bash $PROJECT_DIR/scripts/setup.py
bash $PROJECT_DIR/scripts/