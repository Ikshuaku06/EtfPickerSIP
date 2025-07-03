import streamlit as st
import sys
import os

# from Config import read_config as rc
from Config import read_config as rc

def main():
    st.title("Welcome to ETF Tracker Picker")
    menu = ["View ETF tracker", "Edit Decided Quantity"]
    choice = st.sidebar.selectbox("Navigation", menu)

    etf_list = rc.get_etf_list()
    qty_list = rc.get_decided_quantities()

    from utilities import utils
    import pandas as pd

    if choice == "View ETF tracker":
        # Prepare data for table
        data = []
        for i, etf in enumerate(etf_list):
            price = utils.get_current_value(etf)
            prev_close = utils.get_previous_close(etf)
            qty = qty_list[i] if qty_list and i < len(qty_list) else ''
            data.append({"ETF": etf, "Current Price": price, "Previous Close": prev_close, "Decided Quantity": qty})

        df = pd.DataFrame(data)
        df.index = df.index + 1  # Make index start from 1

        def highlight_price(row):
            current = row["Current Price"]
            prev = row["Previous Close"]
            if pd.isna(current) or pd.isna(prev):
                return ["" for _ in row]
            if current > prev:
                color = "background-color: lightgreen"
            elif current < prev:
                color = "background-color: salmon"
            else:
                color = "background-color: yellow"
            return [color if col in ["Current Price"] else "" for col in row.index]

        st.dataframe(
            df.style.apply(highlight_price, axis=1),
            use_container_width=True
        )

    elif choice == "Edit Decided Quantity":
        st.header("Edit Decided Quantity")
        new_qty = []
        for i, etf in enumerate(etf_list):
            val = st.text_input(f"{etf} quantity", value=qty_list[i] if qty_list and i < len(qty_list) else "")
            new_qty.append(val)
        if st.button("Save Quantities"):
            rc.set_decided_quantities(new_qty)
            st.success("Decided quantities updated!")


if __name__ == "__main__":
    main()