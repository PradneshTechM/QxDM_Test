import re
# from utils import map_entry, metadata
class Packet_0xB171:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?'
        self.pattern2 = r".*?\(f\(i\)\).*?\|Power.*?\|.*?-+.*?\n(?P<table>[\s\S]*)"
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
                    # self.dict[key] = value
                if self.config['__collection']:
                    row_dict['__collection'] = self.config.get('__collection')
                if self.config['__cell']:
                    if int(row_dict["Cell index"]) == 0:
                        row_dict['__cell'] = 'PCC'
                    elif int(row_dict["Cell index"]) >= 1:
                        row_dict['__cell'] = f'SCC{self.dict["Cell index"]}'
                if self.config['Packet_Type']:
                    row_dict["Packet_Type"] = self.config.get('Packet_Type')
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
                    if len(row_values) >= 9:  # Ensure there are enough values in the row to avoid IndexError
                        dict_1 = {}
                        # Extracting values from row by index
                        cell_index = row_values[2].strip()
                        path_loss = row_values[6].strip()
                        srs_actual_tx_power = row_values[9].strip()


                        # Checking if each value contains a value
                        if cell_index:
                            dict_1['Cell index'] = cell_index
                        if path_loss:
                            dict_1['Pathloss'] = path_loss
                        if srs_actual_tx_power:
                            dict_1['Actual Tx Power (dBm)'] = srs_actual_tx_power
                        # appending to list as long as there is an entry in the dict
                        if dict_1:
                            carrier_ids.append(dict_1)
            return carrier_ids
        else:
            return None