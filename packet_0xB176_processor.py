import re
from kpi_utils import simple_map_entry
class Packet_0xB176:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r'.*?Subscription ID = (?P<subs_id>[\d]+).*?E-ARFCN = (?P<e_arfcn>[\d]+).*?Band = (?P<band>[\d]+).*?Duplex Mode = (?P<duplex_mode>[a-zA-Z]+).*?Result = (?P<result>[a-zA-Z]+).*?Min Search Half Frames = (?P<Min_search_half_frams>[\d]+).*?Min Search Half Frames Early Abort = (?P<min_search_half_frames_early_abort>[\d]+).*?Max Search Half Frames = (?P<max_search_half_frames>[\d]+).*?Max PBCH Frames = (?P<max_pbch_frames>[\d]+).*?Number of Blocked Cells = (?P<number_of_blocked_cells>[\d]+).*?Number PBCH Decode Attemp Cells = (?P<number_pbch_decode_attemp_cells>[\d]+).*?Number of Search Results = (?P<number_of_search_results>[\d]+)'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None