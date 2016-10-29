#!/bin/bash

for file in tagged_data/*.xlsx; do
    libreoffice \
      --headless \
      --convert-to csv:"Text - txt - csv (StarCalc):44,34,76,3" \
      --outdir tagged_data $file
done
