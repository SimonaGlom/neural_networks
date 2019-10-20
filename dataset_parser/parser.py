import os
import re
import csv

import urllib.request
import logging


class datasetParser(object):
    @staticmethod
    def _parse_line(line):
        """
        Save all defined columns and search name of spieces
        return info about spieces

        :param line: raw line from dataset
        :return: sample consists from specified columns
        """
        sample = {}

        # get required data
        for key, rx in rx_dict.items():
            sample.update({key: line[rx]})

        # search name of spieces with regular expression
        sample['name'] = re.search('unique_id\=(TSA\:|FRA\:|)(.+?_.+?)_.*?&auto.*$', sample['info_url'])

        if sample['name'] is not None:
            sample['name'] = sample['name'].groups()[1]
        else:
            # if None it is bad formatted line -> throw away
            return None

        # if there are no matches
        return sample

    @staticmethod
    def parse_dataset(file_path):
        """
        Parse text at given filepath

        :param file_path: for file_object to be parsed
        :return data: parsed data
        """

        data = []  # create an empty list to collect the data
        # open the file and read through it line by line
        csv.register_dialect('escaped', escapechar='\\', doublequote=False, quoting=csv.QUOTE_NONE)

        # open dataset file
        with open(file_path, 'r') as file_object:
            reader = csv.reader(file_object, delimiter='\t')

            # proceed every row in file
            for i, row in enumerate(reader):
                if i == 0:
                    continue

                # parse one line
                sample = datasetParser()._parse_line(row)

                # if sample is well formatted
                if sample is not None:
                    data.append(sample)

        return data

    @staticmethod
    def get_aggregated(simplified_dataset, minimum_samples=None):
        """

        :param simplified_dataset: parsed dataset
        :param minimum_samples: condition of minimum spieces occurrence in dataset
        :return: aggregated samples
        """
        aggregated = {}
        sum_index = 'sum'


        # aggregate dataset (sum samples count for every spieces)
        for d in simplified_dataset:
            # new spieces
            if (d['name'] is not None) and (d['name'] not in aggregated):
                aggregated[d['name']] = {}
                aggregated[d['name']].update({sum_index: 1})

                for key, rx in rx_dict.items():
                    aggregated[d['name']].update({key: [d[key]]})
            # existing spieces, only append to arrays
            elif d['name'] is not None:
                aggregated[d['name']][sum_index] += 1

                for key, rx in rx_dict.items():
                    aggregated[d['name']].get(key).append(d[key])

        logging.info(str(len(aggregated)) + ' animal spieces found!')

        # remove animals, which has not enough samples in dataset
        if minimum_samples is not None:
            for key in list(aggregated):
                if aggregated[key].get(sum_index) < minimum_samples:
                    del aggregated[key]

            logging.info(str(len(aggregated)) + ' animal spieces found, which have more than ' + minimum_samples + ' sound samples!')

        return aggregated

    @staticmethod
    def download_records(aggregated_dataset):
        """
        :param aggregated_dataset:
        """
        directory = './records'

        # create folder for records
        if not os.path.exists(directory):
            os.makedirs(directory)

        for key in aggregated_dataset:
            i = 0

            # download all records for animal
            for record in aggregated_dataset[key]['record_url']:
                file_name = key.lower()+str(i)+'.mp3'
                full_file_name = os.path.join(directory, file_name).encode('utf8')

                urllib.request.urlretrieve(str(record).encode('utf8'), full_file_name)

                logging.info(file_name)
                i += 1


if __name__ == '__main__':
    file_path = 'multimedia.txt'
    logging.basicConfig(level=logging.DEBUG)

    # set up columns to save
    # name: index in dataset
    rx_dict = {
        'format': 2,
        'record_url': 3,
        'info_url': 4
    }

    parser = datasetParser()

    # parsed dataset
    data = parser.parse_dataset(file_path)

    # aggregated dataset
    aggregated_data = parser.get_aggregated(data)

    # download records
    # parser.download_records(aggregated_data)


