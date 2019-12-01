import csv
import logging
root_path = 'src/experiments/e3/'

with open('src/data/AnimalSound.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    writer = csv.writer(open(root_path + 'data/e.csv', 'w'))

    logging.info('Dataset loading ...')
    line_count = 0
    for row in csv_reader:
        line_count += 1
        class_name = row[3]
        if class_name is not '':
            with open(root_path + 'data/e.csv', 'w', newline='') as file:
                writer.writerow([row[0], row[1], class_name])