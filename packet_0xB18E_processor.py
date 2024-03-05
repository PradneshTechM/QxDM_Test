import re

class Packet_0xB18E:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Use Init Search = (?P<Use_Init_Search>[\d]+).*?Num Candidates = (?P<num_candidates>[\d]+).*?'
        self.pattern2 = r".*?\|\(dBm/100KHz\).*?\|Pruned\|.*?-+.*?\n(?P<table>[\s\S]*)"
        self.dict = {}
        self.result = []

    def extract_info(self):
        self.dict.update(self.entry)
        non_table_capture = self.regular_pattern(self.config)
        table_capture = self.table_pattern()
        if non_table_capture:  # Check if non_table_capture is not None
            self.dict.update(non_table_capture)
        if table_capture:
            for row in table_capture:
                row_dict = self.dict.copy()
                for key, value in row.items():
                    row_dict[key] = value
                if self.config['__collection']:
                    row_dict["__collection"] = self.config.get('__collection')
                if self.config['__cell']:
                    row_dict["__cell"] = self.config.get('__cell')
                if self.config['__Raw_Data']:
                    row_dict["__Raw_Data"] = self.config.get('__Raw_Data')
                if self.config['__KPI_type']:
                    row_dict["__KPI_type"] = self.config.get('__KPI_type')
                self.result.append(row_dict)
        return self.result


    def regular_pattern(self, config):
        match = re.search(self.pattern1, self.packet_text, re.DOTALL)
        if match:
            regular_dict = {}
            regular_dict = match.groupdict()
            # entry = match.groupdict()
            key_mapping = {
                'Subs_ID': config['Subscription ID']['DB Field'],
                'Use_Init_Search': config['Use Init Search']['DB Field'],
                'num_candidates': config['Num Candidates']['DB Field']


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
                    if len(row_values) >= 7:  # Ensure there are enough values in the row to avoid IndexError
                        dict_1 = {}
                        # Extracting values from row by index
                        earfcn = row_values[2].strip()
                        band = row_values[3].strip()
                        bandwidth = row_values[4].strip()
                        energy = row_values[5].strip()
                        nb_energy = row_values[6].strip()

                        # Checking if each value contains a value
                        if earfcn:
                            dict_1['EARFCN'] = earfcn
                        if band:
                            dict_1['Band'] = band
                        if bandwidth:
                            dict_1['Bandwidth'] = bandwidth
                        if energy:
                            dict_1['Energy (dBm/100KHz)'] = energy
                        if nb_energy:
                            dict_1['NB_Energy (dBm/100KHz)'] = nb_energy
                        # appending to list as long as there is an entry in the dict
                        if dict_1:
                            carrier_ids.append(dict_1)
            return carrier_ids
        else:
            return None