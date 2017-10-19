#!/bin/bash

CURRENT_DIR=`pwd`
REPO_PATH=${HOME}/Repository
JC2LI_PATH=${REPO_PATH}/jc2li/jc2li
VENV_PATH=${HOME}/virtualenv
P3_PATH=${VENV_PATH}/python3/bin/
PYTHON=python
RUN=${JC2LI_PATH}/run.py

export PYTHONPATH=$PYTHONPATH:.

${P3_PATH}/${PYTHON} ${RUN} -M $1
