#/bin/bash

git pull origin gh-pages
python tippspiel.py
git add saure_gurke.pkl standings.png
git commit -m "neue standings"
git push origin gh-pages