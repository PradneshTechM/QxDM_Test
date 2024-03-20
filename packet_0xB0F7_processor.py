import regex as re

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
            if '__collection' in config:
                mapped_entry["__collection"] = config.get('__collection')
            if '__cell' in config:
                mapped_entry["__cell"] = config.get('__cell')
            if '__Raw_Data' in config:
                mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
            # if config['__KPI_type']:
            #     mapped_entry["__KPI_type"] = config.get('__KPI_type')
            return mapped_entry
        else:
            return None