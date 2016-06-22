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
from functools import partial
from toolz.dicttoolz import get_in


DATA_FILE = "saure_gurke.pkl"
ROUND_MULTIPLICATOR = {24: 1, 16: 2, 8: 3, 4: 4, 2: 5}


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


def load_result(fname):
    content = get_content(fname, with_time=True)
    return {match: {'time': time, 'result': parse(result)} for time, match, result in content}


def get_content(fname, with_time=False):
    splitter = partial(split, with_time=with_time)
    return map(splitter, read(fname))


def load_tipps(fname):
    return {k: parse(v) for k, v in get_content(fname)}


def basename(fname):
    return os.path.splitext(os.path.basename(fname))[0]


def get_all_tipps(round_number):
    files = glob.glob("ro{}/tipps/*.txt".format(round_number))
    return {basename(fname): load_tipps(fname) for fname in files}


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
    return sum(score(tipps[match], result["result"]) for match, result in results.items())


def get_fname(rn):
    return "ro{}/results.txt".format(rn)


def get_standing(round_number):
    results = load_result(get_fname(rn))
    return {player: ROUND_MULTIPLICATOR[round_number] * total_points(tipps, results)
            for player, tipps in get_all_tipps(round_number).items()}


def get_all_rounds():
    for rn in ROUND_MULTIPLICATOR.keys():
        if os.path.isfile(get_fname(rn)):
            yield get_standing(rn)


def add_rounds(standings):
    overall = defaultdict(int)
    for standing in standings:
        for player, points in standing.items():
            overall[player] += points
    return overall

def time(tsring):
    return datetime.datetime.strptime(tsring + ' 2016', '%d %B %H.%M %Y') 

def round_to_df(rn):
        results = load_result(get_fname(rn))
        all_tipps = get_all_tipps(rn)

        matches = list(results.keys())
        times = [time(a['time']) for a in results.values()]
        df = pd.DataFrame(columns=all_tipps.keys(), index=[matches, times])

        for game, game_data in results.items():
            if game_data['result']:
                game_tipps = {player: ROUND_MULTIPLICATOR[rn]*score(players_tipp[game], game_data['result'])
                              for player, players_tipp in all_tipps.items()}

                df.loc[game, time(game_data['time'])] = game_tipps
        
        return df.swaplevel().sort_index().sort_index(axis=1)

def get_all_rounds():
    return pd.concat([round_to_df(rn) for rn in ROUND_MULTIPLICATOR.keys() if os.path.isfile(get_fname(rn))])


def update_data():


    df = get_all_rounds()

    sns.set_style('white')
    plt.xkcd()

    series = df.sum()
    colors = sns.color_palette("husl", len(series))
    ax = series.plot(kind="bar", rot=0, sort_columns=True, color=colors)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    fig = ax.get_figure()
    fig.suptitle("Aktuelles Ranking")
    plt.xlabel("Spieler")
    plt.ylabel("Punkte")
    fig.subplots_adjust(bottom=0.15)
    fig.savefig("standings.png")


    df = df.dropna()
    index = df.index.get_level_values(0)
    ax = df.cumsum().plot(x=index, kind='area', stacked=False, sort_columns=True, rot=0, color=colors)
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

    return df


if __name__ == "__main__":
    df =update_data()


