import re
from kpi_utils import simple_map_entry
class Packet_0x17F2:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r".*?Subscription ID = (?P<Subs_ID>[\d]+).*?SipCallDur = (?P<SipCallDur>[\d]+).*?CodecType = (?P<CodecType>.*?(?=\n)).*?RAT Type = (?P<RAT_Type>[\w]+)"
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None