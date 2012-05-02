#!/bin/sh

MODULES=$(echo *.py omot/*.py)

echo '===> Running pylint...'
pylint $MODULES

echo '===> Running pychecker...'
pychecker $MODULES

echo '===> Running doctest...'
python -m doctest $MODULES
