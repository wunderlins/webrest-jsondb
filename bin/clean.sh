#!/usr/bin/env bash

find ./ -iname '*.pyc' -exec rm {} \;
find ./ -iname '*~' -exec rm {} \;
