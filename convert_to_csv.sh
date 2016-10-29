#!/bin/bash

for file in tagged_data/*.xlsx; do
    libreoffice --headless --convert-to csv $file --outdir tagged_data
done
