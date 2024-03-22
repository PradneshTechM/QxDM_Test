import regex as re
from parser.kpi_utils import simple_map_entry
class Packet_0xB0C0:
    def extract_info(packet_text,config=None, entry=None):
        patterns = [r".*?0xB0C0.*? --  (?P<msg_subtitle>.*)\n.*?Subscription ID = (?P<subscription_id>\d+).*?Physical Cell ID = (?P<PCI>\d+).*?Freq = (?P<Frequency>\d+).*?PDU Number = (?P<pdu_number>.*?(?=,)).*?{\n\s+(?P<message_c1>.*?).\n*?freqBandIndicator",
                    r".*?0xB0C0.*? --  (?P<msg_subtitle>.*)\n.*?Subscription ID = (?P<subscription_id>\d+).*?Physical Cell ID = (?P<PCI>\d+).*?Freq = (?P<Frequency>\d+).*?PDU Number = (?P<pdu_number>.*?(?=,)).*?establishmentCause (?P<establishmentCause>.*?(?=,)).*?"]
        for pattern in patterns:
            match = re.match(pattern, packet_text, re.DOTALL)
            if match:
                entry1 = match.groupdict()
                data = simple_map_entry(entry1, config)
                entry.update(data)
                return entry
            else:
                # Return None or an empty dictionary if there is no match
                return None


