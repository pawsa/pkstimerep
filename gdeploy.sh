#! /bin/sh

pip install -t lib/ cerberus isoweek
exec gcloud app deploy app.yaml
