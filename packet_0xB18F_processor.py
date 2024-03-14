import re
# from kpi_utils import table_extract, map_entry
class Packet_0xB18F:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?'
        self.pattern2 = r'.*?Buffer.*?\|Cell Type.*?\|.*?-+.*?\n(?P<table>[\s\S]*).*?Neighbors'
        self.pattern3 = r'.*?Neighbors.*?Buffer.*?\|Cell Type.*?\|.*?-+.*?\n(?P<table>[\s\S]*).*?'
        self.dict = {}
        self.table_dict ={}
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
                for additional_key in ['__Raw_Data', '__collection', '__cell', '__frequency']:
                    if additional_key in self.config:
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
        match2 = re.search(self.pattern3, self.packet_text, re.DOTALL)
        carrier_ids = []  # Initialize an empty list to store dictionaries
        if match:
            dict_1 = {}

            # return table_extract(match, self.config, self.config['Records'])
            # Extract the 'table' named group which contains the data rows
            table_content = match.group('table').strip()

            # Split the captured content into rows based on newline characters
            rows = table_content.split('\n')

            for row in rows:  # Iterate over each row
                row_values = row.split('|')  # Split the current row by the '|' character to get individual values
                config_values = self.config['Serving']
                for entry in config_values[0].items():  # Access the first (and only) item in the list, then iterate over its items
                    key, value = entry
                    db_field = 'Serving '+ value['DB Field']
                    index = value['index'] + 1
                    if index < len(row_values):  # Check if the index is within the bounds of row_values
                        row_value = row_values[index].strip()
                        if row_value:  # Add to dict_1 only if row_value is not empty
                            dict_1[db_field] = row_value
                if dict_1:  # Check if dict_1 is not empty before printing or adding to carrier_ids
                    self.table_dict.update(dict_1)
        if match2:
            dict_2 = {}

            # return table_extract(match, self.config, self.config['Records'])
            # Extract the 'table' named group which contains the data rows
            table_content = match.group('table').strip()

            # Split the captured content into rows based on newline characters
            rows = table_content.split('\n')

            for row in rows:  # Iterate over each row
                row_values = row.split('|')  # Split the current row by the '|' character to get individual values
                config_values = self.config['Neighbors']
                for entry in config_values[0].items():  # Access the first (and only) item in the list, then iterate over its items
                    key, value = entry
                    db_field = 'Neighbors ' + value['DB Field']
                    index = value['index'] + 1
                    if index < len(row_values):  # Check if the index is within the bounds of row_values
                        row_value = row_values[index].strip()
                        if row_value:  # Add to dict_1 only if row_value is not empty
                            dict_2[db_field] = row_value
                if dict_2:  # Check if dict_1 is not empty before printing or adding to carrier_ids
                    self.table_dict.update(dict_2)
            carrier_ids.append(self.table_dict)
            return carrier_ids
        else:
            print("No data rows found.")