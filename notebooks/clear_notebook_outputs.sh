#!/usr/bin/env bash

set -x

for file in *.ipynb; do
    jupyter nbconvert --clear-output --inplace $file
done