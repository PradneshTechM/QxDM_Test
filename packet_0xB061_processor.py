import re
from kpi_utils import simple_map_entry
class Packet_0xB061:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r".*?Subscription ID = (?P<Subs_ID>[\d]+).*?Number of SubPackets = (?P<no_sub_packets>[\d]+).*?SubPacket ID = (?P<subpacket_id>[\d]+).*?SubPacket - (?P<subpacket>.*?(?=\n)).*?Sub Id = (?P<sub_id>[\d]+).*?Num Active Cell = (?P<num_active_cell>[\d]+).*?CC Id = (?P<cc_id>[\d]+).*?Preamble initial power = (?P<preamble_initial_power>[-\d\s\w]+)\n.*?Power ramping step = (?P<power_ramping_step>[\d\s\w]+)\n.*?RA index1 = (?P<ra_index_1>[\d]+).*?RA index2 = (?P<ra_index_2>[\d]+).*?Preamble trans max = (?P<preamble_trans_max>[\d]+).*?Contention resolution timer = (?P<contention_resolution_timer>.*?(?=\n)).*?Message size Group_A = (?P<msg_group_a>[\d]+).*?Power offset Group_B = (?P<power_groupb>.*?(?=\n)).*?Delta preamble Msg3 = (?P<delta_preamble_msg3>[\d]+).*?PRACH config = (?P<prach_config>[\d]+).*?CS zone length = (?P<cs_zone_length>[\d]+).*?Root seq index = (?P<root_seq_index>[\d]+).*?PRACH Freq Offset = (?P<prach_freq_offset>[\d]+).*?High speed flag = (?P<high_speed_flag>[\d]+).*?Max retx Msg3 = (?P<max_retx_msg3>[\d]+).*?RA rsp win size = (?P<ra_resp_win_size>.*?(?=\n)).*?Rach reason = (?P<rach_reason>.*?(?=\n)).*?RACH Contention = (?P<rach_contention>[\w]+).*?Msg3 size = (?P<msg3_size>.*?(?=\n)).*?Radio condn = (?P<radio_condn>.*?(?=\n)).*?CRNTI = (?P<crnti>.*?(?=\n)).*?"

        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            data['SubPacket'] = data['SubPacket'].strip('()')
            data['SubPacket'] = data['SubPacket'].strip(' ')
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None