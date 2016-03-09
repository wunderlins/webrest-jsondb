# webpy REST exmaple

REST example with json/xml/txt and html output. The output is controlled 
by the http Accept request header.

## install 
	./bin/setup.sh

## Run
	./httpd.py&

## Testing
	curl -iH "Accept: application/json" localhost:8082/a/b/c
	curl -iH "Accept: text/xml" localhost:8082/a/b/c
	curl -iH "Accept: text/html" localhost:8082/a/b/c
	curl -iH "Accept: text/plain" localhost:8082/a/b/c

Using a different method:
	curl -XDELETE  -iH "Accept: text/xml" localhost:8082/a/b/c

if the Accept header is missing, json is the default.



