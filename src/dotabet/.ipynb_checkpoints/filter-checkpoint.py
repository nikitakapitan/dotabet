import json
import csv
import dotabet

def read_csv(file_path):
    team_ids = set()
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            team_ids.add(int(row['Team ID']))
    return team_ids

# Function to filter JSON file based on team IDs and write to new JSON file
def filter_json(input_json_paths, team_ids):
    filtered_data = []
    data = dotabet.utils.get_merged_data(input_json_paths)
    for entry in data:
        if entry['dire_team_id'] in team_ids or entry['radiant_team_id'] in team_ids:
            filtered_data.append(entry)
    return filtered_data

def filter_top_teams(input_json_paths, csv_file_path, output_file):
    team_ids = read_csv(csv_file_path)
    filtered_data = filter_json(input_json_paths, team_ids)
    print(f"Total of {len(filtered_data)} pro games")
    
    with open(output_file, 'w') as jsonfile:
        json.dump(filtered_data, jsonfile)

########### FILTER all_player.csv

# import csv

# def is_monotonically_increasing(data_list):
#     return all(x <= y for x, y in zip(data_list, data_list[1:]))

# def filter_and_preprocess(all_player_csv_path):
#     total_rows = 0
#     thresholds = {'gold_t': 1000, 'xp_t': 1000, 'lh_t': 10}
	
#     removal_details = {
#         'gold_t': {'empty': 0, 'high_start': 0, 'non_increasing': 0},
#         'xp_t': {'empty': 0, 'high_start': 0, 'non_increasing': 0},
#         'lh_t': {'empty': 0, 'high_start': 0, 'non_increasing': 0}
#     }
    
#     clean_rows = []
#     fieldnames = []
    
#     with open(all_player_csv_path, 'r', newline='') as csvfile:
#         reader = csv.DictReader(csvfile)
#         fieldnames = reader.fieldnames 
        
#         for row in reader:
								 
#             total_rows += 1
#             corrupted_rows = {column: False for column in ['gold_t', 'xp_t', 'lh_t']}
            
#             for column in corrupted_rows.keys():
#                 if not row[column].strip():  # Check if the column is empty or contains only whitespace
#                     removal_details[column]['empty'] += 1
#                     corrupted_rows[column] = True
#                     continue  

#                 data_list = eval(row[column])
																																						        
#                 if data_list[0] > thresholds[column]:
#                     removal_details[column]['high_start'] += 1
#                     corrupted_rows[column] = True
#                     continue  
					
#                 adjustment = data_list[0]
#                 adjusted_data_list = [value - adjustment for value in data_list]
#                 row[column] = str(adjusted_data_list)  # Update the row with adjusted values
                
                
#                 if not is_monotonically_increasing(data_list):
#                     removal_details[column]['non_increasing'] += 1
#                     corrupted_rows[column] = True
#                     continue  
            
#             if not any(corrupted_rows.values()):  # If the row is not corrupted in any column
				 
#                 clean_rows.append(row)
    
#     # Write the clean data to a new file, preserving all original columns
#     with open(all_player_csv_path.replace('.csv', '_clean.csv'), 'w', newline='') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(clean_rows)
    
#     # Calculate totals and print detailed report
#     print(f"Total rows analyzed: {total_rows}")
#     for column, reasons in removal_details.items():
#         total_removed_for_column = sum(reasons.values())
#         print(f"\n{column} - Total rows removed: {total_removed_for_column}")
#         for reason, count in reasons.items():
#             print(f"\t {reason}: {count} ({count/total_rows*100:.2f}% of total rows)")




    