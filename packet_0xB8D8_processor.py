import re
from decimal import Decimal
# from kpi_utils import map_entry


class Packet_0xB8D8:
    def extract_info(packet_text, config=None, entry= None):
        pattern = r'.*?0xB8D8.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Cell Id = (?P<PCI>[\d]+).*?Carrier Index = (?P<Carrier_Index>[\d]+).*?Reference Signal = (?P<Reference_Signal>[a-zA-Z\d]+).*?RX\[0\].*?SNR = (?P<SINR_DBM>[\d\.]+).*?'
        dict_1 = {}
        dict_1.update(entry)
        # Use re.search to find the first match of the pattern in the packet_text
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            # entry1 = match.groupdict()
            # data = map_entry(entry1, config)
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
                    if new_key == 'Subs ID':
                        number = int(value)
                        new_value = abs(number)
                        modified_entry[new_key] = new_value
                    elif new_key == 'PCI':
                        number = int(value)
                        new_value = abs(number)
                        modified_entry[new_key] = new_value
                    elif new_key == 'SINR(dBm)':
                        new_value = int(value)
                        # new_value = Decimal(value)
                        modified_entry[new_key] = new_value
                    else:
                    # Add the modified key and its value to the new dictionary
                        modified_entry[new_key] = value
            if int(modified_entry['Carrier Index']) == 0:
                modified_entry['_Cell'] = 'PCC'
            modified_entry['__Raw_Data'] = str(config['__Raw_Data'])
            # modified_entry['__KPI_type'] = config['__KPI_type']
            return modified_entry
            # dict_1.update(data)
            # return dict_1
        else:
            # Return None or an empty dictionary if there is no match
            return None