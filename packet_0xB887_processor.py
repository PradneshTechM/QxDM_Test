import re

class Packet_0xB887:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?'
        self.pattern2 = r'.*?Mapping 2.*?\|Mapping 3.*?\|.*?-+.*?\n(?P<table>[\s\S]*)'
        self.dict = {}
        self.result = []

    def extract_info(self):
        self.dict.update(self.entry)
        non_table_capture = self.regular_pattern()
        table_capture = self.table_pattern()
        if non_table_capture:  # Check if non_table_capture is not None
            self.dict.update(non_table_capture)
        if table_capture:
            for row in table_capture:
                for key, value in row.items():
                    self.dict[key] = value
                for additional_key in ['__collection', '__cell', '__Raw_Data', '__KPI_type', '__frequency']:
                    if additional_key in self.config:
                        if additional_key == '__collection':
                            self.dict[additional_key] = self.config[additional_key]
                            if int(self.dict['Carrier Id']) == 0:
                                self.dict['__cell'] = 'PCC'
                            elif int(self.dict['Carrier Id']) >= 1:
                                self.dict['__cell'] = 'SCC(' + self.dict['Carrier Id'] + ')'
                        self.dict[additional_key] = self.config[additional_key]
                self.result.append(self.dict)
        return self.result  # Return the updated dictionary

    def regular_pattern(self):
        match = re.search(self.pattern1, self.packet_text, re.DOTALL)
        if match:
            data = match.groupdict()
            modified_entry = {}
            for key, value in data.items():
                # Replace underscores with spaces in the key
                new_key = key.replace('_', ' ')
                # Add the modified key and its value to the new dictionary
                modified_entry[new_key] = value
            return modified_entry
        else:
            return None
        # if match:
        #     entry1 = match.groupdict()
        #     data = map_entry(entry1, self.config)
        #     return data
        # else:
        #     return None

    def table_pattern(self):
        match = re.search(self.pattern2, self.packet_text, re.DOTALL)
        carrier_ids = []  # Initialize an empty list to store dictionaries
        if match:
            # return table_extract(match, self.config, self.config['Records'])
            # Extract the 'table' named group which contains the data rows
            table_content = match.group('table').strip()

            # Split the captured content into rows based on newline characters
            rows = table_content.split('\n')
            for row in rows:  # Iterate over each row
                dict_1 = {}
                row_values = row.split('|')  # Split the current row by the '|' character to get individual values
                config_values = self.config['Records']
                for entry in config_values[0].items():  # Access the first (and only) item in the list, then iterate over its items
                    key, value = entry
                    db_field = value['DB Field']
                    index = value['index'] + 1
                    if index < len(row_values):  # Check if the index is within the bounds of row_values
                        row_value = row_values[index].strip()
                        if row_value:  # Add to dict_1 only if row_value is not empty
                            dict_1[db_field] = row_value
                if dict_1:  # Check if dict_1 is not empty before printing or adding to carrier_ids
                    for additional_key in ['__collection', '__cell', '__Raw_Data', '__KPI_type', '__frequency']:
                        if additional_key in self.config:
                            dict_1[additional_key] = self.config[additional_key]
                    carrier_ids.append(dict_1)
            return carrier_ids
        else:
            print("No data rows found.")