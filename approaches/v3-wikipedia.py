#! /usr/bin/env python2
import sys

import requests
import argparse

import Levenshtein
import re

def levenshtein(a,b,caseSensitive=False):
    "Calculates the Levenshtein distance between a and b."

    a = unicode(a)
    b = unicode(b)

    if not caseSensitive:
        a = a.lower()
        b = b.lower()

    return Levenshtein.distance(a,b)

def standardizeName(name):

    if not name:
        return

    wikipediaAPI = 'http://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srprop=titlesnippet&srsearch=%s'

    result = requests.get(wikipediaAPI % name)

    titles = [re.sub(r'[^a-zA-Z0-9 ]','',article['title']) for article in result.json()['query']['search'] if name.lower() in article['title'].lower().replace(' ', '')]

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

    # Find the name in the title (handling cases like "Vananda, Montana" for Vananda)
    levPartialTitle = [(index, levenshtein(name, part)) for index, part in enumerate(bestMatch.split())]
    levPartialTitle.sort(key=lambda x: x[1])

    bestMatch = bestMatch.split()

    # Pull the name itself off of our best match
    finalName = bestMatch[levPartialTitle[0][0]]
    bestMatch = bestMatch[:levPartialTitle[0][0]]

    while len(finalName) < len(name):
        # Pull the next particle off of our best match
        finalName = bestMatch[-1] + ' ' + finalName
        bestMatch = bestMatch[:-1]

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

    parser.add_argument("--lev1")
    parser.add_argument("--lev2")

    parser.add_argument("--debug",
                        action="store_true",
                        default=False)

    args = parser.parse_args()

    #### Parse input
    if args.lev1 and args.lev2:
        print levenshtein(args.lev1, args.lev2)
    elif not args.name:
        for line in args.input.readlines():
            print standardizeName(line)
    else:
        print '%s: %s' % (args.name, standardizeName(args.name))
