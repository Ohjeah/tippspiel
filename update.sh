#/bin/bash

git pull origin gh-pages
python tippspiel.py
git add saure_gurke.pkl standings.png standings_vs_time.png ro*/results.txt
git commit -m "neue standings"
git push origin gh-pages
