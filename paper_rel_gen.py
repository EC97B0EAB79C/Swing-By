#!/usr/bin/env python
import argparse

parser = argparse.ArgumentParser(
    prog='paper_rel_gen',
    description='Processes markdown notes with BibTeX to add metadata to paper notes.'
    )
parser.add_argument(
    'filename',
    help='Markdown file to process.'
    )
parser.add_argument(
    '-i',
    '--ignore-bibtex',
    action='store_true'
    )
args = parser.parse_args()




print(args)

