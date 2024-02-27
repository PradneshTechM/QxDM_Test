import re
# import json
class Packet_0x1831:
    def extract_info(lines, config, entry):
        # print(lines)
        # pattern = r'(?P<timestamp>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\d+\]\s+0x1569.*?Subscription ID = (?P<subscription_id>\d+).*?Sequence Number = (?P<sequence_number>\d+).*?SSRC = (?P<ssrc>\d+).*?codecType = (?P<codec_type>\w+).*?LossType = (?P<loss_type>[\w\s]+).*?Total Packets Count = (?P<total_packets_count>\d+)'
        pattern = r'.*?0x1831.*?Subscription ID = (?P<subscription_id>\d+).*?Direction = (?P<direction>\w+).*?End Cause = (?P<end_cause>[A-Z\s]+)\n.*?Call Setup Delay = (?P<call_setup_delay>\d+).*?RAT = (?P<rat>\w+).*?Client End Cause = (?P<client_end_cause>[A-Z_]+)'

        match = re.match(pattern, lines, re.DOTALL)
        if match:
            entry.update(match.groupdict())
            # entry = match.groupdict()
            # print(entry)

            key_mapping = {
                'subscription_id': config['Subscription ID']['DB Field'],
                'end_cause': config['End Cause']['DB Field'],
                'call_setup_delay': config['Call Setup Delay']['DB Field'],
                'rat': config['RAT']['DB Field'],
                'client_end_cause': config['Client End Cause']['DB Field']

            }


            # mapped_entry = {key_mapping[key]: value for key, value in entry.items() if key in key_mapping}
            mapped_entry = {key_mapping.get(key,key): value for key, value in entry.items()}
            mapped_entry["__collection"] = config.get('__collection')
            mapped_entry["__frequency"] = config.get('__frequency')
            mapped_entry["__cell"] = config.get("__cell")
            if "__packet_message" in config:
                mapped_entry["__packet_message"] = entry["direction"]
            mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
            mapped_entry["__KPI_type"] = config.get('__KPI_type')

            # print(lines)
            return mapped_entry
        else:
            return None