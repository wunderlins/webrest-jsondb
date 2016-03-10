#!/usr/bin/env bash

uri=$1
method="GET"

post=""
if [ ! -t 0 ]; then
	while read line; do
		post="$post$line"
	done < /dev/stdin
	method="POST"
fi

# echo "$post"
if [[ "$method" = "POST" ]]; then
	curl --data "$post" -X$method -iH "Accept: text/xml" localhost:8083/$uri
else
	curl -X$method -iH "Accept: text/xml" localhost:8083/$uri
fi

