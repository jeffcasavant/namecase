#! /usr/bin/env python2
import sys

from time import sleep

import requests
import argparse

import Levenshtein
import re

import unicodedata

from titlecase import titlecase

def memoize(f):
    class memodict(dict):
        __slots__ = ()
        def __missing__(self, key):
            self[key] = ret = f(key)
            return ret
    return memodict().__getitem__

def levenshtein(a,b,caseSensitive=False):
    "Calculates the Levenshtein distance between a and b."

    # Convert unicode characters to their ascii matches 
    # (removes umlauts & accents for this comparison)
    # Pretend both strings are unicode for this conversion
    a = unicodedata.normalize('NFKD', unicode(a)).encode('ascii','ignore')
    b = unicodedata.normalize('NFKD', unicode(b)).encode('ascii','ignore')

    if not caseSensitive:
        a = a.lower()
        b = b.lower()

    return Levenshtein.distance(a,b)

@memoize
def standardizeName(name):

    if not name:
        return

    # Normalize the name
    name = name.upper().replace(' ', '')

    # API URL
    wikipediaAPI = 'http://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srprop=titlesnippet&srsearch=%s'

    result = requests.get(wikipediaAPI % name)

    # Remove non alphanumeric & space characters from each title
    titles = [re.sub(r'[^a-zA-Z0-9 \-\']','',article['title']) for article in result.json()['query']['search']]

    # Titlecase if we got no answer
    if not titles:
        return titlecase(name)

    # If we did, pick the best one based on levenshtein distance
    levSensitive = {}
    levInsensitive = {}
    for title in titles:
        # Calculate both case sensitive and case insensitive distance
        levSensitive[title] = levenshtein(name, title, caseSensitive=True) / float(len(name))
        levInsensitive[title] = levenshtein(name, title) / float(len(name))
    
    # Weighted average (weighted towards case insensitive since we are looking for proper capitalization)
    weighted = [(title, (levSensitive[title] * .15 + levInsensitive[title] * .85)) for title in titles]
    weighted.sort(key=lambda x: x[1])

    bestMatch = weighted[0][0]

    # Verify that the best match does in fact contain the name we want
    if name.replace(' ', '').lower() not in re.sub(r'[^a-zA-Z0-9]','', bestMatch.lower()):
        # If not, titlecase
        return titlecase(name)

    # Find the name in the title (handling cases like "Vananda, Montana" for Vananda)
    levPartialTitle = [(index, levenshtein(name, part)) for index, part in enumerate(bestMatch.split())]
    levPartialTitle.sort(key=lambda x: x[1])

    bestMatch = bestMatch.split()

    # Pull the name itself off of our best match
    finalName = bestMatch[levPartialTitle[0][0]]
    bestMatch = bestMatch[:levPartialTitle[0][0]]

    while len(finalName) < len(name):
        # If the name is too short, pull the previous word from the title (e.g. Beek -> Van Beek)
        # Be sure there's one to pull; if we've somehow lost letters, try the apostropher version
        if bestMatch:
            finalName = bestMatch[-1] + ' ' + finalName
            bestMatch = bestMatch[:-1]
        else:
            return titlecase(name)

    # If we've gotten all upper case or all lowercase, or if the name doesn't match at all
    # try the apostrophe version
    if finalName.isupper() or finalName.islower() or levenshtein(name.upper().replace(' ', ''), finalName.upper().replace(' ', '')):
        if not ("'" in name or "'" in finalName or "-" in name or "-" in finalName):
            return titlecase(name)

    # And if we made it this far we obviously have a good result
    return finalName

if __name__ == '__main__':

    #### Handle different methods of input

    parser = argparse.ArgumentParser()

    # This allows us to take input from a file or from stdin (defaults to stdin)
    parser.add_argument("--input",
                        type=argparse.FileType("r"),
                        default="-",
                        help="Input stream/file")

    parser.add_argument("--start")

    parser.add_argument("--name")

    parser.add_argument("--lev1")
    parser.add_argument("--lev2")

    args = parser.parse_args()

    #### Parse input
    if args.lev1 and args.lev2:
        print levenshtein(args.lev1, args.lev2)
    elif not args.name:
        printing = False
        for line in args.input.readlines():
            line = line.strip()
            if args.start:
                if not printing:
                    if line.lower() >= args.start.lower():
                        printing = True
                    else:
                        continue
            name = standardizeName(line)
            print '%30s: %30s' % (line, name)
            sleep(0.1)
    else:
        print '%s: %s' % (args.name, standardizeName(args.name))
