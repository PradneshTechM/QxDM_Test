import regex as re
class Packet_0xB80A:
    # def __int__(self):
    #     print("New")

    def extract_info(lines, config, entry):
        # print("Lines", lines)
        # print("obj", dict)
        # return dict
        # pattern = r'''(?P<timestamp>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\w+\]\s+0xB167.*?Subscription ID = (?P<subscription_id>\d+).*?Version = (?P<version>\d+).*?Cell Index = (?P<cell_index>\d+).*?PRACH Config Index = (?P<prach_config_index>\d+).*?Preamble Sequence = (?P<preamble_sequence>\d+).*?Physical Root Index = (?P<physical_root_index>\d+).*?Cyclic Shift = (?P<cyclic_shift>\d+).*?PRACH Tx Power = (?P<prach_tx_power>[\d\s]+).*?Beta PRACH = (?P<beta_prach>\d+).*?PRACH Frequency Offset = (?P<prach_frequency_offset>\d+).*?Preamble Format = (?P<preamble_format>\d+).*?Duplex Mode = (?P<duplex_mode>\w+).*?RA RNTI = (?P<ra_rnti>\d+).*?PRACH Actual Tx Power = (?P<prach_actual_tx_power>[\d\s]+)\n'''
        # pattern = r'.*?0xB0C2.*?Subscription ID = (?P<subscription_id>\d+).*?Physical cell ID = (?P<physical_cell_id>\d+).*?DL FREQ = (?P<dl_freq>\d+).*?UL FREQ = (?P<ul_freq>\d+).*?DL Bandwidth = (?P<dl_bandwidth>[\d\s]+).*?UL Bandwidth = (?P<ul_bandwidth>[\d\s]+).*?Cell Identity = (?P<cell_identity>\d+).*?Tracking area code = (?P<tracking_area_code>\d+).*?MCC = (?P<mcc>\d+).*?MNC = (?P<mnc>\d+)'
        pattern = r'.*?0xB80A.*?--  (?P<msg_subtitle>.*?)\s+(?=Subscription ID).*?Subscription ID = (?P<Subs_ID>\d+).*?nr5g_mm_msg\s+(?P<nr5g_mm_msg>.+?)\n'
        match = re.match(pattern, lines, re.DOTALL)

        # print(config)
        if match:
            # _obj["State"] = 1
            # print(lines)
            # _obj.update(match.groupdict())
            entry.update(match.groupdict())
            # entry = match.groupdict()
            # print(entry)

            key_mapping = {'Subs_ID': config['Subscription ID']['DB Field'],
                           'nr5g_mm_msg': config['nr5g_mm_msg']['DB Field']
                           }

            # mapped_entry = {key_mapping[key]: value for key, value in entry.items() if key in key_mapping}
            mapped_entry = {key_mapping.get(key,key): value for key, value in entry.items()}
            if '__collection' in config:
                mapped_entry["__collection"] = config.get('__collection')
            if '__cell' in config:
                mapped_entry["__cell"] = config.get('__cell')
            if "Packet_Type" in config:
                mapped_entry["Packet_Type"] = entry["msg_subtitle"]
                mapped_entry.pop("msg_subtitle", None)
            # mapped_entry["__Raw_Data"] = config.get("__Raw_Data")
            if '__KPI_type' in config:
                mapped_entry["__KPI_type"] = config.get('__KPI_type')

            # print(entry)
            # print(dict)
            # return True
            return mapped_entry
        else:

            return None