import regex as re

class Packet_0xB97F:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<Subs_ID>\d+).*?Raster ARFCN = (?P<ARFCN>\d+).*?CC_ID = (?P<CC_ID>\d+).*?Serving Cell PCI = (?P<PCI>\d+)'
        self.pattern2 = r'.*?Beam RSRP L3.*?\|Beam RSRQ L3.*?\|.*?-+.*?\n(?P<table>[\s\S]*)'
        self.dict = {}
        self.result = []

    def extract_info(self):
        self.dict.update(self.entry)
        non_table_capture = self.regular_pattern()
        table_capture = self.table_pattern()
        if non_table_capture:  # Check if non_table_capture is not None
            self.dict.update(non_table_capture)
            # print(self.dict)
        if table_capture:
            for row in table_capture:
                row_dict = self.dict.copy()
                for key, value in row.items():
                    row_dict[key] = value
                    # self.dict[key] = value
                # print(self.dict)

                if '__collection' in self.config:
                    row_dict["__collection"] = self.config.get('__collection')
                if '__cell' in self.config:
                    if int(row_dict['CC_ID']) == 0:
                        row_dict["__cell"] = 'PCC'
                    elif int(row_dict['CC_ID']) >= 1:
                        row_dict["__cell"] = f'SCC{row_dict["CC_ID"]}'
                        # row_dict["__cell"] = self.config.get('__cell')
                if '__Raw_Data' in self.config:
                    row_dict["__Raw_Data"] = self.config.get('__Raw_Data')
                self.result.append(row_dict)
                # self.result.append(self.dict)
            # print(self.result)

        return self.result  # Return the updated dictionary

    def regular_pattern(self):
        match = re.search(self.pattern1, self.packet_text, re.DOTALL)
        if match:
            # # if self.dict['Subs_ID']:
            # #     self.dict[self.config['Subscription ID']['DB Field']] = self.dict['Subs_ID']
            # return match.groupdict()
            data = match.groupdict()
            modified_entry = {}
            for key, value in data.items():
                if key == 'Subs_ID':
                    modified_entry[self.config['Subscription ID']["DB Field"]] = value
                else:
                    modified_entry[key] = value
                # Replace underscores with spaces in the key
                # new_key = key.replace('_', ' ')
                # Add the modified key and its value to the new dictionary
                # modified_entry[new_key] = value
            return modified_entry
        else:
            return None

    def table_pattern(self):
        match = re.search(self.pattern2, self.packet_text, re.DOTALL)
        row_dicts = []  # Initialize an empty list to store dictionaries
        if match:
            # Extract the 'table' named group which contains the data rows
            table_content = match.group('table').strip()
            # Split the captured content into rows based on newline characters
            rows = table_content.split('\n')

            for row in rows:  # Iterate over each row
                dict_1 = {}
                row_values = row.split('|')  # Split the current row by the '|' character to get individual values
                config_values = self.config['Component Carrier List[0].Cells']
                for entry in config_values[0].items():  # Access the first (and only) item in the list, then iterate over its items
                    key, value = entry
                    db_field = value['DB Field']
                    index = value['index'] + 1
                    if index < len(row_values):  # Check if the index is within the bounds of row_values
                        row_value = row_values[index].strip()
                        if row_value:  # Add to dict_1 only if row_value is not empty
                            if db_field == 'RSRP(dBm)' and row_value != 0:
                                continue
                            elif db_field == 'RSRQ(dBm)' and row_value != 0:
                                continue
                            dict_1[db_field] = row_value
                if dict_1:  # Check if dict_1 is not empty before printing or adding to carrier_ids
                    row_dicts.append(dict_1)
            # print(carrier_ids)
            return row_dicts
        else:
            print("No data rows found.")