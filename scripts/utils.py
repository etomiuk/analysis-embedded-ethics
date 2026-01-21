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


# function for plotting the percentages and n values on pie chart (credits: stackoverflow)
def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{:.1f}%({v:d})'.format(pct, v=val)
    return my_format