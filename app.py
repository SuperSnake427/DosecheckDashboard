#############################################################################################
#
# Create a dashboard to visualize the DoseCheck database
# 
# Drew Hall (drewhall@ucsd.edu)
#
#
# Notes:
#
#
# Revision History:
#   - 19 Oct 2023 -- DAH -- Initial coding
#
# References:
#    - https://medium.com/@max.lutz./how-to-build-a-data-visualization-page-with-streamlit-4ca4999eba64
#
#############################################################################################
import streamlit as st
import pandas as pd
import numpy as np
#import gspread
#from pathlib import Path
import matplotlib.pyplot as plt

#REMOTE_DATABASE_URL = 'https://docs.google.com/spreadsheets/d/1FgGdpDp5uR22m-37YVRNk4FWufgAQS1NYAYKwUnMdUk/edit#gid=1034852951'
REMOTE_DATABASE_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTUPZCGv471mBayU1mLe5DLkVkoxF6K9I5f16kFVh5vPF-3MpMmgxjQOWqA_sYWsGXr60xCeeNmFGSr/pub?output=csv'
LOCAL_DATABASE_FILENAME = r'./data/UnknownDatabase.xlsx'

drug_grouping = {   'Fentanyl-like': ['Fentanyl', "2'-Fluorofentanyl",	"2'-Methyl fentanyl",	'Acetyl fentanyl',	'Benzyl fentanyl',	'Despropionyl fentanyl (4-ANPP)',	'Fentanyl (hydroxy)',	'Furanylethyl fentanyl',	
                    'Methyl acetyl fentanyl', 'N-(2C-C) fentanyl', 'N-(2C-D) fentanyl',	'N-Methyl norfentanyl',	'N-methyl fentanyl',	'N-methyl norfentanyl',	'Norfentanyl',	'Phenethyl 4-ANPP'],
                    'MDMA-like': ['MDMA', 'MDA',	'2,3 MDMA',	'3,4-Dimethoxyamphetamine',	'Amphetamine',	'MBDB',	'MDA 2-aldoxime analogue',	'MDDMA',	'MDEA',	'MMDPPA', 'N-formyl-MDA'],
                    'Heroin-like': ['Heroin',	'6-MAM',	'Acetyl codeine'],
                    'Cocaine-like': ['Cocaine',	'Anhydroecgonine methyl ester (AEME)',	'Benzoylecgonine',	'Benzoylecgonine ethyl ester',	'Ecgonine',	'Ecgonine methyl ester (EME)',	'Methylecgonine',	'Pseudoecgonine methyl ester',	'Tropacocaine'],
                    'Keatmine-like': ['Ketamine', 'Deschloroketamine',	'Ketamine isomer',	'Ketamine-related',	'Norketamine'],
                    'Carfentanil-like': ['Carfentanil'],
                    'Nitazene-class opioids': ['5-Aminoisotonitazene',	'Etodesnitazene',	'Etonitazepyne',	'Isotonitazene/protonitazene'],
                    'Xylazine-like': ['Xylazine']
                    }

@st.cache_data
def load_local_data() -> pd.DataFrame:
    '''
    Load the data locally
    Parameters:
        - None
        
    Returns:
        - dataframe: 
    '''
    return pd.read_excel(Path(LOCAL_DATABASE_FILENAME))

@st.cache_data
def load_remote_data() -> pd.DataFrame:
    #gc = gspread.service_account('credentials.json')
    #gc = gspread.service_account()
    #worksheet = gc.open_by_url(REMOTE_DATABASE_URL)
    #sheet = worksheet.sheet1
    #data = sheet.get_all_records()
    #df = pd.DataFrame(data)
    
    return pd.read_csv(REMOTE_DATABASE_URL)

def cleanup_data(df) -> pd.DataFrame:
    # Drop rows without a filename 
    df['filename'].replace('', np.nan, inplace=True)
    df.dropna(subset=['filename'], inplace=True)

    # Fixup the date
    df['Date Checked'] = pd.to_datetime(df['Date Checked'], infer_datetime_format=True)

    df.set_index('ID', inplace=True)

    return df

def group_drugs(df, groupings) -> pd.DataFrame:
    '''
    Combine different drug categories together

    Parameters:
        - df: Dataframe with all drugs
        - groupings: dictionary with columns to combine and new name

    Returns:
        - Dataframe with reduced drugs
    '''
    for drug_class, drug_list in groupings.items():
        # Combine
        df[drug_class] = df[drug_list].any(axis=1)
        # Drop
        df = df.drop(columns=drug_list)

    return df

def plot_drug_histogram(df, items):
    '''
    Plot a histogram of drug types

    Parameters:
        - 
    
    Returns:
    
    '''
    # Count the number of non-zero items in each column
    drug_counts = df[items].astype(bool).sum()
    
    st.subheader('Street drugs checked')
    st.bar_chart(drug_counts)#.set_index('Category')

def plot_timecourse(df, items):
    # Set the Date column as the index
    df.set_index('Date Checked', inplace=True)

    # Note: The dataframe has only True/False -- so count() will return the same number for all. Sum is correct.
    # Requantize the data to 3 months
    df_monthly = df.resample('3M')[items].sum()

    st.subheader('Time Series Data')
    st.line_chart(df_monthly[items])

def plot_site_distribution(df):
    # Count the number of occurances for each of the sites
    counts = df['Site'].value_counts()

    # Make a plot in Matplotlib, then display it with Streamlit
    fig, ax = plt.subplots()
    ax.pie(list(counts), labels=list(counts.index), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.subheader('Testing Site')
    st.pyplot(fig)
    
# Load the data
#data = load_local_data()
data = load_remote_data()
data = cleanup_data(data)
data_cleaned = group_drugs(data, drug_grouping)

st.title('DoseCheck Dashboard')
plot_drug_histogram(data_cleaned, list(drug_grouping.keys()))
plot_timecourse(data_cleaned, list(drug_grouping.keys()))
plot_site_distribution(data_cleaned)