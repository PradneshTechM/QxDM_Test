import regex as re
from kpi_utils import simple_map_entry
class Packet_0xB0C1:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r".*?Subscription ID = (?P<subscription_id>\d+).*?Physical cell ID = (?P<PCI>\d+).*?FREQ = (?P<Frequency>\d+).*?Number of TX Antennas = (?P<no_tx_antennas>\d+).*?DL Bandwidth = (?P<dl_bandwidth>.*)"
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None


