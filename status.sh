#!/bin/bash -x
path=`dirname "$0":`
pollintv=`cat $path/settings | grep pollintv | cut -f2`
x=1

while [ x=1 ];
do
	bash $path/heatpump info
	bash $path/heatpump status
	sleep $pollintv
done

