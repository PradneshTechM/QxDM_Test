import regex as re
from kpi_utils import simple_map_entry
class Packet_0xB186:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r'.*?Subscription ID = (?P<subs_id>[\d]+).*?Serving E-ARFCN = (?P<serving_e_arfcn>[\d]+).*?Serving Cell ID = (?P<serving_cell_id>[\d]+).*?Num Reselection Candidates = (?P<num_reselection_candidates>[\d]+).*?Candidates\[\d\].*?Candidate Priority = (?P<candidate_priority>[\d\.]+).*?RAT Type = (?P<rat_type>[a-zA-Z]+).*?LTE Candidate.*?E-ARFCN = (?P<e_arfcn>[\d]+).*?Cell ID = (?P<cell_id>[\d]+).*?Candidate Priority = (?P<candidate_priority_1>[\d\.]+).*?RAT Type = (?P<rat_type_1>[a-zA-Z]+).*?LTE Candidate.*?E-ARFCN = (?P<e_arfcn_1>[\d]+).*?Cell ID = (?P<cell_id_1>[\d]+)'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None