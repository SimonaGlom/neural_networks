import logging
from os import path

from dataset_parser.parser import datasetParser

if __name__ == '__main__':
    parser = datasetParser()

    file_path = 'dataset_parser/multimedia.txt'
    logging.basicConfig(level=logging.INFO)

    multimedia_path = 'dataset_parser/multimedia.txt'
    dataset_save_path = 'dataset_parser/dataset_info.save'

    # parse dataset if not parsed yet
    if not path.exists(multimedia_path):
        # parsed dataset
        data = parser.parse_dataset(file_path)

        # aggregated dataset
        aggregated_data = parser.get_aggregated(parsed_dataset=data, download_extended_information=True)
        parser.serialize_dataset_to_file(aggregated_data)

    # load dataset from file
    dataset_info = parser.load_dataset_from_file(dataset_save_path)
    logging.info('Dataset loaded ;)')

    # download records
    records_path = 'dataset_parser/records'
    parser.download_records(dataset_info, records_path, dataset_save_path)
