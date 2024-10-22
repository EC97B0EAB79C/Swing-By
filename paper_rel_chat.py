#!/usr/bin/env python

##
# Global parameters
import os
DB_LOCATION = os.environ["PAPER_REL_DB"]

##
# Load DB
import pandas
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


try:
    df = pandas.read_hdf(DB_LOCATION, key='df')
    print(f"Loaded {len(df.index)} entries")
except:
    print(f"\033[31mERROR\033[0m: Failed to open DB at [{DB_LOCATION}]")
    print("\033[31mABORTED\033[0m")
    exit()


df['similarity'] = df['embedding_body'].apply(lambda x: np.dot(x,df['embedding_body'][0]).flatten()[0])
print(df["similarity"])