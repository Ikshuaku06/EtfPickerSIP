import streamlit as st
from datetime import datetime
import pytz

# from Config import read_config as rc
from Config import read_config as rc
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd

def main():
    # Set Streamlit page config to wide mode
    st.set_page_config(layout="wide")

    # Show current date in IST at the top, centered and only date
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    st.markdown(f"<h3 style='text-align: center;'>{now_ist.strftime('%A, %d %B %Y')}</h3>", unsafe_allow_html=True)

    st.title("Welcome to ETF Tracker Picker")
    menu = ["View ETF tracker", "Edit Decided Quantity"]
    if "nav_choice" not in st.session_state:
        st.session_state.nav_choice = menu[0]
    choice = st.sidebar.selectbox("Navigation", menu, key="nav_choice")

    etf_list = rc.get_etf_list()
    qty_list = rc.get_decided_quantities()
    traded_qty_list = rc.get_traded_quantities()

    from utilities import utils

    if choice == "View ETF tracker":
        # --- Daily traded quantity logic ---
        today_str = now_ist.strftime('%Y-%m-%d')
        # Load original traded quantity at the start of the day
        if 'traded_qty_original' not in st.session_state or st.session_state.get('traded_qty_day_date') != today_str:
            st.session_state.traded_qty_original = [int(q) for q in traded_qty_list]
            st.session_state.traded_qty_day_date = today_str
            st.session_state.traded_qty_incremented = [False] * len(etf_list)

        traded_qty = st.session_state.traded_qty_original.copy()
        incremented = st.session_state.traded_qty_incremented.copy()

        for i, etf in enumerate(etf_list):
            try:
                curr = float(utils.get_current_value(etf))
                prev = float(utils.get_previous_close(etf))
                dec = int(qty_list[i]) if qty_list and i < len(qty_list) else 0
            except:
                continue
            if curr < prev and not incremented[i]:
                traded_qty[i] += dec
                incremented[i] = True
            elif curr > prev and incremented[i]:
                traded_qty[i] = st.session_state.traded_qty_original[i]
                incremented[i] = False
        st.session_state.traded_qty_incremented = incremented

        # Use this for display and persistence
        traded_qty_list = [str(q) for q in traded_qty]

        # Prepare data for table
        data = []
        for i, etf in enumerate(etf_list):
            price = utils.get_current_value(etf)
            prev_close = utils.get_previous_close(etf)
            qty = qty_list[i] if qty_list and i < len(qty_list) else ''
            traded_qty = traded_qty_list[i] if traded_qty_list and i < len(traded_qty_list) else ''
            data.append({
                "ETF": str(etf),
                "Current Price": price if price is not None else "",
                "Previous Close": prev_close if prev_close is not None else "",
                "Decided Quantity": str(qty),
                "Traded Quantity": str(traded_qty),
                "Bought": "Not Bought"
            })
        df = pd.DataFrame(data)
        # Only cast non-numeric columns to string
        for col in ["ETF", "Decided Quantity", "Traded Quantity", "Bought"]:
            df[col] = df[col].astype(str)
        if "index" in df.columns:
            df = df.drop(columns=["index"])
        df = df.fillna("").reset_index(drop=True)

        if not df.empty:
            # Convert 'Bought' to boolean for checkbox editing
            df['Bought'] = False

            # Add emoji to Curr Price for display, with 2 decimal places
            def price_with_emoji(row):
                try:
                    current = float(row['Current Price'])
                    prev = float(row['Previous Close'])
                    current_fmt = f"{current:.2f}"
                    if current > prev:
                        return f"{current_fmt} 📈"
                    elif current < prev:
                        return f"{current_fmt} 📉"
                    else:
                        return f"{current_fmt} ="
                except:
                    return row['Current Price']
            df['Curr Price'] = df.apply(price_with_emoji, axis=1)

            # Add a style column for coloring Current Price
            def price_color(row):
                try:
                    current = float(row['Current Price'])
                    prev = float(row['Previous Close'])
                    if current > prev:
                        return 'background-color: #b6fcb6; color: #006400; font-weight: bold;'
                    elif current < prev:
                        return 'background-color: #ffb3b3; color: #b30000; font-weight: bold;'
                    else:
                        return 'background-color: #fff7b3; color: #b38f00; font-weight: bold;'
                except:
                    return ''
            styled_df = df.style.apply(lambda x: [price_color(x)], axis=1, subset=['Curr Price'])

            # Use session state to persist table edits
            if 'etf_table' not in st.session_state:
                st.session_state.etf_table = df[["ETF", "Curr Price", "Previous Close", "Decided Quantity", "Traded Quantity", "Bought"]].copy()

            # Show editable table
            edited_df = st.data_editor(
                st.session_state.etf_table,
                column_config={
                    "Bought": st.column_config.CheckboxColumn(
                        "Bought",
                        help="Mark as bought",
                        default=False
                    ),
                    "Decided Quantity": st.column_config.NumberColumn(
                        "Decided Quantity",
                        help="Edit decided quantity",
                        min_value=0,
                        step=1
                    )
                },
                use_container_width=True,
                hide_index=True,
                key="etf_data_editor"
            )

            # Button to set Traded Quantity to 0 for checked ETFs
            if st.button("Set Traded Quantity to 0 for Bought ETFs"):
                st.session_state.etf_table.loc[edited_df['Bought'] == True, 'Traded Quantity'] = '0'
                # Persist to config.properties
                new_traded_qty = st.session_state.etf_table['Traded Quantity'].tolist()
                rc.set_traded_quantities(new_traded_qty)
                st.success("Traded Quantity set to 0 for all ETFs marked as bought and saved to config.properties. Please make further edits as needed.")
                # No second table is shown; the user continues editing in the same table
        else:
            st.warning("No ETF data to display.")

    elif choice == "Edit Decided Quantity":
        st.header("Edit Decided Quantity")
        new_qty = []
        for i, etf in enumerate(etf_list):
            val = st.text_input(f"{etf} quantity", value=qty_list[i] if qty_list and i < len(qty_list) else "")
            new_qty.append(val)
        if st.button("Save Quantities"):
            rc.set_decided_quantities(new_qty)
            st.success("Decided quantities updated!")
            st.session_state.nav_choice = "View ETF tracker"
            st.experimental_rerun()


if __name__ == "__main__":
    main()