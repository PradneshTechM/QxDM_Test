import regex as re

class Packet_0xB823:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Standby Mode = (?P<Standby_Mode>[a-zA-Z\s]+)\n.*?DDS sub = (?P<DDS_sub>[a-zA-Z]+).*?HST mode = (?P<HST_mode>[a-zA-Z]+).*?Physical Cell ID = (?P<Physical_Cell_ID>[\d]+).*? NR Cell Global Identity = (?P<NR_Cell_Global_Identity>[a-zA-Z0-9]+).*?DL Frequency = (?P<DL_Frequency>[\d]+).*?UL Frequency = (?P<UL_Frequency>[\d]+).*?DL Bandwidth = (?P<DL_Bandwidth>[\d]+).*?UL Bandwidth = (?P<UL_Bandwidth>[\d]+).*?Cell Id = (?P<Cell_Id>[\d]+).*?Selected PLMN MCC = (?P<Selected_PLMN_MCC>[\d]+).*?Selected PLMN MNC = (?P<Selected_PLMN_MNC>[\d]+).*?TAC = (?P<TAC>[\d]+).*?Freq Band Indicator = (?P<Freq_Band_Indicator>[\d]+)'
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
            modified_entry['__cell'] = config['__cell']
            return modified_entry
        else:
            # Return None or an empty dictionary if there is no match
            return None