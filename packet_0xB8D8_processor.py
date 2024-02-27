import re


class Packet_0xB8D8:
    def extract_info(packet_text, config=None, entry= None):
        pattern = r'.*?0xB8D8.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Cell Id = (?P<PCI>[\d]+).*?Carrier Index = (?P<Carrier_Index>[\d]+).*?Reference Signal = (?P<Reference_Signal>[a-zA-Z\d]+).*?RX\[0\].*?SNR = (?P<SINR_DBM>[\d\.\sa-zA-Z]+)\n'

        # Use re.search to find the first match of the pattern in the packet_text
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            # If there is a match, extract the group dictionary
            entry.update(match.groupdict())

            # entry = match.groupdict()
            key_mapping = {
                'SINR_DBM': config['RX[0].SNR']['DB Field']
            }
            if entry['Reference_Signal'] == 'TRS':
                return None
            # Initialize an empty dictionary for modified entries
            modified_entry = {}

            # Iterate over each item in the entry dictionary
            for key, value in entry.items():
                if key in key_mapping:
                    new_key = key_mapping.get(key, key)
                    modified_entry[new_key] = value
                # Replace underscores with spaces in the key
                else:
                    new_key = key.replace('_', ' ')
                    # Add the modified key and its value to the new dictionary
                    modified_entry[new_key] = value
            if int(modified_entry['Carrier Index']) == 0:
                modified_entry['_Cell'] = 'PCC'
            modified_entry['__Raw_Data'] = str(config['__Raw_Data'])
            modified_entry['__KPI_type'] = config['__KPI_type']
            return modified_entry
        else:
            # Return None or an empty dictionary if there is no match
            return None
