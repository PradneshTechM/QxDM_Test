import regex as re
from parser.kpi_utils import simple_map_entry
class Packet_0xB821:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r'.*?0xB821.*?--  (?P<msg_subtitle>[\w\s\/]+)\n.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Physical Cell ID = (?P<PCI>[\d]+).*?Freq = (?P<Frequency>[\d]+).*?PDU Number = (?P<PDU_Type>[a-zA-Z\s_]+)(?:.*?message c1 : (?P<Message>[a-zA-Z]+))?(?:.*?establishmentCause (?P<establishmentCause>[a-zA-Z\-]+))?.*?'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None