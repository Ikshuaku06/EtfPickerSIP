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
    
if __name__ == "__main__":
    etf_list = get_etf_list()
    if etf_list:
        print("ETF List:", etf_list)
    else:
        print("No ETF data available.")