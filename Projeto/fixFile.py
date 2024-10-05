import csv
import math

def create_csv_from_text_file():
    for i in range(0, 2):
        input_file_path = f"docs/sensor{i+1}.txt"
        output_file_path = f"docs/data{i+1}.csv"
        with open(input_file_path, 'r') as input_file, open(output_file_path, 'w', newline='') as output_file:
            reader = csv.reader(input_file, delimiter=';')
            writer = csv.writer(output_file, delimiter=';')
            
            # Write the header row
            writer.writerow(['MAC Address', 'Signal Strength', 'Distance', "Timestamp"])
            
            # Write the rest of the rows with calculated Distance
            for row in reader:
                col1 = row[0]
                col2 = row[1]
                col4 = row[2]
                distance = pow(10.0, ((-63.0 - float(col2)) / (10.0 * 2.0))) # +-
                #distance = math.pow(10.0, (-63.55 - (20.0 * math.log10(2412)) + math.fabs(float(col2))) / 20.0)
                #distance = pow(10, (float(-53.0 - float(col2) - 10.0)) / (10 * 2))
                #distance = round(distance, 6)
                writer.writerow([col1, col2, distance, col4])

create_csv_from_text_file()