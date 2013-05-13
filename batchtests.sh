#!/bin/bash
# Jon_K <jon.kelley@rackspace.com>

# Runs all unit tests explicitly defined within onlinetests; returns 1 if failure.
# This is good for Jenkens build failures and that sort of thing.

onlinetests="broken.feature new.feature"
#1tests=*.feature # Do every feature.
for test in $onlinetests; do
	behave features/$test
	echo "===================================================================================="
	echo "===================================================================================="
	if [ $? -ne 0 ]; then
    	failed=1
	fi
done

if [[ $failed -eq 1 ]]; then
	exit 1 # Makes jenkens consider it a failure.
fi
