#!/bin/sh
# The build 
make specs
make results
make dirhtml
make web
make clean
make pdf-a4
make clean
make specs_cn
make results
make dirhtml_cn
make web_cn
make clean
make pdf-cn
