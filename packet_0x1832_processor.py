import regex as re
# import json
class Packet_0x1832:
    def extract_info(lines, config, entry):
        # print(lines)
        # pattern = r'(?P<timestamp>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\d+\]\s+0x1569.*?Subscription ID = (?P<subscription_id>\d+).*?Sequence Number = (?P<sequence_number>\d+).*?SSRC = (?P<ssrc>\d+).*?codecType = (?P<codec_type>\w+).*?LossType = (?P<loss_type>[\w\s]+).*?Total Packets Count = (?P<total_packets_count>\d+)'
        pattern = r'.*?0x1832.*?Subscription ID = (?P<subscription_id>\d+).*?Registration Type = (?P<registration_type>\w+-\w+).*?Result = (?P<result>\w+)\n'

        match = re.match(pattern, lines, re.DOTALL)
        if match:
            entry.update(match.groupdict())

            # entry = match.groupdict()
            # print(entry)
            key_mapping = {
                'subscription_id': config['Subscription ID']['DB Field'],
                'registration_type': config['Registration Type']['DB Field'],
                'result': config['Result']['DB Field']
            }


            # mapped_entry = {key_mapping[key]: value for key, value in entry.items() if key in key_mapping}
            mapped_entry = {key_mapping.get(key,key): value for key, value in entry.items()}
            if '__collection' in config:
                mapped_entry["__collection"] = config.get('__collection')
            if '__cell' in config:
                mapped_entry["__cell"] = config.get("__cell")
            if "Packet_Type" in config:
                mapped_entry["Packet_Type"] = config.get('Packet_Type')
            if '__Raw_Data' in config:
                mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
            if '__KPI_type' in config:
                mapped_entry["__KPI_type"] = config.get('__KPI_type')

            # print(lines)
            return mapped_entry
        else:
            return None