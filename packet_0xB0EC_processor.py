import regex as re
from parser.kpi_utils import simple_map_entry
class Packet_0xB0EC:
    # def __int__(self):
    #     print("New")
    def extract_info(lines, config, entry):
        # print("Lines", lines)
        # print("obj", dict)
        # return dict
        # pattern = r'''(?P<timestamp>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\w+\]\s+0xB167.*?Subscription ID = (?P<subscription_id>\d+).*?Version = (?P<version>\d+).*?Cell Index = (?P<cell_index>\d+).*?PRACH Config Index = (?P<prach_config_index>\d+).*?Preamble Sequence = (?P<preamble_sequence>\d+).*?Physical Root Index = (?P<physical_root_index>\d+).*?Cyclic Shift = (?P<cyclic_shift>\d+).*?PRACH Tx Power = (?P<prach_tx_power>[\d\s]+).*?Beta PRACH = (?P<beta_prach>\d+).*?PRACH Frequency Offset = (?P<prach_frequency_offset>\d+).*?Preamble Format = (?P<preamble_format>\d+).*?Duplex Mode = (?P<duplex_mode>\w+).*?RA RNTI = (?P<ra_rnti>\d+).*?PRACH Actual Tx Power = (?P<prach_actual_tx_power>[\d\s]+)\n'''
        # pattern = r'.*?0xB0C2.*?Subscription ID = (?P<subscription_id>\d+).*?Physical cell ID = (?P<physical_cell_id>\d+).*?DL FREQ = (?P<dl_freq>\d+).*?UL FREQ = (?P<ul_freq>\d+).*?DL Bandwidth = (?P<dl_bandwidth>[\d\s]+).*?UL Bandwidth = (?P<ul_bandwidth>[\d\s]+).*?Cell Identity = (?P<cell_identity>\d+).*?Tracking area code = (?P<tracking_area_code>\d+).*?MCC = (?P<mcc>\d+).*?MNC = (?P<mnc>\d+)'
        pattern = r'.*?Subscription ID = (?P<Subs_ID>\d+).*?prot_disc = (?P<prot_disc>[\d\sa-zA-Z\(\)]+)\n.*?msg_type = (?P<msg_type>[\d\sa-zA-Z\(\)]+)\n.*?lte_emm_msg\s+(?P<lte_emm_msg>.+?)\n'
        match = re.match(pattern, lines, re.DOTALL)

        # print(config)
        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None