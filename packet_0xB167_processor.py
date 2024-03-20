import regex as re
class Packet_0xB167:
    # def __int__(self):
    #     print("New")
    def extract_info(lines, config, entry=None):
        # print("Lines", lines)
        # print("obj", dict)
        # return dict
        # pattern = r'''(?P<timestamp>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\w+\]\s+0xB167.*?Subscription ID = (?P<subscription_id>\d+).*?Version = (?P<version>\d+).*?Cell Index = (?P<cell_index>\d+).*?PRACH Config Index = (?P<prach_config_index>\d+).*?Preamble Sequence = (?P<preamble_sequence>\d+).*?Physical Root Index = (?P<physical_root_index>\d+).*?Cyclic Shift = (?P<cyclic_shift>\d+).*?PRACH Tx Power = (?P<prach_tx_power>[\d\s]+).*?Beta PRACH = (?P<beta_prach>\d+).*?PRACH Frequency Offset = (?P<prach_frequency_offset>\d+).*?Preamble Format = (?P<preamble_format>\d+).*?Duplex Mode = (?P<duplex_mode>\w+).*?RA RNTI = (?P<ra_rnti>\d+).*?PRACH Actual Tx Power = (?P<prach_actual_tx_power>[\d\s]+)\n'''
        pattern = r'.*?0xB167.*?Subscription ID = (?P<subscription_id>\d+).*?Cell Index = (?P<cell_index>\d+).*?PRACH Config Index = (?P<prach_config_index>\d+).*?Preamble Sequence = (?P<preamble_sequence>\d+).*?Physical Root Index = (?P<physical_root_index>\d+).*?Cyclic Shift = (?P<cyclic_shift>\d+).*?PRACH Tx Power = (?P<prach_tx_power>[\d\s]+).*?PRACH Frequency Offset = (?P<prach_frequency_offset>\d+).*?Preamble Format = (?P<preamble_format>\d+).*?Duplex Mode = (?P<duplex_mode>\w+).*?PRACH Window Start SFN = (?P<prach_window_start_sfn>\d+).*?RACH Window Start Sub-fn = (?P<rach_window_start_sub_fn>\d+).*?PRACH Window End SFN = (?P<prach_window_end_sfn>\d+).*?PRACH Window End Sub-fn = (?P<prach_window_end_sub_fn>\d+).*?RA RNTI = (?P<ra_rnti>\d+).*?PRACH Actual Tx Power = (?P<prach_actual_tx_power>[\d\s]+)\n'

        match = re.match(pattern, lines, re.DOTALL)


        if match:
            # _obj["State"] = 1
            # print(lines)
            # _obj.update(match.groupdict())
            entry.update(match.groupdict())

            # entry = match.groupdict()
            # key_mapping = {'subscription_id': 'Subscription ID', 'cell_index': 'Cell Index',
            #                'prach_config_index': 'PRACH Config Index', 'preamble_sequence': 'Preamble Sequence',
            #                'physical_root_index': 'Physical Root Index', 'cyclic_shift': 'Cyclic Shift',
            #                'prach_tx_power': 'PRACH Tx Power', 'prach_frequency_offset': 'PRACH Frequency Offset',
            #                'preamble_format': 'Preamble Format', 'duplex_mode': 'Duplex Mode', 'prach_window_start_sfn': 'PRACH Window Start SFN',
            #                'rach_window_start_sub_fn': 'PRACH Window Start Sub-fn',
            #                'prach_window_end_sfn': 'PRACH Window End SFN',
            #                'prach_window_end_sub_fn': 'PRACH Window End Sub-fn', 'ra_rnti': 'RA RNTI',
            #                'prach_actual_tx_power': 'PRACH Actual Tx Power'}

            key_mapping = {'subscription_id': config['Subscription ID']['DB Field'],
                           'cell_index': config['Cell Index']['DB Field'],
                           'prach_config_index': config['PRACH Config Index']['DB Field'],
                           'preamble_sequence': config['Preamble Sequence']['DB Field'],
                           'physical_root_index': config['Physical Root Index']['DB Field'],
                           'cyclic_shift': config['Cyclic Shift']['DB Field'],
                           'prach_tx_power': config['PRACH Tx Power']['DB Field'],
                           'prach_frequency_offset': config['PRACH Frequency Offset']['DB Field'],
                           'preamble_format': config['Preamble Format']['DB Field'],
                           'duplex_mode': config['Duplex Mode']['DB Field'],
                           'prach_window_start_sfn': config['PRACH Window Start SFN']['DB Field'],
                           'rach_window_start_sub_fn': config['RACH Window Start Sub-fn']['DB Field'],
                           'prach_window_end_sfn': config['PRACH Window End SFN']['DB Field'],
                           'prach_window_end_sub_fn': config['PRACH Window End Sub-fn']['DB Field'],
                           'ra_rnti': config['RA RNTI']['DB Field'],
                           'prach_actual_tx_power': config['PRACH Actual Tx Power']['DB Field']
                           }

            # mapped_entry = {key_mapping[key]: value for key, value in entry.items() if key in key_mapping}
            mapped_entry = {key_mapping.get(key,key): value for key, value in entry.items()}
            mapped_entry["__cell"] = config.get('__cell')


            # print(entry)
            # print(dict)
            # return True
            return mapped_entry
        else:

            return None