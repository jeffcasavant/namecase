#! /usr/bin/env python2
import sys

import requests
import argparse

def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
                current[j] = min(add, delete, change)
                        
    return current[n]

def standardizeName(name):

    wikipediaAPI = 'http://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srprop=titlesnippet&srsearch=%s'

    result = requests.get(wikipediaAPI % name)

    titles = [article['title'] for article in result.json()['query']['search']]

    lev = []
    for title in titles:
        lev.append((title, levenshtein(name, title)))

    print lev.sort(key=lambda x: x[1])

    print lev

if __name__ == '__main__':

    #### Handle different methods of input

    parser = argparse.ArgumentParser()

    # This allows us to take input from a file or from stdin (defaults to stdin)
    parser.add_argument("--input",
                        type=argparse.FileType("r"),
                        default="-",
                        help="Input stream/file")

    parser.add_argument("--name")

    parser.add_argument("--debug",
                        action="store_true",
                        default=False)

    args = parser.parse_args()

    #### Parse input
    if not args.name:
        for line in args.input.readlines():
            print standardizeName(line)
    else:
        print standardizeName(args.name)
