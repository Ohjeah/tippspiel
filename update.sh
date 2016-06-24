#!/usr/bin/env bash

git pull origin gh-pages
python tippspiel.py
git add standings.png standings_vs_time.png ro*/results.txt index.html
git commit -m "neue standings"
git push origin gh-pages
