import string
import glob
import os
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.ticker as ticker
import seaborn as sns
from operator import sub
from functools import partial
from itertools import repeat


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
    if len(line) > index + 1:
        result = line[index + 1]
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
        return np.nan  # match not played or no valid tipp

    elif tipp == result:
        return 3  # exact result

    elif sub(*result) * sub(*tipp) > 0 or (
            sub(*tipp) == 0 and sub(*result) == 0):  # correct winner(>0), oder correct draw(=0)
        return 1

    else:
        return 0


def get_fname(rn):
    return "ro{}/results.txt".format(rn)


def time(tsring):
    return datetime.datetime.strptime(tsring + ' 2016', '%d %B %H.%M %Y')


def round_to_df(rn):
    results = load_result(get_fname(rn))
    all_tipps = get_all_tipps(rn)

    matches = list(results.keys())
    times = [time(a['time']) for a in results.values()]
    columns = pd.MultiIndex.from_product([all_tipps.keys(), ['score', 'tipp']])
    df = pd.DataFrame(columns=columns, index=[matches, times])

    for game, game_data in results.items():
            game_scores = {(player, 'score'): ROUND_MULTIPLICATOR[rn] * score(players_tipp[game], game_data['result'])
                          for player, players_tipp in all_tipps.items()}

            game_tipps = {(player, 'tipp'): players_tipp[game] for player, players_tipp in all_tipps.items()}

            df.loc[game, time(game_data['time'])] = {**game_tipps, **game_scores}

    return df.swaplevel().sort_index().sort_index(axis=1)


def get_all_rounds():
    return pd.concat([round_to_df(rn) for rn in ROUND_MULTIPLICATOR.keys() if os.path.isfile(get_fname(rn))])


def next_games_tipps(df):
    unplayed = df[df.isnull().any(1)]
    return unplayed.swaplevel(axis=1)['tipp']


def update_plots(df):
    plotdf = df.swaplevel(axis=1)['score']

    sns.set_style('white')
    plt.xkcd()

    series = plotdf.sum()
    colors = sns.color_palette("husl", len(series))
    ax = series.plot(kind="bar", rot=0, sort_columns=True, color=colors)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    fig = ax.get_figure()
    fig.suptitle("Aktuelles Ranking")
    plt.xlabel("Spieler")
    plt.ylabel("Punkte")
    fig.subplots_adjust(bottom=0.15)
    fig.savefig("standings.png")

    plotdf = plotdf.dropna()
    index = plotdf.index.get_level_values(0)
    ax = plotdf.cumsum().plot(x=index, stacked=False, sort_columns=True, rot=0, color=colors)
    date1 = datetime.datetime(2016, 6, 10)
    date2 = datetime.datetime(2016, 7, 11)
    ax.xaxis.set_major_formatter(dates.DateFormatter('%d.%m'))
    ax.set_ylim([0, 1.1 * max(series)])
    ax.set_xlim(date1, date2)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    fig = ax.get_figure()
    fig.suptitle("Punkte vs Zeit")
    plt.xlabel("Datum")
    plt.ylabel("Punkte")
    fig.subplots_adjust(bottom=0.15)
    fig.savefig("standings_vs_time.png")


def update_indexhtml(df):
    lines = ["""<meta charset="UTF-8">""",
             """<link rel="stylesheet" href="style.css">""",
             """<h2>Ranking</h2><br><br>"""
             """<img src = "standings.png" > </img>""",
             """<img src = "standings_vs_time.png" > </img>""",
             """<h2>Nächste Tipps</h2><br><br>"""]

    def formatter(field):
        if field:
            fmt = "{} - {}".format(*field)
        else:
            fmt = field
        return fmt

    formatters = list(repeat(formatter, times=len(df.columns)))

    with open('index.html', 'w') as f:
        f.writelines("\n" + "\n".join(lines))
        f.write(df.to_html(justify='left', sparsify=True, col_space=60, formatters=formatters))


if __name__ == "__main__":
    df = get_all_rounds()
    update_plots(df)
    update_indexhtml(next_games_tipps(df))
