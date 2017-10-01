#! /bin/sh

pip install -t lib/ passlib cerberus isoweek
exec gcloud app deploy app.yaml
