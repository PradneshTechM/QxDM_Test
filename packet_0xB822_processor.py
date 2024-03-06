import re


class Packet_0xB822:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Physical Cell ID = (?P<Physicall_Cell_ID>[\d]+).*?DL Frequency = (?P<DL_Frequency>[\d]+).*?Intra Freq Reselection = (?P<Intra_Freq_Reselection>[a-zA-Z]+).*?Cell Barred = (?P<Cell_Barred>[a-zA-Z_]+).*?PDCCH Config SIB1 = (?P<PDCCH_Config_SIB1>[\d]+).*?DMRS TypeA Position = (?P<DMRS_TypeA_Position>[a-zA-Z\d]+).*?SSB Subcarrier Offset = (?P<SSB_Subcarrier_Offset>[\d]+).*?Subcarrier Spacing Common = (?P<Subcarrier_Spacing_Common>[a-zA-Z\d]+)'
        # Use re.search to find the first match of the pattern in the packet_text
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            # If there is a match, extract the group dictionary
            entry.update(match.groupdict())
            # entry = match.groupdict()
            # Initialize an empty dictionary for modified entries
            modified_entry = {}
            # modified_entry['subtitle'] = subtitle
            # Iterate over each item in the entry dictionary
            for key, value in entry.items():
                # Replace underscores with spaces in the key
                new_key = key.replace('_', ' ')
                # Add the modified key and its value to the new dictionary
                modified_entry[new_key] = value
            modified_entry['__collection'] = config['__collection']
            modified_entry['__Raw_Data'] = str(config['__Raw_Data'])
            modified_entry['__KPI_type'] = config['__KPI_type']
            return modified_entry
        else:
            # Return None or an empty dictionary if there is no match
            return None