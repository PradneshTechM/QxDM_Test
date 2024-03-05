import re
class Packet_0xB0E4:
    # def __int__(self):
    #     print("New")
    def extract_info(lines, config, entry):
        # print("Lines", lines)
        # print("obj", dict)
        # return dict
        # pattern = r'''(?P<timestamp>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\w+\]\s+0xB167.*?Subscription ID = (?P<subscription_id>\d+).*?Version = (?P<version>\d+).*?Cell Index = (?P<cell_index>\d+).*?PRACH Config Index = (?P<prach_config_index>\d+).*?Preamble Sequence = (?P<preamble_sequence>\d+).*?Physical Root Index = (?P<physical_root_index>\d+).*?Cyclic Shift = (?P<cyclic_shift>\d+).*?PRACH Tx Power = (?P<prach_tx_power>[\d\s]+).*?Beta PRACH = (?P<beta_prach>\d+).*?PRACH Frequency Offset = (?P<prach_frequency_offset>\d+).*?Preamble Format = (?P<preamble_format>\d+).*?Duplex Mode = (?P<duplex_mode>\w+).*?RA RNTI = (?P<ra_rnti>\d+).*?PRACH Actual Tx Power = (?P<prach_actual_tx_power>[\d\s]+)\n'''
        pattern = r'.*?0xB0E4.*?Subscription ID = (?P<subscription_id>\d+).*?Bearer ID = (?P<bearer_id>\d+).*?Bearer State = (?P<bearer_state>\w+).*?Connection ID = (?P<connection_id>\d+)'

        match = re.match(pattern, lines, re.DOTALL)

        if match:
            # _obj["State"] = 1
            # print(lines)
            # _obj.update(match.groupdict())
            entry.update(match.groupdict())

            # entry = match.groupdict()
            # print(entry)

            key_mapping = {'subscription_id': config['Subscription ID']['DB Field'],
                           'bearer_id': config['Bearer ID']['DB Field'],
                           'bearer_state': config['Bearer State']['DB Field'],
                           'connection_id': config['Connection ID']['DB Field'],
                           }


            # mapped_entry = {key_mapping[key]: value for key, value in entry.items() if key in key_mapping}
            mapped_entry = {key_mapping.get(key,key): value for key, value in entry.items()}
            mapped_entry['Source'] = 'QxDM'

            mapped_entry["__collection"] = config.get('__collection')
            mapped_entry["__cell"] = config.get('__cell')
            if "Packet_Type" in config:
                mapped_entry["Packet_Type"] = config.get('Packet_Type')
            mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
            mapped_entry["__KPI_type"] = config.get('__KPI_type')

            # print(entry)
            # print(dict)
            # return True
            return mapped_entry
        else:

            return None