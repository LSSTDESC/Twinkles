#!/bin/bash

curl -O http://faculty.washington.edu/rbiswas/Twinkles/InstanceCatalogs/index.txt
file='index.txt'
while IFS='' read -r line || [[ -n "$line" ]]; do
    echo "downloading file: $line"
    curl -O http://faculty.washington.edu/rbiswas/Twinkles/InstanceCatalogs/$line
done < $file
