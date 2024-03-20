import regex as re
# import kpi_utils
# import json
class Packet_0x1569:
    def extract_info(lines, config, entry=None):
        # print(lines)
        # pattern = r'(?P<timestamp>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+)\s+\[\d+\]\s+0x1569.*?Subscription ID = (?P<subscription_id>\d+).*?Sequence Number = (?P<sequence_number>\d+).*?SSRC = (?P<ssrc>\d+).*?codecType = (?P<codec_type>\w+).*?LossType = (?P<loss_type>[\w\s]+).*?Total Packets Count = (?P<total_packets_count>\d+)'
        pattern = r'.*?0x1569.*?Subscription ID = (?P<subscription_id>\d+).*?Sequence Number = (?P<sequence_number>\d+).*?SSRC = (?P<ssrc>\d+).*?codecType = (?P<codec_type>[\w-]+).*?LossType = (?P<loss_type>[A-Z\s]+)\n.*?Total Packets Count = (?P<total_packets_count>\d+)'

        match = re.match(pattern, lines, re.DOTALL)
        if match:
            entry.update(match.groupdict())
            # key_mapping = {'subscription_id': 'Subscription ID', 'sequence_number': 'Sequence Number',
            #                'ssrc': 'SSRC', 'codec_type': 'codecType',
            #                'loss_type': 'LossType', 'total_packets_count': 'Total Packets Count'}
            # with open('config.json') as f:
            #     config = json.load(f)
            # key_mapping = {
            #     'subscription_id': 'Subscription ID',
            #     'sequence_number': 'Sequence Number',
            #     'ssrc': 'SSRC',
            #     'codec_type': 'codecType',
            #     'loss_type': 'LossType',
            #     'total_packets_count': 'Total Packets Count'
            # }
            key_mapping = {
                'subscription_id': config['Subscription ID']['DB Field'],
                'sequence_number': config['Sequence Number']['DB Field'],
                'ssrc': config['SSRC']['DB Field'],
                'codec_type': config['codecType']['DB Field'],
                'loss_type': config['LossType']['DB Field'],
                'total_packets_count': config['Total Packets Count']['DB Field']
            }


            # mapped_entry = {key_mapping[key]: value for key, value in entry.items() if key in key_mapping}
            mapped_entry = {key_mapping.get(key,key): value for key, value in entry.items()}
            mapped_entry["__collection"] = config.get('__collection')
            mapped_entry["__cell"] = config.get('__cell')
            mapped_entry["__KPI_type"] = config.get('__KPI_type')
            # mapped_entry = kpi_utils.map_entry(entry,config, key_mapping)

            # print(lines)
            return mapped_entry
        else:
            return None