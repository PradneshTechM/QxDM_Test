import re


class Packet_0xB168:
    def extract_info(packet_text, config=None, entry=None):

        pattern = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Cell Index = (?P<Cell_Index>[\d]+).*?RACH Procedure Type = (?P<RACH_Type>[a-zA-Z]+).*?RACH Procedure Mode = (?P<RACH_Mode>[a-zA-Z]+).*?RNTI Type = (?P<RNTI_Type>[a-zA-Z_]+).*?Timing Advance Included = (?P<Timing_Advance_Included>[a-zA-Z]+).*?Timing Advance = (?P<Timing_Advance>[\d]+)'
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
            if int(modified_entry['Cell Index']) == 0:
                modified_entry['_cell'] = 'PCC'
            elif int(modified_entry['Cell Index']) >= 1:
                modified_entry['_cell'] = 'SCC(' + modified_entry['Cell Index'] + ')'
            modified_entry['__collection'] = config['__collection']
            modified_entry['__KPI_type'] = config['__KPI_type']
            return modified_entry
        else:
            # Return None or an empty dictionary if there is no match
            return None