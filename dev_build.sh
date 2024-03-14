#!/bin/bash

package_name="loggissimo"
old_version=$(cat $package_name/version)

min=1000000
max=9999999

version="$old_version"".dev$(shuf -i $min-$max -n 1)"

echo $version

sed -i "s/[0-9]\+.[0-9]\+.[0-9]\+\(.dev[0-9]\+\)\?/$version/" ./$package_name/__init__.py

sudo python3 setup.py bdist_wheel

sed -i "s/[0-9]\+.[0-9]\+.[0-9]\+\(.dev[0-9]\+\)\?/$old_version/" ./$package_name/__init__.py

python3 -m pip install ./dist/$package_name-$version-py3-none-any.whl
sudo python3 -m pip install ./dist/$package_name-$version-py3-none-any.whl

sudo rm ./$package_name-*dev*-py3-none-any.whl
cp dist/$package_name-$version-py3-none-any.whl ./
sudo cp dist/$package_name-$version-py3-none-any.whl ../dev_dist/

sudo rm -r dist/
sudo rm -r "$package_name.egg-info"
sudo rm -r "build"

echo "Dev version: $version"