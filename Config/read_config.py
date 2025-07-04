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
    
def get_etf_list(section='Index_ETF'):
    try:
        etf_list = get_value(section, 'etf')
        return etf_list.split(',')
    except ValueError as e:
        print(f"Error: {e}")
        return None
    
def get_decided_quantities(section='Index_ETF'):
    try:
        qty_list = get_value(section, 'decidedquantity')
        return qty_list.split(',')
    except ValueError as e:
        print(f"Error: {e}")
        return None
    
def set_decided_quantities(qty_list, section='Index_ETF'):
    Config = read_config()
    if not Config.has_section(section):
        Config.add_section(section)
    Config.set(section, 'decidedquantity', ','.join(str(q) for q in qty_list))
    with open('Config/config.properties', 'w') as configfile:
        Config.write(configfile)

def get_traded_quantities(section='Index_ETF'):
    try:
        qty_list = get_value(section, 'tradedquantity')
        return qty_list.split(',')
    except ValueError as e:
        print(f"Error: {e}")
        return None

def set_traded_quantities(qty_list, section='Index_ETF'):
    Config = read_config()
    if not Config.has_section(section):
        Config.add_section(section)
    Config.set(section, 'tradedquantity', ','.join(str(q) for q in qty_list))
    with open('Config/config.properties', 'w') as configfile:
        Config.write(configfile)
    
if __name__ == "__main__":
    index_etf_list = get_etf_list('Index_ETF')
    sector_etf_list = get_etf_list('Sector_ETF')
    print("Index ETF List:", index_etf_list)
    print("Sector ETF List:", sector_etf_list)