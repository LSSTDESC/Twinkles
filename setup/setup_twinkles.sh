#!/usr/bin/env bash
# Run this script to eups declare the Twinkles package from the top level
# directory
if [ "$#" -gt 1 ]
then
    echo "there should be 0 or 1 argument for this script\n"
    exit 1
elif [ "$#" -eq 1 ]
then
    name=$1
else
    name=sims
fi
setup Twinkles -t $USER -t $name

