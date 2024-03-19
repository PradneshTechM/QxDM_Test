import re
from parser.kpi_utils import simple_map_entry
class Packet_0xB193:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r".*?Subscription ID = (?P<subs_id>[\d]+).*?E-ARFCN = (?P<e_arfcn>[\d]+).*?Cells\[0\].*?Physical Cell ID = (?P<physicall_cell_id>[\d]+).*?Serving Cell Index = (?P<serving_cell_index>[a-zA-Z]+).*?Inst RSRP Rx\[0\] = (?P<inst_rspr_rx0>[\d\-\sa-zA-Z\.]+)\n.*?Inst RSRQ Rx\[0\] = (?P<inst_rsrq_rx>[\d\-\sa-zA-Z\.]+)\n.*?Inst RSSI Rx\[0\] = (?P<inst_rssi_rx>[\d\-\sa-zA-Z\.]+)\n.*?FTL SNR Rx\[0\] = (?P<ftl_snr_rx>[\d\-\sa-zA-Z\.]+)\n"
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None