import re

class Packet_0x156E:
    def __init__(self):
        print("0x156E")
    def extract_info(lines, config, entry):
        # pattern = r"(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\w+\]\s+0x156E.*?Subscription ID = (?P<subscription_id>\d+).*?Direction = (?P<direction>\w+).*?Message ID = (?P<message_id>\w+).*?Response Code = (?P<response_code>.*)\n.*?CM Call ID = (?P<cm_call_id>\d+)\n.*?Sip Message = (?P<sip_message>.*?(?=\n)).*?CSeq: (?P<CSeq>.*?(?=\n)).*?P-Access-Network-Info: (?P<p_access_network_info>.*?(?=\n)).*?Reason: (?P<Reason>.*?(?=\n)).*?"
        pattern = r".*?0x156E.*?Subscription ID = (?P<subscription_id>\d+).*?Direction = (?P<direction>\w+).*?Message ID = (?P<message_id>\w+).*?Response Code = (?P<response_code>.*)\n.*?CM Call ID = (?P<cm_call_id>\d+)\n.*?Sip Message = (?P<sip_message>.*?(?=\n)).*?CSeq: (?P<CSeq>.*?(?=\n)).*?P-Access-Network-Info: (?P<p_access_network_info>.*?(?=\n)).*?Reason: (?P<Reason>.*?(?=\n)).*?"

        match = re.match(pattern, lines, re.DOTALL)
        if match:
            entry.update(match.groupdict())
            # print("entry before key mapping", entry)
            # utils.key_mapping(entry)
            # entry = match.groupdict()
            key_mapping = {
                'subscription_id': config['Subscription ID']['DB Field'],
                'direction': config['Direction']['DB Field'],
                'message_id': config['Message ID']['DB Field'],
                'response_code': config['Response Code']['DB Field'],
                'cm_call_id': config['CM Call ID']['DB Field'],
                'sip_message': config['Sip Message']['DB Field'],
                'p_access_network_info': config['P-Access-Network-Info']['DB Field'],
                'Reason': config['Reason']['DB Field']
            }
            parts = entry['CSeq'].split(' ', 1)
            if len(parts) == 2:
                entry['CSeq'], entry['Method'] = parts



            # mapped_entry = {key_mapping[key]: value for key, value in entry.items() if key in key_mapping}
            mapped_entry = {key_mapping.get(key, key): value for key, value in entry.items()}
            # final_entry = utils.metadata(mapped_entry, config)
            # for entry, value in mapped_entry.items():
            #     if value == None:

            if config['__collection']:
                mapped_entry["__collection"] = config.get('__collection')
            if config['__cell']:
                mapped_entry["__cell"] = config.get('__cell')
            if config['Packet_Type']:
                mapped_entry["Packet_Type"] = mapped_entry["Message ID"]
            if config['__Raw_Data']:
                mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
            if config['__KPI_type']:
                mapped_entry["__KPI_type"] = config.get('__KPI_type')

            return mapped_entry

        else:
            return None