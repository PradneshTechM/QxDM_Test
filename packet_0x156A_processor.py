import re

class Packet_0x156A:
    def __init__(self):
        print("0x156A")
    def extract_info(lines, config, entry):
        # pattern = r"(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\w+\]\s+0x156A.*?Subscription ID = (?P<subscription_id>\d+).*?Direction = (?P<Direction>.*?(?=\n)).*?Rat Type = (?P<rat_type>\w+).*?Type = (?P<Type>.*?(?=\n)).*?Codec Type = (?P<codec_type>.*?(?=\n)).*?"
        # pattern = r"\s+\[\w+\]\s+0x156A.*?Subscription ID = (?P<subscription_id>\d+).*?Direction = (?P<Direction>.*?(?=\n)).*?Rat Type = (?P<rat_type>\w+).*?Type = (?P<Type>.*?(?=\n)).*?Codec Type = (?P<codec_type>.*?(?=\n)).*?"
        pattern = r".*?0x156A.*?Subscription ID = (?P<subscription_id>\d+).*?Direction = (?P<Direction>.*?(?=\n)).*?Rat Type = (?P<rat_type>\w+).*?Type = (?P<Type>.*?(?=\n)).*?Codec Type = (?P<codec_type>.*?(?=\n)).*?"

        match = re.match(pattern, lines, re.DOTALL)
        if match:

            entry.update(match.groupdict())
            # entry = match.groupdict()
            key_mapping = {
                'subscription_id': config['Subscription ID']['DB Field'],
                'rat_type': config['Rat Type']['DB Field'],
                'codec_type': config['Codec Type']['DB Field']
            }
            mapped_entry = {key_mapping.get(key, key): value for key, value in entry.items()}
            if config['__collection']:
                mapped_entry["__collection"] = config.get('__collection')
            if config['__cell']:
                mapped_entry["__cell"] = config.get('__cell')
            if config['__Raw_Data']:
                mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
            if config['__KPI_type']:
                mapped_entry["__KPI_type"] = config.get('__KPI_type')

            return mapped_entry
        else:
            return None