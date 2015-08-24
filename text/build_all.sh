#!/bin/sh
# The build 
make clean
make web
make pdf-a4
make clean
make web_cn
make pdf-cn
