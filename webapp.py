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
    for idx, etf in enumerate(etf_list, start=1):
        price = utils.get_current_value(etf)
        data.append({"S.No.": idx, "ETF": etf, "Current Price": price})

    df = pd.DataFrame(data)
    st.table(df.reset_index(drop=True))


if __name__ == "__main__":
    main()