from decimal import Decimal

def map_entry(entry, config, key_mapping = None ):
    mapped_entry = {}
    key_mapping = key_mapping
    for key, value in entry.items():
        if key_mapping:
            key = key_mapping.get(key,key)

        db_config = config.get(key, {})
        db_field = db_config.get('DB Field')
        field_type = db_config.get('Field Type')
        # print(field_type)
        if field_type:
            if field_type == 'Positive Number':
                mapped_value = int(value)
            # print(mapped_value)
            elif field_type == 'Text':
                mapped_value = str(value)
            elif field_type == 'decimal':
                mapped_value = Decimal(value)
        else:
            mapped_value = value

        if db_field:
            mapped_entry[db_field] = mapped_value
        else:
            mapped_entry[key] = mapped_value

    for additional_key in ['__collection', '__cell', '__Raw_Data', '__KPI_type', '__frequency']:
        if additional_key in config:
            mapped_entry[additional_key] = config[additional_key]

    # mapped_entry['__collection'] = config.get('__collection')
    # mapped_entry['__cell'] = config.get('__cell')
    # mapped_entry['__Raw_Data'] = config.get('__Raw_Data')
    # mapped_entry['__KPI_type'] = config.get('__KPI_type')

    return mapped_entry



def metadata(mapped_entry:dict, config):
    mapped_entry["__collection"] = config.get('__collection')
    mapped_entry["__frequency"] = config.get('__frequency')
    mapped_entry["__cell"] = config.get('__cell')
    mapped_entry["__packet_type"] = config.get('__packet_message')
    mapped_entry["__Raw_Data"] = config.get('__Raw_Data')
    mapped_entry["__KPI_type"] = config.get('__KPI_type')
    filtered_entry = {key: value for key, value in mapped_entry.items() if value is not None}

    return filtered_entry