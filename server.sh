#!/bin/bash

source ./setup.sh

SERVER_PATH=${JC2LI_PATH}/server
SERVER_APP=main.py

echo 'Running server.'
python ${SERVER_PATH}/${SERVER_APP}
echo ''
echo 'Server stopped.'
