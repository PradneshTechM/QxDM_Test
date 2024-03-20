import regex as re
from parser.kpi_utils import simple_map_entry
class Packet_0x1568:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r".*?Subscription ID = (?P<Subs_ID>[\d]+).*?Direction = (?P<direction>[\w_]+).*?Rat Type = (?P<rat_type>[\w]+).*?Ssrc = (?P<Ssrc>[\d]+).*?Rtp Time stamp = (?P<rtp_time_stamp>[\d]+).*?CodecType = (?P<CodecType>[\w-]+).*?mediaType = (?P<mediaType>[\w]+).*?PayLoad Size = (?P<payload_size>[\d]+).*?Logged Payload Size = (?P<logged_payload_size>[\d]+).*?"

        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None