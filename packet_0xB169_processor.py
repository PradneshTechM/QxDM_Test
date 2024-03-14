import re


class Packet_0xB169:
    def extract_info(packet_text, config=None, entry=None):

        pattern = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Modulation Type = (?P<Modulation>[a-zA-Z]+).*?Cell Index = (?P<Cell_Index>[\d]+).*?MCS = (?P<MCS>[\d]+).*?CQI = (?P<CQI>[\da-zA-Z]+).*?HARQ ID = (?P<HARQ_ID>[\d]+)'
        # Use re.search to find the first match of the pattern in the packet_text
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            # If there is a match, extract the group dictionary
            entry.update(match.groupdict())            # Initialize an empty dictionary for modified entries
            modified_entry = {}
            # modified_entry['subtitle'] = subtitle
            # Iterate over each item in the entry dictionary
            for key, value in entry.items():
                # Replace underscores with spaces in the key
                new_key = key.replace('_', ' ')
                # Add the modified key and its value to the new dictionary
                modified_entry[new_key] = value
            if int(modified_entry['Cell Index']) == 0:
                modified_entry['_cell'] = 'PCC'
            elif int(modified_entry['Cell Index']) >= 1:
                modified_entry['_cell'] = 'SCC(' + modified_entry['Cell Index'] + ')'
            modified_entry['__collection'] = config['__collection']
            return modified_entry
        else:
            None
