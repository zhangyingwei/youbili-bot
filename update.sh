#!/usr/bin/env bash

rm -f /home/d_state.txt.1
cp d_state.txt /home/d_state.txt.1

git add .
git commit -m 'commit by update'
git fetch –all
git reset --hard origin/main

sed 's/=dev/=prod/g' conf.ini
mv -f /home/d_state.txt.1 ./d_state.txt
git add .
git commit -m 'commit by update'
git push