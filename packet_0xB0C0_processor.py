import re

import re

class Packet_0xB0C0:
    def __init__(self):
        print("0xB0C0")

    def extract_info(lines, config, entry):
        # pattern = r"(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\w+\]\s+0x156E.*?Subscription ID = (?P<subscription_id>\d+).*?Direction = (?P<direction>\w+).*?Message ID = (?P<message_id>\w+).*?Response Code = (?P<response_code>.*)\n.*?CM Call ID = (?P<cm_call_id>\d+)\n.*?Sip Message = (?P<sip_message>.*?(?=\n)).*?CSeq: (?P<CSeq>.*?(?=\n)).*?P-Access-Network-Info: (?P<p_access_network_info>.*?(?=\n)).*?Reason: (?P<Reason>.*?(?=\n)).*?"
        patterns = [r".*?0xB0C0.*?Subscription ID = (?P<subscription_id>\d+).*?Physical Cell ID = (?P<PCI>\d+).*?Freq = (?P<Frequency>\d+).*?PDU Number = (?P<pdu_number>.*?(?=,)).*?{\n\s+(?P<message_c1>.*?).\n*?freqBandIndicator",
                    r".*?0xB0C0.*?Subscription ID = (?P<subscription_id>\d+).*?Physical Cell ID = (?P<PCI>\d+).*?Freq = (?P<Frequency>\d+).*?PDU Number = (?P<pdu_number>.*?(?=,)).*?establishmentCause (?P<establishmentCause>.*?(?=,)).*?"]
        for pattern in patterns:
            match = re.match(pattern, lines, re.DOTALL)
            if match:
                entry.update(match.groupdict())
                # entry = match.groupdict()
                key_mapping = {
                    'subscription_id': config['Subscription ID']['DB Field'],
                    'pdu_number': config['PDU Number']['DB Field'],
                    'message_c1': config['message c1 :']['DB Field'],
                    'establishmentCause': config['establishmentCause']['DB Field']
                }



                # mapped_entry = {key_mapping[key]: value for key, value in entry.items() if key in key_mapping}
                mapped_entry = {key_mapping.get(key, key): value for key, value in entry.items()}
                mapped_entry["__collection"] = config.get('__collection')
                # mapped_entry["__frequency"] = config.get('__frequency')
                mapped_entry["__cell"] = config.get('__cell')
                mapped_entry["__packet_message"] = entry['Subtitle']
                mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
                mapped_entry["__KPI_type"] = config.get('__KPI_type')

                return mapped_entry

        else:
            return None