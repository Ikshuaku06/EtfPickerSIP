from configparser import ConfigParser

def read_config():
    Config=ConfigParser()
    Config.read('Config/config.properties')
    return Config

def get_value(section, key):
    Config = read_config()
    if Config.has_section(section) and Config.has_option(section, key):
        return Config.get(section, key)
    else:
        raise ValueError(f"Section '{section}' or key '{key}' not found in the configuration file.")
    
def get_etf_list():
    try:
        etf_list = get_value('ETF', 'ETF')
        return etf_list.split(',')
    except ValueError as e:
        print(f"Error: {e}")
        return None
    
def get_decided_quantities():
    try:
        qty_list = get_value('ETF', 'DecidedQuantity')
        return qty_list.split(',')
    except ValueError as e:
        print(f"Error: {e}")
        return None
    
def set_decided_quantities(qty_list):
    Config = read_config()
    if not Config.has_section('ETF'):
        Config.add_section('ETF')
    Config.set('ETF', 'DecidedQuantity', ','.join(str(q) for q in qty_list))
    with open('Config/config.properties', 'w') as configfile:
        Config.write(configfile)

def get_traded_quantities():
    try:
        qty_list = get_value('ETF', 'TradedQuantity')
        return qty_list.split(',')
    except ValueError as e:
        print(f"Error: {e}")
        return None

def set_traded_quantities(qty_list):
    Config = read_config()
    if not Config.has_section('ETF'):
        Config.add_section('ETF')
    Config.set('ETF', 'TradedQuantity', ','.join(str(q) for q in qty_list))
    with open('Config/config.properties', 'w') as configfile:
        Config.write(configfile)
    
if __name__ == "__main__":
    etf_list = get_etf_list()
    if etf_list:
        print("ETF List:", etf_list)
    else:
        print("No ETF data available.")