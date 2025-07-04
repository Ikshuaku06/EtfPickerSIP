import streamlit as st
from streamlit.runtime.scriptrunner import RerunException
from streamlit.runtime.scriptrunner import get_script_run_ctx
from datetime import datetime
import pytz
import os
import json

# from Config import read_config as rc
from Config import read_config as rc
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd

def load_traded_state(state_file, etf_list, traded_qty_list, today_str):
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            state = json.load(f)
        # Check if date matches today and ETF list matches
        if state.get('date') == today_str and state.get('etf_list') == etf_list:
            return state['traded_qty_original'], state['traded_qty_incremented']
    # If not found or date mismatch, reset
    return [int(q) for q in traded_qty_list], [False] * len(etf_list)

def save_traded_state(state_file, etf_list, traded_qty_original, traded_qty_incremented, today_str):
    state = {
        'date': today_str,
        'etf_list': etf_list,
        'traded_qty_original': traded_qty_original,
        'traded_qty_incremented': traded_qty_incremented
    }
    with open(state_file, 'w') as f:
        json.dump(state, f)

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

    from utilities import utils

    # Prepare ETF data for both Index and Sector
    etf_sections = [
        {"name": "Index ETF", "section": "Index_ETF"},
        {"name": "Sector ETF", "section": "Sector_ETF"}
    ]

    if choice == "View ETF tracker":
        today_str = now_ist.strftime('%Y-%m-%d')
        for etf_info in etf_sections:
            section = etf_info["section"]
            etf_list = rc.get_etf_list(section)
            qty_list = rc.get_decided_quantities(section)
            traded_qty_list = rc.get_traded_quantities(section)
            state_file = os.path.join(os.path.dirname(__file__), f'traded_state_{section}.json')
            # Load original traded quantity and incremented state from file
            if f'traded_qty_original_{section}' not in st.session_state or st.session_state.get(f'traded_qty_day_date_{section}') != today_str:
                traded_qty_original, traded_qty_incremented = load_traded_state(state_file, etf_list, traded_qty_list, today_str)
                st.session_state[f'traded_qty_original_{section}'] = traded_qty_original
                st.session_state[f'traded_qty_day_date_{section}'] = today_str
                st.session_state[f'traded_qty_incremented_{section}'] = traded_qty_incremented

            traded_qty = st.session_state[f'traded_qty_original_{section}'].copy()
            incremented = st.session_state[f'traded_qty_incremented_{section}'].copy()

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
                    traded_qty[i] = st.session_state[f'traded_qty_original_{section}'][i]
                    incremented[i] = False
            st.session_state[f'traded_qty_incremented_{section}'] = incremented

            # If user sets Traded Quantity to 0 via Bought checkbox, treat as manual override for the day
            table_key = f'etf_table_{section}'
            if table_key in st.session_state:
                for i, etf in enumerate(etf_list):
                    try:
                        manual_traded = int(st.session_state[table_key].loc[i, 'Traded Quantity'])
                    except:
                        continue
                    if manual_traded == 0:
                        incremented[i] = True
            st.session_state[f'traded_qty_incremented_{section}'] = incremented

            # Persist state to file after any logic
            save_traded_state(state_file, etf_list, traded_qty, incremented, today_str)

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
            for col in ["ETF", "Decided Quantity", "Traded Quantity", "Bought"]:
                df[col] = df[col].astype(str)
            if "index" in df.columns:
                df = df.drop(columns=["index"])
            df = df.fillna("").reset_index(drop=True)

            st.subheader(etf_info["name"])
            if not df.empty:
                df['Bought'] = False
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
                if table_key not in st.session_state:
                    st.session_state[table_key] = df[["ETF", "Curr Price", "Previous Close", "Decided Quantity", "Traded Quantity", "Bought"]].copy()
                edited_df = st.data_editor(
                    st.session_state[table_key],
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
                    key=f"etf_data_editor_{section}"
                )
                if st.button(f"Set Traded Quantity to 0 for Bought ETFs in {etf_info['name']}"):
                    st.session_state[table_key].loc[edited_df['Bought'] == True, 'Traded Quantity'] = '0'
                    new_traded_qty = st.session_state[table_key]['Traded Quantity'].tolist()
                    rc.set_traded_quantities(new_traded_qty, section)
                    st.success(f"Traded Quantity set to 0 for all ETFs marked as bought in {etf_info['name']} and saved to config.properties. Please make further edits as needed.")
            else:
                st.warning(f"No {etf_info['name']} data to display.")

    elif choice == "Edit Decided Quantity":
        st.header("Edit Decided Quantity")
        tab1, tab2 = st.tabs(["Index ETF", "Sector ETF"])
        for tab, etf_info in zip([tab1, tab2], etf_sections):
            section = etf_info["section"]
            etf_list = rc.get_etf_list(section)
            qty_list = rc.get_decided_quantities(section)
            with tab:
                new_qty = []
                for i, etf in enumerate(etf_list):
                    val = st.text_input(f"{etf} quantity", value=qty_list[i] if qty_list and i < len(qty_list) else "", key=f"qty_{section}_{i}")
                    new_qty.append(val)
                if st.button(f"Save Quantities for {etf_info['name']}", key=f"save_qty_{section}"):
                    rc.set_decided_quantities(new_qty, section)
                    st.success(f"Decided quantities updated for {etf_info['name']}!")
                    raise RerunException(get_script_run_ctx())


if __name__ == "__main__":
    main()