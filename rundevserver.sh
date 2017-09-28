#! /bin/sh

if test "$1" = "datastore"; then
    gcloud alpha emulators datastore start &
fi

exec python server/main.py "$@"
