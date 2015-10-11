#!/bin/sh
image_name="xiedongping/book-mbe"
echo $image_name

sudo docker build -t $image_name MBE
sudo docker run -t -e "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" -e "AWS_SECRET_KEY=$AWS_SECRET_KEY" $image_name
