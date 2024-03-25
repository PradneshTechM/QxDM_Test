import pandas as pd
import json

def generate_json_from_excel(excel_file_path, comments_file_path, json_file_path):
    # Load the Excel file
    df = pd.read_excel(excel_file_path)
    df_comments = pd.read_excel(comments_file_path)

    # Initialize an empty dictionary to hold the JSON structure
    json_output = {}

    # Group the DataFrame by 'Log Packet' to process each packet separately
    for (packet_name, collection, cell), group in df.groupby(['Packet Name', '__collection', '__cell']):
        packet_dict = {}

        # Process each row in the group
        for _, row in group.iterrows():
            print(row)

            if pd.notna(row['Table Name']):
                table_name = row['Table Name']
                if table_name not in packet_dict:
                    packet_dict[table_name] = [{}]  # Initialize with an empty dictionary in a list

                # Add or update the nested fields within the dictionary
                if pd.notna(row['DB Field']):
                    if pd.notna(row['Field Name']):
                        packet_dict[table_name][0][row['QxDM Field']] = {
                            "index": int(row['Index']),
                            "DB Field": row['DB Field'],
                            "Field Name": row['Field Name']
                        }
                    else:
                        packet_dict[table_name][0][row['QxDM Field']] = {
                            "index": int(row['Index']),
                            "DB Field": row['DB Field'],
                        }
                else:
                    if pd.notna(row['Field Name']):
                        packet_dict[table_name][0][row['QxDM Field']] = {
                            "index": int(row['Index']),
                            "DB Field": row['QxDM Field'],
                            "Field Name": row['Field Name']
                        }
                    else:
                        packet_dict[table_name][0][row['QxDM Field']] = {
                            "index": int(row['Index']),
                            "DB Field": row['QxDM Field']
                        }
            else:
                if pd.notna(row['DB Field']):
                    if pd.notna(row['Field Name']):
                        packet_dict[row['QxDM Field']] = {"DB Field": row['DB Field'], "Field Name": row['Field Name']}
                    else:
                        packet_dict[row['QxDM Field']] = {"DB Field": row['DB Field']}
                else:
                    if pd.notna(row['Field Name']):
                        packet_dict[row['QxDM Field']] = {"DB Field": row['QxDM Field'], "Field Name": row['Field Name']}
                    else:
                        packet_dict[row['QxDM Field']] = {"DB Field": row['QxDM Field']}

        # Add special fields after processing all rows in the group
        special_fields = {
            "Raw_Data": group['Raw_PD'].iloc[0],
            "__collection": group['__collection'].iloc[0],
            "__cell": group['__cell'].iloc[0],
            "Packet_Type": group['Packet_Type'].iloc[0],
            "__frequency": group['Frequency'].iloc[0]
        }
        for key, value in special_fields.items():
            if key == 'Raw_Data':
                if pd.isna(value) or value == 'No':
                    packet_dict['__Raw_Data'] = False
                elif value == 'Yes':
                    packet_dict['__Raw_Data'] = True
            elif pd.notna(value):
                packet_dict[key] = value
        print(packet_dict)

        # Handle comments if any matches the current packet
        comments_group = df_comments[df_comments['Packet Name'] == packet_name]
        for _, comments_row in comments_group.iterrows():
            list_convertor = comments_row['Dynamic Comment'].split(',')
            packet_dict[comments_row['Field']] = list_convertor
        json_output[packet_name] = packet_dict

    # Write the JSON output to a file
    with open(json_file_path, 'w') as file:
        json.dump(json_output, file, indent=4)


### change the paths where you have stored the files
excel_file_path = 'C:/Users/PS001015449/output.xlsx'
comments_file_path = 'C:/Users/PS001015449/comments.xlsx'
json_file_path = 'C:/Users/PS001015449/PycharmProjects/Helloworld/packet_data.json'

generate_json_from_excel(excel_file_path,comments_file_path, json_file_path)