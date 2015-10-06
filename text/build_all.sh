#!/bin/sh
# The build 
make clean
make specs
make web
make pdf-a4
make clean
make specs_cn
make web_cn
make pdf-cn
