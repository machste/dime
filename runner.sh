#!/bin/bash

SCRIPT_NAME="$0"
SCRIPTS_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SRC_DIR="${SCRIPTS_ROOT}/src/"

export PYTHONPATH=${SRC_DIR}:${PYTHON_PATH}
PYTHON="$(which python3)"

echo -e "[${SCRIPT_NAME}] start dime"
${PYTHON} -m src.dime

echo -e "[${SCRIPT_NAME}] exit"
