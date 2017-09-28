#! /bin/sh

python -m unittest discover -s -d server || exit 1
exec pep8 server
