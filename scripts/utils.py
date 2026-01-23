import pandas as pd
import matplotlib.pyplot as plt
import plot_likert
import pingouin as pg

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

# function for plotting the likert plots for the attitude questions
def likert_plot_attitudes(ee_data, cg_data, attitude):
    likert = likert = range(1, 8)
    likert_values = ["Strongly Disagree", "Disagree", "Somewhat Disagree", "Neutral", "Somewhat Agree", "Agree", "Strongly Agree"]

    fig, (ax1, ax2) = plt.subplots(2, 1, constrained_layout=True, sharey=True) # draw two plots in one row, two columns

    plot_likert.plot_likert(ee_data[attitude], likert, plot_percentage=True, colors=plot_likert.colors.likert7, bar_labels=True, ax=ax1, legend=False)
    plot_likert.plot_likert(cg_data[attitude], likert, plot_percentage=True, colors=plot_likert.colors.likert7, bar_labels=True, ax=ax2, legend=False)

    fig.suptitle(f"{attitude} in ethics")
    ax1.set_title("EE courses")
    ax2.set_title("Control group courses")

    handles, labels = ax2.get_legend_handles_labels()
    fig.legend(handles, likert_values, bbox_to_anchor=(1.34, 0.90))
    plt.show()


# function for checking equal variance between two groups of data
def equal_var_test(data, var_list):
    '''
    Docstring for equal_var_test
    
    :param data: a list of the dataframes for which we want to get the variance of.
    :param var_list: Description
    '''
    # put data in correct format

    equal_var = pd.DataFrame()
    for var in var_list:
        data_formatted = []
        for d in data:
            data_formatted.append(d[var].to_numpy())
        equal_var_test = pg.homoscedasticity(data=data_formatted, method="levene")
        equal_var = pd.concat([equal_var, equal_var_test])

    equal_var.index = var_list # change index to be the attitudes
    return equal_var


def ttest(ee_data, cg_data, var_list):
    '''
    Performs both the parametric and non-parametric t-test and returns them in that order
    '''
    ttest_avg = pd.DataFrame()
    mwu_avg = pd.DataFrame()
    ttest_stars = []
    mwu_stars = []

    for var in var_list:
        t_test = pg.ttest(ee_data[var], cg_data[var])
        mwu_test = pg.mwu(ee_data[var], cg_data[var])

        ttest_stars.append(p_val_star(t_test["p-val"].values[0])) # take index 0 cause only one element at a time
        mwu_stars.append(p_val_star(mwu_test["p-val"].values[0])) # take index 0 cause only one element at a time

        ttest_avg = pd.concat([ttest_avg, t_test])
        mwu_avg = pd.concat([mwu_avg, mwu_test])

    # set the index as the attitudes
    ttest_avg.index = var_list
    mwu_avg.index = var_list

    ttest_avg.insert(4, "significance", ttest_stars)
    mwu_avg.insert(3, "significance", mwu_stars)

    return ttest_avg, mwu_avg


def anova(data, groups, var_list):
    '''
    Performs both the parametric and non-parametric anova and returns them in that order
    '''
    aov = pd.DataFrame()
    welch = pd.DataFrame()
    aov_stars = []
    welch_stars = []

    for var in var_list:
        aov_var = pg.anova(data=data, dv=var, between=groups)
        welch_var = pg.welch_anova(data=data, dv=var, between=groups)

        aov_stars.append(p_val_star(aov_var["p-unc"].values[0])) # take index 0 cause only one element at a time
        welch_stars.append(p_val_star(welch_var["p-unc"].values[0])) # take index 0 cause only one element at a time

        aov = pd.concat([aov, aov_var])
        welch = pd.concat([welch, welch_var])

    # set the index as the attitudes
    aov.index = var_list
    welch.index = var_list

    aov.insert(4, "significance", aov_stars)
    welch.insert(3, "significance", welch_stars)

    return aov, welch

def anova_post_hoc(data, groups, var_list, aov_data, parametric=True):
    posthoc_list = {}
    stars = []
    for var in var_list:
        if aov_data["p-unc"][var] < 0.05:
            if parametric:
                posthoc = pg.pairwise_tukey(data=data, dv=var, between=groups)
            else:
                posthoc = pg.pairwise_gameshowell(data=data, dv=var, between=groups)

            stars = posthoc["pval"].apply(p_val_star)
            #stars.append(p_val_star(posthoc["pval"])) # take index 0 cause only one element at a time
            posthoc.insert(9, "significance", stars)
            posthoc_list[var] = posthoc

    return posthoc_list


# function for converting p-values to stars
def p_val_star(p):
    stars = "ns"
    if 0.01 < p and p <= 0.05:
        stars = "*"
    elif 0.001 < p and p <= 0.01:
        stars = "**"
    elif p <= 0.001:
        stars = "***"
    return stars
        

# function for plotting the percentages and n values on pie chart (credits: stackoverflow)
def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{:.1f}%({v:d})'.format(pct, v=val)
    return my_format