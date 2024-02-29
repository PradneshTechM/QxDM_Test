import re

class Packet_0xB80B:
    def __init__(self):
        print("0xB80B")
    def extract_info(lines, config, entry):
        # pattern = r".*?0xB80B.*? --  (?P<msg_subtitle>.*)\nSubscription ID = (?P<subscription_id>\d+).*?nr5g_mm_msg\n(?P<nr5g_mm_msg>.*?(?=\n))"
        pattern = r".*?0xB80B.*? --  (?P<msg_subtitle>.*)\nSubscription ID = (?P<subscription_id>\d+).*?nr5g_mm_msg\n\s*(?P<nr5g_mm_msg>.*?(?=\n))"
        match = re.match(pattern, lines, re.DOTALL)
        if match:
            entry.update(match.groupdict())
            # entry = match.groupdict()
            key_mapping = {
                'subscription_id': config['Subscription ID']['DB Field'],
                'nr5g_mm_msg': config['nr5g_mm_msg']['DB Field']
            }
            mapped_entry = {key_mapping.get(key, key): value for key, value in entry.items()}
            mapped_entry["__collection"] = config.get('__collection')
            mapped_entry["__frequency"] = config.get('__frequency')
            mapped_entry["__cell"] = config.get('__cell')
            if "__packet_message" in config:
                mapped_entry["__packet_message"] = entry["msg_subtitle"]
                mapped_entry.pop("msg_subtitle", None)
            # mapped_entry["__packet_message"] = entry['msg_subtitle']
            # mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
            mapped_entry["__KPI_type"] = config.get('__KPI_type')

            return mapped_entry
        else:
            return None