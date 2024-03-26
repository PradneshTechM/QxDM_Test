from kpi_utils import table_config, map_entry

class Packet_0xB132:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.dict = {}
        self.result = []

    def extract_info(self):
        self.dict.update(self.entry)
        non_table_capture = self.regular_pattern()
        # table_capture = self.table_pattern()
        # table_capture2 = self.table_pattern2()
        if non_table_capture:
            self.dict.update(non_table_capture)
        # if table_capture:
        #     for row in table_capture:
        #         row_dict = self.dict.copy()
        #         row_dict.update(row)
        #         self.result.append(row_dict)
        # if table_capture2:
        #     for row in table_capture2:
        #         row_dict = self.dict.copy()
        #         row_dict.update(row)
        #         self.result.append(row_dict)
        return self.dict

    def regular_pattern(self):
        fields_to_extract = ['Subscription ID', 'Cell Id', 'EARFCN', 'System BW', 'Num HARQ', 'UE Category', 'TX Mode', 'Num eNb Tx Ant']
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
        tb_info_start_index = self.packet_text.find('TB Info Record[0]')
        if tb_info_start_index != -1:
            tb_info_end_index = self.packet_text.find('TB Config', tb_info_start_index)
            if tb_info_end_index != -1:
                table_text = self.packet_text[tb_info_start_index:tb_info_end_index]
                rows = table_text.split('\n')[4:-1]  # Skip header and footer
                if rows:
                    table_data = []
                    for row in rows:
                        row_data = row.split('|')
                        if len(row_data) >= 7:
                            table_data.append({
                                'Enable': row_data[1].strip(),
                                'TB Top': row_data[2].strip(),
                                # Add more fields as needed
                            })
                    return table_data
        return None

    def table_pattern2(self):
        tb_config_start_index = self.packet_text.find('TB Config')
        if tb_config_start_index != -1:
            tb_config_end_index = self.packet_text.find('TB Log Extend', tb_config_start_index)
            if tb_config_end_index != -1:
                table_text = self.packet_text[tb_config_start_index:tb_config_end_index]
                rows = table_text.split('\n')[4:-1]  # Skip header and footer
                if rows:
                    table_data = []
                    for row in rows:
                        row_data = row.split('|')
                        if len(row_data) >= 7:
                            table_data.append({
                                'Value': row_data[1].strip(),
                                'Rate': row_data[2].strip(),
                                # Add more fields as needed
                            })
                    return table_data
        return None