#! /usr/bin/env python2
import sys

import argparse

from titlecase import titlecase

def standardizeName(name):
    name = titlecase(name)

    ## Generic rules applied first so they can be overridden
    # Arbitrary dashes, e.g. Smythington-Smythe-Smith
    newName = []
    for namePart in name.split():
        if '-' in namePart:
            namePart = titlecase(namePart.replace('-', ' ')).replace(' ', '-')
        newName.append(namePart)

    name = ' '.join(newName)

    # All of these particles & prefixes should be written here with proper capitalization
    # http://en.wikipedia.org/wiki/Nobiliary_particle
    # http://stylemanual.ngs.org/home/D/de-d-etc
    # Assumptions:
    #  - If a particle can be written both ways, I have chosen to use the lowercase (which shows that we know it's not a middle name)

    # Since prefixes will also match particles, apply them next so they can be overridden

    prefixes = ["Mac",      # Amy MacDonald                 -- note we will get this one wrong; she uses Amy Macdonald
                "Mc",       # Ronald McDonald
                "d'",       # Ferdinand d'Orleans
                "l'",       # Pierre l'Enfant
                "O'",       # Peter O'Toole
                "al-"]      # Haroun al-Rasheed


    newName = []
    for namePart in name.split():
        for prefix in prefixes:
            # If the prefix is the first thing in the namePart
            if prefix.lower() == namePart.lower()[:len(prefix)]:
                # Remove the prefix
                namePart = namePart.lower()[len(prefix):]
                # Capitalize the next letter
                namePart = namePart.title()
                # Add the prefix back again
                namePart = prefix + namePart
        newName.append(namePart)

    name = ' '.join(newName)

    # Particles last since they are the most specific

    particles = ["van",     # Netherlands
                 "tot",     #
                 "thoe",    #
                 "aw",      # Somalia
                 "der",     # James van der Beek
                 "von",     # Ludwig von Beethoven
                 "zu",      # Gottfried Heinrich Graf zu Pappenheim
                 "di",      # Emilia di Martino
                 "da",      # Leonardo da Vinci
                 "de",      # Guy de Maupassant
                 "do",      # Portuguese alternate forms of 'de'
                 "dos",     #
                 "da",      #
                 "das",     #
                 "bin",     # Osama bin Laden
                 "ben",     # Ahmed ben Bella
                 "bint",    # 
                 "binte",   #
                 "ibn",     # Hind ibn Sheik                -- this should technically not show up as part of a full name; but if it does we keep it
                 "abu",     #                               -- also unlikely 
                 "af",      # Bredo von Munthe af Morgenstierne
                 "av",      # Modern Swedish af
                 "du",      # Bertrand du Guesclin
                 "na",      # Thailand
                 "la",      #
                 "Le",      # French alternate forms of 'la'
                 "Les"]     #

    newName = []
    name = name.split()
    for namePart in name:
        for particle in particles:
            # This will only handle already separated particles; Luther Vandross is not Luther van Dross
            # Also, do not consider it a particle if it is the first or last word (Van Morrison)
            if particle.lower() == namePart.lower() and namePart is not name[0] and namePart is not name[-1]:
                namePart = particle
        newName.append(namePart)

    name = ' '.join(newName)

    return name

if __name__ == '__main__':

    #### Handle different methods of input

    parser = argparse.ArgumentParser()

    # This allows us to take input from a file or from stdin (defaults to stdin)
    parser.add_argument("--input",
                        type=argparse.FileType("r"),
                        default="-",
                        help="Input stream/file")

    parser.add_argument("--debug",
                        action="store_true",
                        default=False)

    args = parser.parse_args()

    #### Parse input
    for line in args.input.readlines():
        print standardizeName(line)
