import string
import glob
import os
from collections import defaultdict
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.ticker as ticker
import seaborn as sns
import datetime
from itertools import repeat
from operator import sub

DATA_FILE = "saure_gurke.pkl"
ROUND_MULTIPLICATOR = {36: 1, 16: 2, 8: 3, 4: 4, 2: 5}

def read(fname):
    with open(fname, 'r') as f:
        content = [line[:-1] for line in f.readlines()]
    return filter(bool, content)

def valid_tipp(str, valid=frozenset(string.digits + " " + "-")):
    return frozenset(str) <= valid

def parse(tipp):
    if tipp and valid_tipp(tipp):
        return [int(x) for x in tipp.split('-')]
    else:
        return None

def split(line, with_time=False):
    line = line.split(',')
    index = 0
    if with_time:
        time = line[0]
        index = 1
    match = line[index]
    if len(line) > index+1:
        result = line[index+1]
    else:
        result = None
    if with_time:
        return time, match, result
    else:
        return match, result

def parse_result(content):
    for line in content:
        time, match, result = split(line, with_time=True)
        yield {'time': time, 'match': match, 'result': tipp}


def get_content(fname):
    return map(split, read(fname))


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

    elif tipp == result:
        return 3    # exact result

    elif sub(*result)*sub(*tipp) > 0 or (sub(*tipp) == 0 and sub(*result) == 0):  # correct winner(>0), oder correct draw(=0)
        return 1

    else:
        return 0

def total_points(tipps, results):
    return sum(score(tipps[match], result) for match, result in results.items())

def get_standing(round_number):
    results = load_tipps("ro{}/results.txt".format(round_number))
    return {player: ROUND_MULTIPLICATOR[round_number] * total_points(tipps, results)
            for player, tipps in get_all_tipps(round_number)}

def get_all_rounds():
    for rn in ROUND_MULTIPLICATOR.keys():
        if os.path.isfile("ro{}/results.txt".format(rn)):
            yield get_standing(rn)

def add_rounds(standings):
    overall = defaultdict(int)
    for standing in standings:
        for player, points in standing.items():
            overall[player] += points
    return overall


def update_data():

    sns.set_style('white')
    plt.xkcd()
    series = pd.Series(add_rounds(get_all_rounds()))
    series.name = datetime.datetime.now()
    colors = sns.color_palette("husl", len(series))
    ax = series.plot(kind="bar", rot=0, sort_columns=True, color=colors)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    fig = ax.get_figure()
    fig.suptitle("Aktuelles Ranking")
    plt.xlabel("Spieler")
    plt.ylabel("Punkte")
    fig.subplots_adjust(bottom=0.15)
    fig.savefig("standings.png")

    if os.path.isfile(DATA_FILE):
        df = pd.read_pickle(DATA_FILE)
    else:
        df = pd.DataFrame()
    df = df.append(series)

    ax = df.plot(sort_columns=True, rot=0, color=colors, marker='o')
    date1 = datetime.datetime(2016, 6, 10)
    date2 = datetime.datetime(2016, 7, 11)
    ax.xaxis.set_major_formatter(dates.DateFormatter('%d.%m'))
    ax.set_ylim([0, 1.1*max(series)])
    ax.set_xlim(date1, date2)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    fig = ax.get_figure()
    fig.suptitle("Punkte vs Zeit")
    plt.xlabel("Datum")
    plt.ylabel("Punkte")
    fig.subplots_adjust(bottom=0.15)
    fig.savefig("standings_vs_time.png")

    df.to_pickle(DATA_FILE)


if __name__ == "__main__":
    update_data()
