import regex as re
# import json
class Packet_0x1830:
    def extract_info(lines, config, entry):
        pattern = r'.*?0x1830.*?Subscription ID = (?P<subscription_id>\d+).*?Direction = (?P<direction>\w+).*?Result = (?P<result>\w+).*?Call Setup Delay = (?P<call_setup_delay>\d+).*?RAT = (?P<rat>\w+)'

        match = re.match(pattern, lines, re.DOTALL)
        if match:
            entry.update(match.groupdict())

            # entry = match.groupdict()
            # print(entry)
            key_mapping = {
                'subscription_id': config['Subscription ID']['DB Field'],
                'direction': config['Direction']['DB Field'],
                'result': config['Result']['DB Field'],
                'call_setup_delay': config['Call Setup Delay']['DB Field'],
                'rat': config['RAT']['DB Field']
            }

            # mapped_entry = {key_mapping[key]: value for key, value in entry.items() if key in key_mapping}
            mapped_entry = {key_mapping.get(key,key): value for key, value in entry.items()}
            if '__collection' in config:
                mapped_entry["__collection"] = config.get('__collection')
            if '__cell' in config:
                mapped_entry["__cell"] = config.get("__cell")
            if '__frequency' in config:
                mapped_entry["__frequency"] = config.get('__frequency')
            if "Packet_Type" in config:
                mapped_entry["Packet_Type"] = entry["direction"]
            if '__Raw_Data' in config:
                mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
            if '__KPI_type' in config:
                mapped_entry["__KPI_type"] = config.get('__KPI_type')


            # print(lines)
            return mapped_entry
        else:
            return None