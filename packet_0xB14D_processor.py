import regex as re
from kpi_utils import simple_map_entry
class Packet_0xB14D:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r'Subscription ID = (?P<subs_id>\d+).*?Scell Index = (?P<scell_index>[\d]+).*?PUCCH Reporting Mode = (?P<pucch_reporting_mode>[\w]+).*?PUCCH Report Type = (?P<pucch_report_type>[a-zA-Z\d\s\,]+)\n.*?Rank Index = (?P<rank_index>[\w\s]+)\n.*?CRI = (?P<cri>[\d]+)'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None