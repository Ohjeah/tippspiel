#/bin/bash

git pull origin master
python tippspiel.py
git add saure_gurke.pkl standings.png
git commit -m "neue standings"
git push origin master