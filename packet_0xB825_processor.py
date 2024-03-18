import re
from parser.json_comments import LTE_bands_0xB825
class Packet_0xB825:
    # def __int__(self):
    #     # print("New")

    def extract_info(lines, config, entry):
        # print("Lines", lines)
        # print("obj", dict)
        # return dict
        # pattern = r'.*?0xB801.*?--  (?P<msg_subtitle>.*?)\s*\nSubscription ID = (?P<subscription_id>\d+)\n.*?nr5g_smm_msg\s+(?P<nr5g_smm_msg>.*?)\n(?:.*?cause = (?P<_5gsm_cause>.*?)\n|.*?)'
        # pattern = r'.*?0xB825.*?Subscription ID = (?P<Subscription_ID>\d+).*?Conn Config Info.*?State = (?P<State>\w+).*?LTE Serving Cell Info.*?Num Bands = (?P<num_bands>\d+).*?LTE Bands = (?P<lte_bands>.+).*?Num Contiguous CC Groups = (?P<num_cont_cc_groups>\d+).*?Num Active CC = (?P<num_active_cc>\d+).*?NR5G Serving Cell Info\n.*?MIMO\|\n.*?\n(?P<table>.+)?Radio Bearer Info.*?'
        # pattern = r'.*?0xB825.*?Subscription ID = (?P<Subscription_ID>\d+).*?Conn Config Info.*?State = (?P<State>\w+).*?LTE Serving Cell Info.*?Num Bands = (?P<num_bands>\d+).*?LTE Bands = (?P<lte_bands>.+?).*?Num Contiguous CC Groups = (?P<num_cont_cc_groups>\d+))?(Num Active CC = (?P<num_active_cc>\d+).*?(?:NR5G Serving Cell Info\n.*?MIMO\|\n.*?\n(?P<table>.+?))?(?:Radio Bearer Info|$)'

        pattern = r'.*?0xB825.*?Subscription ID = (?P<subscription_id>\d+).*?Conn Config Info.*?State = (?P<State>\w+).*?Connectivity Mode = (?P<connectivity_mode>\w+).*?LTE Serving Cell Info {.*?Num Bands = (?P<num_bands>\d+).*?LTE Bands = {(?P<lte_bands>.+)}.*?}.*?Num Contiguous CC Groups = (?P<num_cont_cc_groups>\d+).*?Num Active CC = (?P<num_active_cc>\d+)(.*?)(NR5G Serving Cell Info\n.*?MIMO\|\n.*?\n(?P<table>.+?))?(Radio Bearer Info.*?|$)'

        match = re.match(pattern, lines, re.DOTALL)

        # print(config)

        if match:
            entry.update(match.groupdict())

            key_mapping = {'subscription_id': config['Subscription ID']['DB Field'],
                           'State': config['Conn Config Info.State']['DB Field'],
                           'num_bands': config['Conn Config Info.LTE Serving Cell Info.Num Bands']['DB Field'],
                           'lte_bands': config['Conn Config Info.LTE Serving Cell Info.LTE Bands']['DB Field'],
                           'num_cont_cc_groups': config['Conn Config Info.Num Contiguous CC Groups']['DB Field'],
                           'num_active_cc': config['Conn Config Info.Num Active CC']['DB Field'],
                           }

            lte_bands_str = entry["lte_bands"].strip()
            lte_bands = [int(band) for band in lte_bands_str.split(",") if int(band.strip()) != 0]
            # lte_bands = LTE_bands_0xB825([
            # "lte_bands_str = entry['lte_bands'].strip()",
            # "lte_bands = [int(band) for band in lte_bands_str.split(',') if int(band.strip()) != 0]"
            # ], entry)
            lte_bands_str = ''.join(str(x) for x in lte_bands)
            lte_bands_str.strip('[')

            entry["lte_bands"] = lte_bands_str

            entry = {key_mapping.get(key, key): value for key, value in entry.items()}
            # print(entry["table"])
            if entry["table"]:
                column_row_values = entry["table"].split("|")
                # print(column_row_values)
                # nr5g_serving_cell_info = {}

                for item in config['Conn Config Info.NR5G Serving Cell Info']:
                    # print(item)
                    # keys = list(item.keys())
                    # print(keys)
                    for key in list(item.keys()):
                        # print(key)
                        index = item[key]['index']
                        mapped_key = item[key]['DB Field']
                        if index < len(column_row_values):
                            value = column_row_values[index+1].strip()
                            # nr5g_serving_cell_info[mapped_key] = value
                            entry[mapped_key] = value
            # entry.pop("table", None)

                # entry['NR5G Serving Cell Info'] = nr5g_serving_cell_info
            entry["__collection"] = config.get('__collection')
            entry["__frequency"] = config.get('__frequency')

            if config["__cell"]:
                if entry['table'] and entry['CC Id']:
            #     print(entry)
            #     # ccid= entry['nr5g_serving_cell_info'][0]
                    if int(entry['CC Id']) == 0 or int(entry['CC Id']) == 8:
                        entry["__cell"] = 'PCC'
                    elif int(entry['CC Id']) >= 1:
                        entry["__cell"] = f'SCC{entry["CC ID"]}'
                # else:
                #     pass



            if "__packet_message" in config:
                entry["__packet_message"] = entry["connectivity_mode"]
                entry.pop("connectivity_mode", None)


            # entry["__cell"] = config.get('__cell')
            # if "__packet_message" in config:
            #     entry["__packet_message"] = entry["msg_subtitle"]
            #     entry.pop("msg_subtitle", None)
            entry["__Raw_Data"] = config.get("__Raw_Data")
            entry["__KPI_type"] = config.get('__KPI_type')
            # print("CC ID", entry['CC Id'])
            entry.pop("table",None)
            entry.pop("connectivity_mode", None)
            return entry
        else:
            return None