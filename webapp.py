import streamlit as st
import sys
import os

# from Config import read_config as rc
from Config import read_config as rc

def main():
    st.title("Welcome to ETF Tracker Picker")
    etf_list = rc.get_etf_list()

    from utilities import utils
    import pandas as pd

    # Prepare data for table
    data = []
    for etf in etf_list:
        price = utils.get_current_value(etf)
        data.append({"ETF": etf, "Current Price": price})

    df = pd.DataFrame(data)
    df.index = df.index + 1  # Make index start from 1
    st.table(df)


if __name__ == "__main__":
    main()