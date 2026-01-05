import pandas as pd

def rebuild_multiindex(d):
    '''
    Recreates the MultiIndex dataframe with the correct column names.
    
    :param d: pandas dataframe with MultiIndex columns
    :return: None (modifies dataframe in place)
    '''
    new_cols = []
    for col in d.columns:
        if "Unnamed" in col[1]:
            new_cols.append((col[0], ""))
        else:
            new_cols.append(col)

    d.columns = pd.MultiIndex.from_tuples(new_cols)