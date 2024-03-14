import re
from kpi_utils import simple_map_entry
class Packet_0xB062:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r".*?Subscription ID = (?P<Subs_ID>[\d]+).*?Number of SubPackets = (?P<no_sub_packets>[\d]+).*?SubPacket ID = (?P<subpacket_id>[\d]+).*?SubPacket - (?P<subpacket>.*?(?=\n)).*?Sub Id = (?P<sub_id>[\d]+).*?CC Id = (?P<cc_id>[\d]+).*?Retx counter = (?P<retx_counter>[\d]+).*?Rach result = (?P<rach_result>[\w]+).*?Contention procedure = (?P<contention_procedure>[\w\s]+)\n.*?Preamble Index = (?P<p_index>[\d]+).*?Preamble index mask = (?P<p_index_mask>[\w]+).*?Preamble power offset = (?P<power_offset>[-\d\s\w]+)\n.*?Pcmaxc = (?P<Pcmaxc>[\d]+).*?Group Chosen = (?P<group_chosen>[\w\s]+)\n.*?Backoff Value = (?P<backoff_value>[\d\s\w]+)\n.*?Result = (?P<Result>[\w]+).*?TCRNTI = (?P<TCRNTI>[\d]+).*?TA value = (?P<TA_value>[\d]+).*?Earfcn = (?P<Earfcn>[\d]+).*?P Max = (?P<p_max>[\d]+).*?SCell ID = (?P<scell_id>[\d]+).*?Max Serv RSRP Present = (?P<max_serv_rsrp>[\w]+).*?"

        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None