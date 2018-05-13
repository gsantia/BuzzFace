#!/bin/bash


echo "This script will download and organize the BuzzFace dataset."
echo "It requires Facebook Graph API and Disqus Plugin API credentials."
echo "Also, it's probably best to run this with superuser priveleges."
echo "Please input Facebook APP ID Key:"
read FB_ID
echo "Now input Facebook APP SECRET Key:"
read FB_SECRET
echo "Now input Disqus APP ID Key:"
read DISQUS_ID
echo "Finally, input Disqus APP SECRET Key:"
read DISQUS_SECRET

`sudo nohup bash helper.sh $FB_ID $FB_SECRET $DISQUS_ID $DISQUS_SECRET >> log 2>&1 &`
