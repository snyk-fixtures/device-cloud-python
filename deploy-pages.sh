#!/bin/bash

set -o errexit -o nounset

# only run cov on one version of python.
# only run this if cron triggered it
if [ "$TRAVIS_PYTHON_VERSION" = "2.7" ]; then
	if [ "$TRAVS_EVENT_TYPE" = "cron" ]; then
		pytest --cov-report=html --cov=device_cloud --cov-config .coveragerc -v .
		rev=$(git rev-parse --short HEAD)

		if [ -d "htmlcov" ]; then
			cd htmlcov

			git init
			git config user.name "Paul Barrette"
			git config user.email "paulbarrette@gmail.com"

			git remote add upstream "https://$GH_TOKEN@github.com/Wind-River/hdc-python.git"
			git fetch upstream
			git reset upstream/gh-pages

			touch .

			git add -A .
			git commit -m "HDC Python coverage data at ${rev}"
			git push -q upstream HEAD:gh-pages
		else
			echo "Error: no htmlcov directory"
			exit 1
		fi
	fi
fi
exit 0
