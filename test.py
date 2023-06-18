import csv

data = ["John", "Doe", 25]


file_path = "output_file.txt"  # Specify the file path

with open(file_path, "w", newline="") as file:
    writer = csv.writer(file, delimiter="\t")  # Set the delimiter to tab
    writer.writerows([data])