from decimal import Decimal
from parser.evaluate import evaluate
# def map_entry(entry, config, key_mapping = None ):
#     mapped_entry = {}
#     key_mapping = key_mapping
#     for key, value in entry.items():
#         if key_mapping:
#             key = key_mapping.get(key,key)
#
#         db_config = config.get(key, {})
#         db_field = db_config.get('DB Field')
#         field_type = db_config.get('Field Type')
#         # print(field_type)
#         if field_type:
#             if field_type == 'Positive Number':
#                 mapped_value = int(value)
#             # print(mapped_value)
#             elif field_type == 'Text':
#                 mapped_value = str(value)
#             elif field_type == 'decimal':
#                 mapped_value = Decimal(value)
#         else:
#             mapped_value = value
#
#         if db_field:
#             mapped_entry[db_field] = mapped_value
#         else:
#             mapped_entry[key] = mapped_value
#
#     for additional_key in ['__collection', '__cell', '__Raw_Data', '__KPI_type', '__frequency']:
#         if additional_key in config:
#             mapped_entry[additional_key] = config[additional_key]
#
#     # mapped_entry['__collection'] = config.get('__collection')
#     # mapped_entry['__cell'] = config.get('__cell')
#     # mapped_entry['__Raw_Data'] = config.get('__Raw_Data')
#     # mapped_entry['__KPI_type'] = config.get('__KPI_type')
#
#     return mapped_entry


# Assuming simple_map_entry is defined as below
def simple_map_entry(data, config):
    mapped_data = {}
    data_values = list(data.values())  # Get the values from the data extracted by regex
    # Loop to process and map each data value based on the config
    for i, (config_key, config_value) in enumerate(config.items(), start=0):

        if i < len(data_values):
            if not data_values[i]:
                continue
            mapped_value = data_values[i]  # Use original value, adjusted for index starting at 0

            # Process the value based on 'Field Type' specified in config
            if 'Field Type' in config_value:
                if config_value['Field Type'] == 'Positive Number':
                    mapped_value = int(mapped_value)
                elif config_value['Field Type'] == 'Decimal':
                    mapped_value = float(mapped_value)
                elif config_value['Field Type'] == 'String':
                    mapped_value = str(mapped_value)
            # # Check for __comments and evaluate if present
            # if '__comments' in config_value and isinstance(config_value['__comments'], list):
            #     new_key = config_value.get('DB Field', config_key)  # Get the new key name
            #     mapped_data[new_key] = mapped_value  # Assign the processed value to the new key
            #     code_arr = [line.replace("\\", "") for line in config_value['__comments']]
            #     result = evaluate(code_arr, mapped_data)
            #     if result is not None:
            #         mapped_data.update(result)
            new_key = config_value.get('DB Field', config_key)  # Get the new key name
            mapped_data[new_key] = mapped_value  # Assign the processed value to the new key
            # Check for __comments and evaluate if present
            if '__comments' in config_value and isinstance(config_value['__comments'], list):
                new_key = config_value.get('DB Field', config_key)  # Get the new key name
                mapped_data[new_key] = mapped_value  # Assign the processed value to the new key
                code_arr = [line.replace("\\", "") for line in config_value['__comments']]
                result = evaluate(code_arr, mapped_data)
                if result is not None:
                    mapped_data.update(result)


    # After the loop, add additional keys to ensure they appear at the end
    for additional_key in ['__Raw_Data','__KPI_type','__collection','__cell', 'Packet_Type','__frequency']:
        if additional_key in config:
            # Inside simple_map_entry, when processing __cell:
            if additional_key in ['__cell', 'Packet_Type'] and isinstance(config[additional_key], list):
                code_arr = [line.replace("\\", "") for line in config[additional_key]]
                #evaluate(config[additionalkey], mapped_data)
                # Pass mapped_data to evaluate, allowing the executed code to access/modify it
                result = evaluate(code_arr, mapped_data)  # Using mapped_data as both input and output
                # Optionally capture the result and do something with it, like updating mapped_data with new data
                if result is not None:
                    mapped_data.update(result)  # Example of using the result. Adjust as needed.

                else:
                    # If __cell doesn't meet the criteria, skip execution
                    continue

            else:
                mapped_data[additional_key] = config[additional_key]

    return mapped_data

def map_entry(data, config):
    mapped_data = {}
    data_values = list(data.values())  # Get the values from the data extracted by regex

    for i, (config_key, config_value) in enumerate(config.items(), start=0):
        if i < len(data_values):
            mapped_value = data_values[i]  # use original value
            # Check if 'Field Type' is specified and process the value accordingly
            if 'Field Type' in config_value:
                if config_value['Field Type'] == 'Positive Number':
                    mapped_value = int(mapped_value)
                elif config_value['Field Type'] == 'Decimal':
                    mapped_value = Decimal(mapped_value)
                elif config_value['Field Type'] == 'String':  # Explicitly converting to string, if necessary
                    mapped_value = str(mapped_value)

            new_key = config_value.get('DB Field', config_key)  # Get the new key name
            mapped_data[new_key] = mapped_value  # Assign the processed value to the new key

    return mapped_data


def table_config(data, config_table, config):
        list_dict = []
        # return table_extract(match, self.config, self.config['Records'])
        # Extract the 'table' named group which contains the data rows
        table_content = data.group('table').strip()

        # Split the captured content into rows based on newline characters
        rows = table_content.split('\n')
        for row in rows:  # Iterate over each row
            dict_1 = {}
            row_values = row.split('|')  # Split the current row by the '|' character to get individual values
            config_values = config_table
            for entry in config_values[0].items():  # Access the first (and only) item in the list, then iterate over its items
                key, value = entry
                db_field = value['DB Field']
                index = value['index'] + 1
                if not index:
                    continue
                if index < len(row_values):  # Check if the index is within the bounds of row_values
                    row_value = row_values[index].strip()
                    if row_value:  # Add to dict_1 only if row_value is not empty
                        dict_1[db_field] = row_value
            if dict_1:  # Check if dict_1 is not empty before printing or adding to carrier_ids
                for additional_key in ['__Raw_Data','__collection','__cell', 'Packet_Type','__frequency']:
                    if additional_key in config:
                        # Inside simple_map_entry, when processing __cell:
                        if additional_key in ['__cell','Packet_Type','__Raw_Data'] and isinstance(config[additional_key], list):
                            code_arr = [line.replace("\\", "") for line in config[additional_key]]
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
                            dict_1[additional_key] = config[additional_key]
                list_dict.append(dict_1)
        return list_dict