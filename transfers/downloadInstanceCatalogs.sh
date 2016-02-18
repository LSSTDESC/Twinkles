#!/bin/bash

# This script will download the gzipped instance catalogs and spectra from a website. The downloaded files will be in $pwd
# run as ./downloadInstanceCatalogs.sh

curl -O http://faculty.washington.edu/rbiswas/Twinkles/InstanceCatalogs/index.txt
file='index.txt'
while IFS='' read -r line || [[ -n "$line" ]]; do
    echo "downloading file: $line"
    curl -O http://faculty.washington.edu/rbiswas/Twinkles/InstanceCatalogs/$line
done < $file
