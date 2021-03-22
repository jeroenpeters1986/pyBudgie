#!/bin/bash


# Allow to specify test arguments (test files), just like when running pytest directly.
CMD_ARGS=""
for ARGUMENT in "$@"
do
	CMD_ARGS="$CMD_ARGS $ARGUMENT"
done

coverage run manage.py test -v2 --settings=settings_test --noinput  $CMD_ARGS

echo
echo "      Generating coverage reports..."
coverage html

echo
echo "      Detailed coverage report can be found in: coverage-reports/html/index.html"
echo
