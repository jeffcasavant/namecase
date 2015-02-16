#! /usr/bin/env python2
import sys

import requests
import argparse

def levenshtein(a,b,caseSensitive=False):
    "Calculates the Levenshtein distance between a and b."

    if not caseSensitive:
        a = a.lower()
        b = b.lower()

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

    if not name:
        return

    wikipediaAPI = 'http://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srprop=titlesnippet&srsearch=%s'

    result = requests.get(wikipediaAPI % name)

    titles = [article['title'] for article in result.json()['query']['search'] if name.lower() in article['title'].lower().replace(' ', '')]

    # Titlecase if we didn't get an answer
    if not titles:
        return name.title()

    # If we did, pick the best one based on levenshtein distance
    levSensitive = {}
    levInsensitive = {}
    for title in titles:
        levSensitive[title] = levenshtein(name, title, caseSensitive=True) / float(len(name))
        levInsensitive[title] = levenshtein(name, title) / float(len(name))

    weighted = [(title, (levSensitive[title] * .15 + levInsensitive[title] * .85)) for title in titles]

    weighted.sort(key=lambda x: x[1])

    for match in weighted:
        bestMatch = match[0]

        if name.replace(' ', '').lower() in bestMatch.replace(' ', '').lower():
            break

    finalName = ''
    while len(finalName) < len(name):
        finalName = bestMatch.split()[-1] + ' ' + finalName
        bestMatch = ' '.join(bestMatch.split()[:-1])

    print name + ': ',

    return finalName

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
