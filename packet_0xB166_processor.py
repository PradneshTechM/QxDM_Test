import re

class Packet_0xB166:
    def extract_info(packet_text, config=None, entry=None):

        pattern = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Cell Index = (?P<Cell_Index>[\d]+).*?Logical Root Seq Index = (?P<Logical_Root_Seq_Index>[\d]+).*?PRACH Config = (?P<PRACH_Config>[\d]+).*?Preamble Format = (?P<Preamble_Format>[\d]+).*?Duplex Mode = (?P<Duplex_Mode>[a-zA-Z]+).*?High Speed Flag = (?P<High_Speed_Flag>[\d]+).*?PRACH Frequency Offset = (?P<PRACH_Frequency_Offset>[\d]+).*?Max Transmissions MSG3 = (?P<Max_Transmissions_MSG3>[\d]+).*?Cyclic Shift Zone Length = (?P<Cyclic_Shift_Zone_Length>[\d]+).*?RA Response Window Size = (?P<RA_Response_Window_Size>[\d]+)'  # Use re.search to find the first match of the pattern in the packet_text
        match = re.search(pattern, packet_text, re.DOTALL)
        dict_1 ={}
        dict_1.update(entry)
        if match:
            # If there is a match, extract the group dictionary
            # entry1 = match.groupdict()
            entry.update(match.groupdict())
            # data = map_entry(entry1, config)
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
            modified_entry['Packet_Type'] = config['Packet_Type']
            modified_entry['__Raw_Data'] = str(config['__Raw_Data'])
            dict_1.update(modified_entry)
            return dict_1
        else:
            # Return None or an empty dictionary if there is no match
            return None