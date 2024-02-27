import re


class Packet_0xB115:
    def extract_info(packet_text, config=None, entry=None):

        pattern = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Number of Barred Cells    = (?P<Number_of_Barred_Cells>[\d]+).*?Number of Detected Cells  = (?P<Number_of_Detected_Cells>[\d]+).*?Number of IC Cells.*?= (?P<Number_of_IC_Cells>[\d]+).*?EARFCN.*?=.*?(?P<EARFCN>[\d]+).*?\|.*?\d\|.*?(?P<SSS_Peak_Value>[\d]+)\|.*?(?P<Cell_ID>[\d]+)\|.*?(?P<CP>[a-zA-Z]+)\|.*?[a-zA-Z]+\|.*?(?P<Frequency_Offset_HZ>[\d]+)\|.*?[a-zA-Z0-9]+\|.*?[a-zA-Z/]+\|.*?(?P<Frame_Boundary>[\d]+)\|.*?(?P<Frame_Boundary_Range>[\d]+)\|'        # Use re.search to find the first match of the pattern in the packet_text
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
            return modified_entry
        else:
            # Return None or an empty dictionary if there is no match
            return None