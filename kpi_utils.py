from evaluate import evaluate
def simple_map_entry(data, config):
    mapped_data = {}
    data_values = list(data.values())  # Get the values from the data extracted by regex
    # Loop to process and map each data value based on the config
    for i, (config_key, config_value) in enumerate(config.items(), start=0):

        if i < len(data_values):
            mapped_value = data_values[i]  # Use original value, adjusted for index starting at 0

            # Process the value based on 'Field Type' specified in config
            if 'Field Type' in config_value:
                if config_value['Field Type'] == 'Positive Number':
                    mapped_value = int(mapped_value)
                elif config_value['Field Type'] == 'Decimal':
                    mapped_value = float(mapped_value)
                elif config_value['Field Type'] == 'String':
                    mapped_value = str(mapped_value)

            # Check for __comments and evaluate if present
            # if '__comments' in config_value:
            #     code_arr = [config_value['__comments'].replace("\\", "")]
            #     result = self.evaluate(code_arr, {'_obj': data}, data)
            #     # Handle result, e.g., add to mapped_data if result is not None
            #     if result is not None:
            #         mapped_data[some_key] = result

            new_key = config_value.get('DB Field', config_key)  # Get the new key name
            mapped_data[new_key] = mapped_value  # Assign the processed value to the new key

    # After the loop, add additional keys to ensure they appear at the end
    for additional_key in ['__collection', '__cell', '__Raw_Data', '__KPI_type', '__frequency']:
        if additional_key in config:
            # Inside simple_map_entry, when processing __cell:
            if additional_key == '__cell' and isinstance(config[additional_key], list):
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