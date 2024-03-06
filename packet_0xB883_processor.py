import re
# from utils import map_entry, metadata
#from json_comments import cell_PCC
class Packet_0xB883:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?'
        self.pattern2 = r".*?\|Shift.*?\|Status\|.*?-+.*?\n(?P<table>[\s\S]*)"
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
                if self.config['__Raw_Data']:
                    row_dict["__Raw_Data"] = self.config.get('__Raw_Data')
                if self.config['__KPI_type']:
                    row_dict["__KPI_type"] = self.config.get('__KPI_type')
                if self.config['__collection']:
                    row_dict['__collection'] = self.config.get('__collection')
                if self.config['__cell']:
                    if int(row_dict["Carrier ID"]) == 0:
                        row_dict['__cell'] = 'PCC'
                    elif int(row_dict["Carrier ID"]) >= 1:
                        row_dict['__cell'] = f'SCC{row_dict["Carrier ID"]}'
                if self.config['Packet_Type']:
                    row_dict["Packet_Type"] = self.config.get('Packet_Type')
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
                    if len(row_values) >= 23:  # Ensure there are enough values in the row to avoid IndexError
                        dict_1 = {}
                        # Extracting values from row by index
                        carrier_id = row_values[6].strip()
                        mcs_table = row_values[22].strip()
                        rnti_type = row_values[7].strip()
                        harq_id = row_values[11].strip()
                        mcs = row_values[13].strip()
                        tx_mode =row_values[14].strip()
                        num_rbs = row_values[16].strip()


                        # Checking if each value contains a value
                        if carrier_id:
                            dict_1['Carrier ID'] = carrier_id
                        if mcs_table:
                            dict_1['MCS Table'] = mcs_table
                        if rnti_type:
                            dict_1['RNTI Type'] = rnti_type
                        if harq_id:
                            dict_1['HARQ ID'] = harq_id
                        if mcs:
                            dict_1['MCS'] = mcs
                        if tx_mode:
                            dict_1['TX Mode'] = tx_mode
                        if num_rbs:
                            dict_1['Num RBs'] = num_rbs
                        # appending to list as long as there is an entry in the dict
                        if dict_1:
                            carrier_ids.append(dict_1)
            return carrier_ids
        else:
            return None