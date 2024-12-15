#!/usr/bin/env python

##
# Global parameters
import os
DB_LOCATION = os.environ.get("PAPER_REL_DB")

##
# Load DB
import pandas
import numpy as np

try:
    df = pandas.read_hdf(DB_LOCATION, key='paper')
    print(f"Loaded {len(df.index)} entries")
except:
    print(f"\033[31mERROR\033[0m: Failed to open DB at [{DB_LOCATION}]")
    print("\033[31mABORTED\033[0m")
    exit()


print(df[["title"]])

for _, row in df.iterrows():
    print(row["title"])

# print(df[["key", "doi"]])
# print(df.loc[df['doi'] == "", 'ref'])