#!/bin/bash

package_name="loggissimo"
old_version=$(cat $package_name/version)


version=$(echo $old_version | awk -F. -v OFS=. 'NF==1{print ++$NF}; NF>1{if(length($NF+1)>length($NF))$(NF-1)++; $NF=sprintf("%0*d", length($NF), ($NF+1)%(10^length($NF))); print}')

sed -i "s/[0-9]\+.[0-9]\+.[0-9]\+\(.dev[0-9]\+\)\?/$version/" ./$package_name/__init__.py

sudo python3.11 setup.py bdist_wheel

echo $version > $package_name/version

python3.11 -m pip install --force-reinstall ./dist/$package_name-$version-py3-none-any.whl
sudo python3.11 -m pip install ./dist/$package_name-$version-py3-none-any.whl

sudo rm ./$package_name-$old_version-py3-none-any.whl
cp dist/$package_name-$version-py3-none-any.whl ./
# sudo rm /var/www/html/$package_name/*
# sudo cp dist/$package_name-$version-py3-none-any.whl /var/www/html/$package_name/

sudo rm -r "$package_name.egg-info"
sudo rm -r "build"

echo "Old version: $old_version"
echo "New version: $version"