#!/usr/bin/env bash

# todo integrate building of foundation into doit tasks, to make this
# unnecessary. The build has to happen **before** the assets are copied

while true
do
    echo "build foundation..."
    oldPath=$(pwd)
    cd themes/base-foundation5-jinja/core
    grunt build
    cd ${oldPath}
    echo "build site ..."
    nikola build
    sleep 1
done
