def load_strengths(fname):
    with open(fname) as f:
        content = f.readlines()
    strengths = {k:float(v) for k,v in map(lambda str: str.split(','), content)}
    return strengths

if __name__ == "__main__":
    print(load_strengths('uefa_koef.csv'))
