import string
import glob
import os


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
        content = map(split, filter(lambda x: len(x) > 0, content))
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

    elif tipp == 0 and result == 0:  # correct winner(>0), oder correct draw(=0)
        return 1

    else:
        return 0

def total_points(tipps, results):
    return sum(score(tipps[match], result) for match, result in results.items())

def get_standing(round_number):
    results = load_tipps("ro{}/results.txt".format(round_number))
    return {player: total_points(tipps, results) for player, tipps in get_all_tipps(round_number)}


if __name__ == "__main__":
    print(get_standing(36))
