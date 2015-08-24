#!/bin/sh
image_name="xiedongping/book-mbe"
echo $S3FLAGS
echo $image_name

sudo docker build -t $image_name MBE
sudo docker run -e "S3FLAGS=$S3FLAGS" -t $image_name
