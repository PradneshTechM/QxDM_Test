import re

class Packet_0xB887:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?'
        self.pattern2 = r'.*?Mapping 2.*?\|Mapping 3.*?\|.*?-+.*?\n(?P<table>[\s\S]*)'
        self.dict = {}

    def extract_info(self):
        self.dict.update(self.entry)
        non_table_capture = self.regular_pattern(self.config)
        table_capture = self.table_pattern()
        if non_table_capture:  # Check if non_table_capture is not None
            self.dict.update(non_table_capture)
        if table_capture:
            self.dict['Reports'] = {}  # Initialize the records key as an empty dictionary
            for i, entry in enumerate(table_capture, start=1):
                entry_key = f'report_{i}'  # Create a unique key for each entry
                self.dict['Reports'][entry_key] = entry
        return self.dict  # Return the updated dictionary

    def regular_pattern(self, config):
        match = re.search(self.pattern1, self.packet_text, re.DOTALL)
        if match:
            regular_dict = {}
            regular_dict = match.groupdict()
            # entry = match.groupdict()
            key_mapping = {
                'Subs_ID': config['Subscription ID']['DB Field']
            }
            mapped_entry = {key_mapping.get(key, key): value for key, value in regular_dict.items()}

            return mapped_entry
        else:
            return None

    def table_pattern(self):
        match = re.search(self.pattern2, self.packet_text, re.DOTALL)

        carrier_ids = []  # Initialize an empty list to store dictionaries

        if match:
            # Extract the 'table' named group which contains the data rows
            table_content = match.group('table').strip()

            # Split the captured content into rows based on newline characters
            rows = table_content.split('\n')

            if rows:  # Check if rows list is not empty
                for row in rows:  # Iterate over each row
                    row_values = row.split('|')  # Split the current row by the '|' character to get individual values
                    if len(row_values) > 30:  # Ensure there are enough values in the row to avoid IndexError
                        dict_1 = {}
                        # Extracting values from row by index
                        carrier_id = row_values[6].strip()
                        dl_bandwidth = row_values[10].strip()
                        pci = row_values[13].strip()
                        dl_earfcn = row_values[14].strip()
                        tb_size = row_values[16].strip()
                        dl_mcs = row_values[18].strip()
                        num_rubs = row_values[19].strip()

                        # Checking if each value contains a value
                        if carrier_id:
                            dict_1['Carrier ID'] = carrier_id
                        if dl_bandwidth:
                            dict_1['DL Bandwidth'] = dl_bandwidth
                        if pci:
                            dict_1['PCI'] = pci
                        if dl_earfcn:
                            dict_1['DL EARFCN'] = dl_earfcn
                        if tb_size:
                            dict_1['TB Size(Bytes)'] = tb_size
                        if dl_mcs:
                            dict_1['DL MCS'] = dl_mcs
                        if num_rubs:
                            dict_1['Num RBs'] = num_rubs
                        # appending to list as long as there is an entry in the dict
                        if dict_1:
                            carrier_ids.append(dict_1)
            return carrier_ids
        else:
            return None