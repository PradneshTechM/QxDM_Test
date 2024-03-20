import regex as re
from kpi_utils import simple_map_entry
class Packet_0xB179:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r'.*?Subscription ID = (?P<subs_id>[\d]+).*?Serving Cell Index = (?P<serving_cell_index>[a-zA-Z]+).*?FW Serving Cell Index = (?P<fw_serving_cell_index>[a-zA-Z]+).*?E-ARFCN = (?P<e_arfcn>[\d]+).*?Serving Physical Cell ID = (?P<serving_physical_cell_id>\d+).*?Sub-frame Number = (?P<sub_frame_number>[\d]+).*?Serving Filtered RSRP = (?P<serving_filtered_rsrp>[\-\.\d\sa-zA-Z]+)\n.*?Serving Filtered RSRQ = (?P<serving_filtered_rsrq>[\-\.\d\sa-zA-Z]+)\n.*?Number of Neighbor Cells = (?P<number_of_neighbor_cells>[\d]+).*?Number of Detected Cells = (?P<number_of_detected_cells>[\d]+)'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None