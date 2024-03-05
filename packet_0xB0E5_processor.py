import re


class Packet_0xB0E5:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r'.*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'

        # Use re.search to find the first match of the pattern in the packet_text
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            # If there is a match, extract the group dictionary
            entry.update(match.groupdict())

            # entry.update(match.groupdict())
            # entry = match.groupdict()
            # Initialize an empty dictionary for modified entries
            modified_entry = {}
            # Iterate over each item in the entry dictionary
            for key, value in entry.items():
                # Replace underscores with spaces in the key
                new_key = key.replace('_', ' ')
                # Add the modified key and its value to the new dictionary
                modified_entry[new_key] = value
            if config['__collection']:
                modified_entry['__collection'] = config['__collection']
            if config['__cell']:
                modified_entry['__cell'] = config['__cell']
            if config['Packet_Type']:
                modified_entry['Packet_Type'] = config['Packet_Type']
            if config['__Raw_Data']:
                modified_entry['__Raw_Data'] = str(config['__Raw_Data'])
            if config['__KPI_type']:
                modified_entry['__KPI_type'] = config['__KPI_type']
            return modified_entry
        else:
            # Return None or an empty dictionary if there is no match
            return None
