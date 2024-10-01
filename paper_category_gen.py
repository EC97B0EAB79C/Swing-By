#!/usr/bin/env python

##
# Global parameters

##
# Argement Parser
import re
import argparse

parser = argparse.ArgumentParser(
    prog='paper_category_gen',
    description='Reads tags from markdown files and categorise.'
    )
parser.add_argument(
    'workdapce',
    help='The directory of markdown files.'
    )

args = parser.parse_args()

