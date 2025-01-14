
# DB_LOCATION = os.environ.get("PAPER_REL_DB")
DB_LOCATION = "./test/test.h5"

import pandas
import numpy as np

try:
    df = pandas.read_hdf(DB_LOCATION, key='paper')
    print(f"Loaded {len(df.index)} entries")
except:
    print(f"\033[31mERROR\033[0m: Failed to open DB at [{DB_LOCATION}]")
    print("\033[31mABORTED\033[0m")
    exit()



for _, row in df.iterrows():
    print(row["key"], row["ref"])

