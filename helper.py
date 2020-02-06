import pandas as pd


def GetSizeBySN(SN):
    df = pd.read_csv("./obj_data/obj_info.csv")
    edges = df.iloc[SN - 1][1:4].to_numpy()
    return edges