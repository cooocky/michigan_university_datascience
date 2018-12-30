#!/usr/bin/env python
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[2]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[3]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[4]:


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    df_list = []
    
    with open('university_towns.txt') as f:
        for line in f:
            if '[edit]' in line:
                state = line
            else:
                df_list.append([state, line])
    
    df = pd.DataFrame(df_list, columns=['State', 'RegionName'])
    df['State'].replace('\[.*$', '', regex=True, inplace=True)
    df['State'].replace('\n', '', regex=True, inplace=True)
    df['RegionName'].replace(' \(.*$', '', regex=True, inplace=True)
    df['RegionName'].replace('\n', '', regex=True, inplace=True)
    
    return df

get_list_of_university_towns().head()


# In[5]:


def get_df():
    df = pd.read_excel('gdplev.xls', skiprows=219, usecols=[4,6])
    df.columns=['quarter', 'value']
    return df

def get_sequence_end(ds, start, check):
    first = ds.iloc[start]
    second = ds.iloc[start + 1]

    for i in range(start + 2, len(ds)):
        third = ds.iloc[i]
        if check (third, second, first):
            break
        first, second = second, third

    return i

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a
    string value in a format such as 2005q3'''

    df = get_df()
    ind = get_sequence_end(df['value'], 0, lambda a,b,c: a < b < c) - 1
    return df['quarter'].iloc[ind]

get_recession_start()


# In[6]:


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a
    string value in a format such as 2005q3'''

    df = get_df()
    start = get_sequence_end(df['value'], 0, lambda a,b,c: a < b < c) - 2
    ind = get_sequence_end(df['value'], start, lambda a,b,c: a > b > c)
    return df['quarter'].iloc[ind]

get_recession_end()


# In[7]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a
    string value in a format such as 2005q3'''

    df = get_df()
    df.set_index('quarter', inplace=True)
    return df.iloc[df.index.get_loc(get_recession_end()) - 2].name

get_recession_bottom()


# In[8]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].

    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.

    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''

    df = pd.read_csv('City_Zhvi_AllHomes.csv')

    for i in range(2000, 2017):
        year_df = df[[c for c in df.columns if c[:4] == str(i)]]

        for quarter in range(1, 5):
            df[str(i) + 'q{}'.format(quarter)] = year_df[[c for c in year_df.columns if (quarter - 1) * 3 < int(c[5:]) <= quarter * 3]].mean(axis=1)

    df = df[['State', 'RegionName'] + [c for c in df.columns if c[4] == 'q']].drop('2016q4', axis=1)
    df['State'] = df['State'].map(states)
    df.set_index(['State', 'RegionName'], inplace=True)

    return df

convert_housing_data_to_quarters().head()


# In[9]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values,
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence.

    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''

    prices = convert_housing_data_to_quarters()
    start = get_recession_start()
    bottom = get_recession_bottom()

    prices = prices[[start, bottom]]
    prices['diff'] = prices.apply(lambda row: row[start] - row[bottom], axis=1)
    prices = prices.reset_index()

    uni = set(get_list_of_university_towns()['RegionName'])
    prices['is_uni'] = prices.apply(lambda row: row['RegionName'] in uni, axis=1)
    uni_prices = prices[prices['is_uni'] == True]['diff']
    non_uni_prices = prices[prices['is_uni'] == False]['diff']

    p = ttest_ind(non_uni_prices, uni_prices, nan_policy='omit').pvalue
    different = True if p < 0.01 else False
    better = 'university town' if uni_prices.mean() < non_uni_prices.mean() else 'non-university town'

    return (different, p, better)

run_ttest()

