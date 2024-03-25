import regex as re
from kpi_utils import simple_map_entry
class Packet_0xB167:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r'.*?0xB167.*?Subscription ID = (?P<subscription_id>\d+).*?Cell Index = (?P<cell_index>\d+).*?PRACH Config Index = (?P<prach_config_index>\d+).*?Preamble Sequence = (?P<preamble_sequence>\d+).*?Physical Root Index = (?P<physical_root_index>\d+).*?Cyclic Shift = (?P<cyclic_shift>\d+).*?PRACH Tx Power = (?P<prach_tx_power>[\d\s]+).*?PRACH Frequency Offset = (?P<prach_frequency_offset>\d+).*?Preamble Format = (?P<preamble_format>\d+).*?Duplex Mode = (?P<duplex_mode>\w+).*?PRACH Window Start SFN = (?P<prach_window_start_sfn>\d+).*?RACH Window Start Sub-fn = (?P<rach_window_start_sub_fn>\d+).*?PRACH Window End SFN = (?P<prach_window_end_sfn>\d+).*?PRACH Window End Sub-fn = (?P<prach_window_end_sub_fn>\d+).*?RA RNTI = (?P<ra_rnti>\d+).*?PRACH Actual Tx Power = (?P<prach_actual_tx_power>[\d\s]+)\n'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None