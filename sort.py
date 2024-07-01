import json

def read_and_sort_json(file_path):
    # Load the JSON data from the given file path
    with open(file_path, 'r') as file:
        conferences = json.load(file)
    
    # Create a sorted list of tuples from the dictionary items
    # We sort by the length of the full conference name, in descending order
    sorted_conferences = sorted(conferences.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Convert the sorted list of tuples back to a dictionary
    sorted_dict = {abbr: full_name for abbr, full_name in sorted_conferences}
    sorted_dict = {k : [v] for k, v in sorted_dict.items()}
    sorted_dict.update({k+"_short" : [k] for k in sorted_dict})

    return sorted_dict

def save_sorted_json(sorted_conferences, output_file_path):
    # Save the sorted dictionary to a new JSON file
    with open(output_file_path, 'w') as file:
        json.dump(sorted_conferences, file, indent=4)

# Specify the paths for the input and output JSON files
input_json_path = 'conferences.json'
output_json_path = 'sorted_abbreviations.json'

# Read, sort, and save the JSON data
sorted_conferences = read_and_sort_json(input_json_path)
save_sorted_json(sorted_conferences, output_json_path)

print(f"Sorted conference names have been saved to {output_json_path}")
