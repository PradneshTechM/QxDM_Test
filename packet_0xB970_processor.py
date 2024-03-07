import re
from parser.kpi_utils import simple_map_entry
class Packet_0xB970:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r'.*?Subscription ID = (?P<subs_id>[\d]+).*?Slot Number = (?P<slot_number>[\d]+).*?SubFrame Number = (?P<subframe_number>[\d]+).*?System Frame Number = (?P<system_frame_number>[\d]+).*?SCS = (?P<svs>[\da-zA-Z]+).*?NR ARFCN = (?P<nr_arfcn>[\d]+).*?Phy Cell ID = (?P<phy_cell_id>[\d]+).*?Serving SSB Index = (?P<serving_ssb_index>[\d]+).*?Q Rx Level Min = (?P<q_rx_level_min>[\-a-zA-Z\s\d]+)\n.*?Q RX Level Min Offset = (?P<q_rx_level_min_offset>[a-zA-Z]+).*?P Max = (?P<p_max>[\d\sa-zA-Z]+)\n.*?Max UE TX Power = (?P<max_ue_tx_power>[\d\sa-zA-Z]+)\n.*?Cell Quality RSRP = (?P<cell_quality_rsrp>[\d\-\.\sa-zA-Z]+)\n.*?Q Qual Min = (?P<q_qual_min>[\d\-\.\sa-zA-Z]+)\n.*?Q Qualmin Offset = (?P<q_qualmin_offset>[\d\-\.\sa-zA-Z]+)\n.*?S Qual =(?P<s_qual>[\d\-\.\sa-zA-Z]+)\n.*?Cell Quality RSRQ = (?P<cell_quality_rsrq>[\d\-\.\sa-zA-Z]+)\n.*?Result = (?P<result>[a-zA-Z]+)'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None