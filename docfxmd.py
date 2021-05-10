#!/usr/bin/env python3

import yaml


def load_file(fname):
    with open(fname, 'r') as file:
        return yaml.load(file.read(), Loader=yaml.Loader)

if __name__ == '__main__':
    data = load_file('test.yml')
    print(data)
