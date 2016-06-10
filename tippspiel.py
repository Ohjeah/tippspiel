import string
import glob
import os
from collections import defaultdict
import pandas as pd
import datetime
import matplotlib.pyplot as plt

DATA_FILE = "saure_gurke.pkl"

def read(fname):
    with open(fname, 'r') as f:
        content = [line[:-1] for line in f.readlines()]
    return content

def split(line):
    line = line.split(',')
    a = line[0]
    if len(line) < 2:
        b = None
    else:
        b = line[1]
    return a, b


def get_content(fname):
    content = read(fname)

    if "result" not in fname and len(content[0].split(',')) == 1:
        matches = read(os.path.join(os.path.dirname(fname), "../spiele.txt"))
        content = filter(all, zip(matches, content))
    else:
        content = map(split, filter(bool, content))
    return content


def load_strengths(fname):
    return {k: float(v) for k,v in get_content(fname)}


def valid_tipp(str, valid=frozenset(string.digits + " " + "-")):
    return frozenset(str) <= valid


def parse(tipp):

    if tipp and valid_tipp(tipp):
        return eval(tipp)
    else:
        return None


def load_tipps(fname):
    return {k: parse(v) for k, v in get_content(fname)}


def basename(fname):
    return os.path.splitext(os.path.basename(fname))[0]


def get_all_tipps(round_number):
    files = glob.glob("ro{}/tipps/*.txt".format(round_number))
    for fname in files:
        yield basename(fname), load_tipps(fname)

def score(tipp, result):

    if result is None or tipp is None:
        return 0    # match not played or no valid tipp 

    if tipp == result:
        return 3    # exact result

    elif result*tipp > 0 or (tipp == 0 and result == 0):  # correct winner(>0), oder correct draw(=0)
        return 1

    else:
        return 0

def total_points(tipps, results):
    return sum(score(tipps[match], result) for match, result in results.items())

def get_standing(round_number):
    results = load_tipps("ro{}/results.txt".format(round_number))
    return {player: total_points(tipps, results) for player, tipps in get_all_tipps(round_number)}

def get_all_rounds():
    for rn in [36, 16, 8, 4, 2]:
        if os.path.isfile("ro{}/results.txt".format(rn)):
            yield get_standing(rn)

def add_rounds(standings):
    overall = defaultdict(int)
    for standing in standings:
        for player, points in standing.items():
            overall[player] += points
    return overall


def update_data():


    series = pd.Series(add_rounds(get_all_rounds()))
    series.name = datetime.datetime.now()

    ax = series.plot(kind="bar", rot=0)
    fig = ax.get_figure()
    fig.savefig("standings.png")

    if os.path.isfile(DATA_FILE):
        df = pd.read_pickle(DATA_FILE)
    else:
        df = pd.DataFrame()

    df = df.append(series)

    ax = df.plot()
    fig = ax.get_figure()
    fig.savefig("standings_vs_time.png")

    df.to_pickle(DATA_FILE)




if __name__ == "__main__":
    update_data()