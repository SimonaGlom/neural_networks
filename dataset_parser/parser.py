import os
import re
import csv

import urllib.request
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
import _pickle as cPickle
import urllib.parse
import importlib


class datasetParser(object):
    # set up columns to save
    # name: index in dataset
    rx_dict = {
        'format': 2,
        'record_url': 3,
        'info_url': 4
    }

    @staticmethod
    def __parse_line(line):
        """
        Save all defined columns and search name of spieces
        return info about spieces

        :param line: raw line from dataset
        :return: sample consists from specified columns
        """
        sample = {}

        # get required data
        for key, rx in datasetParser.rx_dict.items():
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
                sample = datasetParser().__parse_line(row)

                # if sample is well formatted
                if sample is not None:
                    data.append(sample)

        return data

    @staticmethod
    def __get_extended_information(latin_name):
        """
        Load additional information for spieces from online sources and parse it

        :param latin_name: name of spieces in latin
        :return: name, spieces for specified latin name
        """

        link = 'https://www.google.sk/search?q=' + latin_name.replace('_', '%20')

        # load driver to render page
        driver = webdriver.PhantomJS()
        driver.get(link)

        name = ''
        spieces = ''
        page_source = ''

        # templates
        page_templates = [
            ['//*[@id="main"]/div[4]/div/div[1]/span[1]/div', '//*[@id="main"]/div[4]/div/div[1]/span[2]/div'],
            ['//*[@id="main"]/div[3]/div/div[1]/span/div', '//*[@id="main"]/div[4]/div/div[1]/span[2]/div'],
            ['//*[@id="main"]/div[5]/div/div[1]/span[1]/div', '//*[@id="main"]/div[5]/div/div[1]/span[2]/div']
        ]

        for page_template in page_templates:
            # Get elements by their xpath
            try:
                name = driver.find_element(By.XPATH, page_template[0]).text
                spieces = driver.find_element(By.XPATH, page_template[1]).text
            except:
                logging.info("nenašlo sa")

            if name != '':
                break

        # for parser improvement only
        if name == '':
            page_source = driver.page_source

        return name, spieces

    @staticmethod
    def get_aggregated(parsed_dataset, minimum_samples=None, download_extended_information=False):
        """

        :param parsed_dataset: parsed dataset
        :param minimum_samples: condition of minimum spieces occurrence in dataset
        :param download_extended_information: load more information about animals from online encyclopedic pages
        :return: aggregated samples
        """
        aggregated = {}
        sum_index = 'sum'


        # aggregate dataset (sum samples count for every spieces)
        for d in parsed_dataset:
            # new spieces
            if (d['name'] is not None) and (d['name'] not in aggregated):
                aggregated[d['name']] = {}
                aggregated[d['name']].update({sum_index: 1})

                for key, rx in datasetParser.rx_dict.items():
                    aggregated[d['name']].update({key: [d[key]]})
            # existing spieces, only append to arrays
            elif d['name'] is not None:
                aggregated[d['name']][sum_index] += 1

                for key, rx in datasetParser.rx_dict.items():
                    aggregated[d['name']].get(key).append(d[key])

        logging.info(str(len(aggregated)) + ' animal spieces found!')

        # remove animals, which has not enough samples in dataset
        if minimum_samples is not None:
            for key in list(aggregated):
                if aggregated[key].get(sum_index) < minimum_samples:
                    del aggregated[key]

            logging.info(str(len(aggregated)) + ' animal spieces found, which have more than ' + minimum_samples + ' sound samples!')


        if download_extended_information:
            for key in list(aggregated):
                print(key)

                translated_name, translated_spieces = datasetParser().__get_extended_information(key)
                aggregated[key]['name'] = translated_name
                aggregated[key]['spieces'] = translated_spieces

        return aggregated

    @staticmethod
    def serialize_dataset_to_file(dataset, dataset_save_path):
        cPickle.dump(dataset, open(dataset_save_path, 'wb'))

    @staticmethod
    def load_dataset_from_file(dataset_save_path):
        dataset = cPickle.load(open(dataset_save_path, 'rb'))

        return dataset

    @staticmethod
    def download_records(aggregated_dataset, records_directory, dataset_save_path):
        """
        :param aggregated_dataset: parsed and aggregated dataset
        :param records_directory: path to records directory
        """

        filepath_key = 'filepath'
        logging.info('Downloading ...')

        # create folder for records
        if not os.path.exists(records_directory):
            os.makedirs(records_directory)


        order = 0
        for key in aggregated_dataset:
            i = 0

            actual_spieces_folder = records_directory + '/' + key

            if not filepath_key in aggregated_dataset[key]:
                aggregated_dataset[key][filepath_key] = dict()

            # create folder for spieces
            if not os.path.exists(actual_spieces_folder):
                os.makedirs(actual_spieces_folder)

            logging.info('Spieces(' + str(order) + '/' + str(len(aggregated_dataset)) + '): ' + actual_spieces_folder)

            # download all records for animal
            for record in aggregated_dataset[key]['record_url']:

                # if donwloaded already continue
                if record in aggregated_dataset[key][filepath_key] and os.path.exists(aggregated_dataset[key][filepath_key][record]):
                    continue

                file_name = (key.lower()+str(i)+'.mp3')
                full_file_name = os.path.join(actual_spieces_folder, file_name).encode('utf8')

                urllib.request.urlretrieve(record, full_file_name)

                # save actual file path to saved dataset file (for preventing duplicate downloading later)
                aggregated_dataset[key][filepath_key][record] = full_file_name
                i += 1

            order += 1

            # save paths
            datasetParser.serialize_dataset_to_file(aggregated_dataset, dataset_save_path)
