import regex as re

class Packet_0xB16A:
    def extract_info(packet_text,config=None, entry= None):
        pattern = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?SFN = (?P<SFN>[\d]+).*?Sub-fn = (?P<Sub_fn>[\d]+).*?Contention Result = (?P<Contention_Result>[a-zA-Z]+).*?UL ACK Timing SFN = (?P<UL_ACK_Timing_SFN>[\d]+).*?UL ACK Timing Sub-fn = (?P<UL_ACK_Timing_Sub_fn>[\d]+)'

        # Use re.search to find the first match of the pattern in the packet_text
        match = re.search(pattern, packet_text, re.DOTALL)
        if match:
            # If there is a match, extract the group dictionary
            entry.update(match.groupdict())
            # entry = match.groupdict()
            key_mapping = {
                'UL_ACK_Timing_Sub_fn': config['UL ACK Timing Sub-fn']['DB Field'],
                'Sub_fn': config['Sub-fn']['DB Field']
            }
            # Initialize an empty dictionary for modified entries
            modified_entry = {}
            # modified_entry['subtitle'] = subtitle
            # Iterate over each item in the entry dictionary
            for key, value in entry.items():
                if key in key_mapping:
                    new = key_mapping.get(key, key)
                    modified_entry[new] = value
                # Replace underscores with spaces in the key
                else:
                    new_key = key.replace('_', ' ')
                    # Add the modified key and its value to the new dictionary
                    modified_entry[new_key] = value
            modified_entry['__cell'] = 'LTE'
            modified_entry['Packet_Type'] = 'PDCCH'
            return modified_entry
        else:
            # Return None or an empty dictionary if there is no match
            return None