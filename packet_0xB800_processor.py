import re

class Packet_0xB800:
    def __init__(self):
        print("0xB800")
    def extract_info(lines, config, entry):
        # pattern = r".*?0xB800.*? --  (?P<msg_subtitle>.*)\nSubscription ID = (?P<subscription_id>\d+).*?nr5g_smm_msg\n(?P<nr5g_smm_msg>.*?(?=\n)).*?_5gsm_cause\n(?P<_5gsm_cause>.*?(?=\n)).*?qci = (?P<qci>.*?(?=\n))"
        pattern = r".*?0xB800.*? --  (?P<msg_subtitle>.*)\nSubscription ID = (?P<subscription_id>\d+).*?nr5g_smm_msg\n\s*(?P<nr5g_smm_msg>.*?(?=\n)).*?_5gsm_cause\n\s*(?P<_5gsm_cause>.*?(?=\n)).*?qci = (?P<qci>.*?(?=\n))"
        match = re.match(pattern, lines, re.DOTALL)
        if match:
            entry.update(match.groupdict())
            # entry = match.groupdict()
            entry['_5gsm_cause'] = entry['_5gsm_cause'].strip(" ")
            key_mapping = {
                'subscription_id': config['Subscription ID']['DB Field'],
                'nr5g_smm_msg': config['nr5g_smm_msg']['DB Field'],
                '_5gsm_cause': config['_5gsm_cause']['DB Field'],
                'eps_qos.qci': config['eps_qos.qci']['DB Field']
            }
            mapped_entry = {key_mapping.get(key, key): value for key, value in entry.items()}
            if config['__collection']:
                mapped_entry["__collection"] = config.get('__collection')
            # mapped_entry["__frequency"] = config.get('__frequency')
            if config['__cell']:
                mapped_entry["__cell"] = config.get('__cell')

            # mapped_entry["__packet_message"] = entry['msg_subtitle']
            if "Packet_Type" in config:
                mapped_entry["Packet_Type"] = entry["msg_subtitle"]
                mapped_entry.pop("msg_subtitle", None)
            # mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
            if config['__KPI_type']:
                mapped_entry["__KPI_type"] = config.get('__KPI_type')

            return mapped_entry
        else:
            return None