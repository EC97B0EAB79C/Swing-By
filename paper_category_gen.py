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
    'workspace',
    help='The directory of markdown files.'
    )
parser.add_argument(
    '--metatags',
    nargs="+",
    type=str,
    default=[]
    )

args = parser.parse_args()

##
# Read Files
# - Create dict of files and metadata
# - Create dict of tag occurrence

# Extract Markdown file metadata
import yaml
def extract_metadata(markdown):
    while markdown[0].strip() =='':
        markdown = markdown[1:]
    if '---' not in markdown[0].strip():
        return {}, ''.join(markdown)

    markdown = markdown[1:]
    for idx, line in enumerate(markdown):
        if '---' in line.strip():
            metadata_end = idx
            break

    metadata_text = ''.join(markdown[:metadata_end])
    metadata = yaml.safe_load(metadata_text)

    return metadata, ''.join(markdown[metadata_end+1:])

# Process files
import os
from pathlib import Path

def process_file(file):
    with open(file, 'r') as f:
        metadata, _ = extract_metadata(f.readlines())

    metadata['tags'] = list(filter(lambda t: t not in args.metatags, metadata['tags']))
    key = Path(file).stem

    return {key: metadata}

def process_files(files):
    file_metadata = {}
    for file in files:
        if ".md" not in file[-3:]:
            continue
        file_metadata.update(process_file(file))

    return file_metadata

def process_workspace(workspace):
    file_metadata = {}
    for (root, dirs, files) in os.walk(workspace):
        file_metadata.update(
            process_files(map(lambda file: os.path.join(root, file), files))
            )

    return file_metadata



##
# Process data
def get_tag_ranking(file_metadata)

# TODO

##
# Add process data to files

# TODO


file_metadata = process_workspace(args.workspace)

for key in file_metadata.keys():
    print(file_metadata[key]['tags'])
