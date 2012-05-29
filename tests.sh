#!/bin/sh

# test.sh
# 
# place all tests you want to run before proceeding to build a package here
set -e

BLUE="\033[1;34m"
GREEN="\033[1;32m"
RED="\033[1;31m"
RESET="\033[0m"

echo "${GREEN}=> Running tests ...${RESET}"


echo "run tests here"

env/bin/python -c "import sanity; sanity.check()"

