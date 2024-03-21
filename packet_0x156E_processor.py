import regex as re
import parser.utils

class Packet_0x156E:
    def __init__(self):
        print("0x156E")
    def extract_info(lines, config, entry):
        pattern = r".*?0x156E.*?Subscription ID = (?P<subscription_id>\d+).*?Direction = (?P<direction>\w+).*?Message ID = (?P<message_id>\w+).*?Response Code = (?P<response_code>.*)\n.*?CM Call ID = (?P<cm_call_id>\d+)\n.*?Sip Message = (?P<sip_message>.*?(?=\n)).*?(?:.*?CSeq: (?P<CSeq>.*?(?=\n)))?.*?P-Access-Network-Info: (?P<p_access_network_info>.*?(?=\n)).*?Reason: (?P<Reason>.*?(?=\n)).*?"
        match = re.match(pattern, lines, re.DOTALL)
        if match:
            entry.update(match.groupdict())

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
            if entry['CSeq'] != None:
                parts = entry['CSeq'].split(' ', 1)
                if len(parts) == 2:
                    entry['CSeq'], entry['Method'] = parts
            else:
                entry = {k: v for k, v in entry.items() if v is not None}




            mapped_entry = {key_mapping.get(key, key): value for key, value in entry.items()}


            if '__collection' in config:
                mapped_entry["__collection"] = config.get('__collection')
            if '__cell' in config:
                mapped_entry["__cell"] = config.get('__cell')
            if '__Packet_Type' in config:
                mapped_entry["Packet_Type"] = mapped_entry["Message ID"]
            if '__Raw_Data' in config:
                mapped_entry["__Raw_Data"] = config.get('__Raw_Data')


            return mapped_entry

        else:
            return None