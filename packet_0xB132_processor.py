import regex as re
from parser.evaluate import evaluate
from parser.kpi_utils import table_config, map_entry
class Packet_0xB132:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'Subscription ID = (?P<subs_id>\d+).*?Cell Id = (?P<cell_id>[\d]+).*?EARFCN = (?P<earfcn>[\d]+).*?System BW = (?P<system_bw>[\d]+).*?Num HARQ = (?P<num_harq>[\d]+).*?UE Category = (?P<ue_category>[\d]+).*?TX Mode = (?P<tx_mode>[\w]+).*?Num eNb Tx Ant = (?P<num_enb_Tx_Ant>[\d]+)'
        self.dict = {}
        self.result = []

    def extract_info(self):
        self.dict.update(self.entry)
        non_table_capture = self.regular_pattern()
        table_capture = self.table_pattern()
        table_capture2 = self.table_pattern2()
        if non_table_capture:  # Check if non_table_capture is not None
            self.dict.update(non_table_capture)
        if table_capture:
            for row in table_capture:
                row_dict = self.dict.copy()
                row_dict.update(row)
                self.result.append(row_dict)
        if table_capture2:
            for row in table_capture2:
                row_dict = self.dict.copy()
                row_dict.update(row)
                self.result.append(row_dict)
        return self.result  # Return the updated dictionary

    def regular_pattern(self):
        fields_to_extract = ['Subscription ID', 'Cell Id', 'EARFCN', 'System BW', 'Num HARQ', 'UE Category', 'TX Mode',
                             'Num eNb Tx Ant']
        extracted_data = {}
        for field in fields_to_extract:
            field_start_index = self.packet_text.find(field)
            if field_start_index != -1:
                field_line = self.packet_text[field_start_index:]
                field_end_index = field_line.find('\n')
                if field_end_index != -1:
                    field_line = field_line[:field_end_index]
                    field_parts = field_line.split('=')
                    if len(field_parts) == 2:
                        field_value = field_parts[1].strip()
                        field_key = field_parts[0].strip()
                        extracted_data[field_key] = field_value

        if extracted_data:
            modified_entry = map_entry(extracted_data, self.config)
            return modified_entry
        else:
            return None

    def table_pattern(self):
        raw_text = self.packet_text
        start_marker = "TB Info Record[0]"
        end_marker = "TB Info Record[1]"
        tb_info_record_0_section = raw_text.split(start_marker)[1].split(end_marker)[0]

        tb_config_start_marker = "   TB Top"
        tb_config_end_marker = "   TB Config"
        tb_config_section = tb_info_record_0_section.split(tb_config_start_marker)[1].split(tb_config_end_marker)[0]

        lines_tb_config = tb_config_section.split('\n')

        header_found = False
        data_rows = []
        returned_ouput = []
        for line in lines_tb_config:
            if "Frame" in line:
                header_found = True
            elif header_found and line.strip().startswith('|'):  # Data lines start with '|'
                data_rows.append(line.strip())

        for row in data_rows:  # Iterate over each row
            dict_1 = {}
            row_values = row.split('|')  # Split the current row by the '|' character to get individual values
            for entry in self.config['TB Info Record[0]'][0].items():  # Access the first (and only) item in the list, then iterate over its items
                key, value = entry
                db_field = value['DB Field']
                index = value['index'] + 1
                if index < len(row_values):  # Check if the index is within the bounds of row_values
                    row_value = row_values[index].strip()
                    if row_value:  # Add to dict_1 only if row_value is not empty
                        dict_1[db_field] = row_value
            if dict_1:  # Check if dict_1 is not empty before printing or adding to carrier_ids
                for additional_key in ['__Raw_Data','__collection','__cell', 'Packet_Type','__frequency']:
                    if additional_key in self.config:
                        # Inside simple_map_entry, when processing __cell:
                        if additional_key in ['__cell','Packet_Type','__Raw_Data'] and isinstance(self.config[additional_key], list):
                            code_arr = [line.replace("\\", "") for line in self.config[additional_key]]
                            # evaluate(config[additionalkey], mapped_data)
                            # Pass mapped_data to evaluate, allowing the executed code to access/modify it
                            result = evaluate(code_arr, dict_1)  # Using mapped_data as both input and output
                            # Optionally capture the result and do something with it, like updating mapped_data with new data
                            if result is not None:
                                dict_1.update(result)  # Example of using the result. Adjust as needed.

                            else:
                                # If __cell doesn't meet the criteria, skip execution
                                continue

                        else:
                            dict_1[additional_key] = self.config[additional_key]
                returned_ouput.append(dict_1)
        return returned_ouput

    def table_pattern2(self):
        raw_text = self.packet_text
        start_marker = "TB Info Record[0]"
        end_marker = "TB Info Record[1]"
        tb_info_record_0_section = raw_text.split(start_marker)[1].split(end_marker)[0]

        # Step 2: Isolate the TB Config section within TB Info Record[0]
        tb_config_start_marker = "   TB Config"
        tb_config_end_marker = "   TB"  # Assuming "TB" uniquely marks the end of the TB Config section
        tb_config_section = tb_info_record_0_section.split(tb_config_start_marker)[1].split(tb_config_end_marker)[0]

        # Step 3: Split the isolated TB Config section into lines for processing
        lines_tb_config = tb_config_section.split('\n')

        # Identify the "RNTI" header line and capture all data rows until the end of the section
        header_found = False
        data_rows = []
        returned_ouput = []
        for line in lines_tb_config:
            if "RNTI" in line:  # This line contains the RNTI header, indicating the start of the data rows
                header_found = True
            elif header_found and line.strip().startswith('|'):  # Data lines start with '|'
                data_rows.append(line.strip())

        for row in data_rows:  # Iterate over each row
            dict_1 = {}
            row_values = row.split('|')  # Split the current row by the '|' character to get individual values
            for entry in self.config['TB Config'][0].items():  # Access the first (and only) item in the list, then iterate over its items
                key, value = entry
                db_field = value['DB Field']
                index = value['index'] + 1
                if index < len(row_values):  # Check if the index is within the bounds of row_values
                    row_value = row_values[index].strip()
                    if row_value:  # Add to dict_1 only if row_value is not empty
                        dict_1[db_field] = row_value
            if dict_1:  # Check if dict_1 is not empty before printing or adding to carrier_ids
                for additional_key in ['__Raw_Data','__collection','__cell', 'Packet_Type','__frequency']:
                    if additional_key in self.config:
                        # Inside simple_map_entry, when processing __cell:
                        if additional_key in ['__cell','Packet_Type','__Raw_Data'] and isinstance(self.config[additional_key], list):
                            code_arr = [line.replace("\\", "") for line in self.config[additional_key]]
                            # evaluate(config[additionalkey], mapped_data)
                            # Pass mapped_data to evaluate, allowing the executed code to access/modify it
                            result = evaluate(code_arr, dict_1)  # Using mapped_data as both input and output
                            # Optionally capture the result and do something with it, like updating mapped_data with new data
                            if result is not None:
                                dict_1.update(result)  # Example of using the result. Adjust as needed.

                            else:
                                # If __cell doesn't meet the criteria, skip execution
                                continue

                        else:
                            dict_1[additional_key] = self.config[additional_key]
                returned_ouput.append(dict_1)
        return returned_ouput