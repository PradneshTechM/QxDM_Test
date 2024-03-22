import regex as re
from parser.kpi_utils import simple_map_entry
class Packet_0xB822:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Physical Cell ID = (?P<Physicall_Cell_ID>[\d]+).*?DL Frequency = (?P<DL_Frequency>[\d]+).*?Intra Freq Reselection = (?P<Intra_Freq_Reselection>[a-zA-Z]+).*?Cell Barred = (?P<Cell_Barred>[a-zA-Z_]+).*?PDCCH Config SIB1 = (?P<PDCCH_Config_SIB1>[\d]+).*?DMRS TypeA Position = (?P<DMRS_TypeA_Position>[a-zA-Z\d]+).*?SSB Subcarrier Offset = (?P<SSB_Subcarrier_Offset>[\d]+).*?Subcarrier Spacing Common = (?P<Subcarrier_Spacing_Common>[a-zA-Z\d]+)'
        # Use re.search to find the first match of the pattern in the packet_text
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None