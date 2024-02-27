import re

class Packet_0xB0F7:
    def __init__(self):
        print("0xB0F7")
    def extract_info(lines, config, entry):
        # pattern = r"(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\w+\]\s+0xB0F7.*?Subscription ID = (?P<subscription_id>\d+).*?Trans Id = (?P<trans_id>\w+).*?Network Select Mode = (?P<network_select_mode>.*?(?=\n))"
        pattern = r".*?0xB0F7.*?Subscription ID = (?P<subscription_id>\d+).*?Trans Id = (?P<trans_id>\w+).*?Network Select Mode = (?P<network_select_mode>.*?(?=\n))"

        match = re.match(pattern, lines, re.DOTALL)
        if match:
            entry.update(match.groupdict())
            # entry = match.groupdict()
            key_mapping = {
                'subscription_id': config['Subscription ID']['DB Field'],
                'trans_id': config['Trans Id']['DB Field'],
                'network_select_mode': config['Network Select Mode']['DB Field']
            }
            mapped_entry = {key_mapping.get(key, key): value for key, value in entry.items()}
            mapped_entry["__collection"] = config.get('__collection')
            # mapped_entry["__frequency"] = config.get('__frequency')
            mapped_entry["__cell"] = config.get('__cell')
            # mapped_entry["__packet_message"] = config.get('__packet_message')
            mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
            mapped_entry["__KPI_type"] = config.get('__KPI_type')

            return mapped_entry
        else:
            return None