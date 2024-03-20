import regex as re
from parser.kpi_utils import simple_map_entry

class Packet_0xB0E3:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r".*? --  (?P<msg_subtitle>.*)\n.*?Subscription ID = (?P<Subs_ID>[\d]+).*?eps_bearer_id_or_skip_id = (?P<eps_id>.*?(?=\n)).*?prot_disc = (?P<prot_disc>.*?(?=\n)).*?msg_type = (?P<msg_type>.*?(?=\n)).*?\n(?P<raw_packet>.*).\n*?prot_config\n.*?"
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None