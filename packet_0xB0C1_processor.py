import re

class Packet_0xB0C1:
    def __init__(self):
        print("0xB0C1")
    def extract_info(lines, config, entry):
        # pattern = r"(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\w+\]\s+0xB0C1.*?Subscription ID = (?P<subscription_id>\d+).*?Physical cell ID = (?P<PCI>\d+).*?FREQ = (?P<Frequency>\d+).*?Number of TX Antennas = (?P<no_tx_antennas>\d+).*?DL Bandwidth = (?P<dl_bandwidth>.*)"
        pattern = r"(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\w+\]\s+0xB0C1.*?Subscription ID = (?P<subscription_id>\d+).*?Physical cell ID = (?P<PCI>\d+).*?FREQ = (?P<Frequency>\d+).*?Number of TX Antennas = (?P<no_tx_antennas>\d+).*?DL Bandwidth = (?P<dl_bandwidth>.*)"

        match = re.match(pattern, lines, re.DOTALL)
        if match:
            entry.update(match.groupdict())

            key_mapping = {
                'subscription_id': config['Subscription ID']['DB Field'],
                'PCI': config['Physical cell ID']['DB Field'],
                'Frequency': config['FREQ']['DB Field'],
                'no_tx_antennas': config['Number of TX Antennas']['DB Field'],
                'dl_bandwidth': config['DL Bandwidth']['DB Field']
            }
            # mapped_entry = {key_mapping[key]: value for key, value in entry.items() if key in key_mapping}
            mapped_entry = {key_mapping.get(key, key): value for key, value in entry.items()}
            if config['__collection']:
                mapped_entry["__collection"] = config.get('__collection')
            if config['__frequency']:
                mapped_entry["__frequency"] = config.get('__frequency')
            if config['__cell']:
                mapped_entry["__cell"] = config.get('__cell')
            if config['Packet_Type']:
                mapped_entry["Packet_Type"] = config.get('Packet_Type')
            if config['__Raw_Data']:
                mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
            # if config['__KPI_type']:
            #     mapped_entry["__KPI_type"] = config.get('__KPI_type')

            return mapped_entry

        else:
            return None