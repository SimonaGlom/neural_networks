import _pickle as cPickle
import src.models.spectrogram as spectogram
import src.models.preprocessor as preprocessor
import logging
import shutil
import glob, os


class Dataset:
    def __init__(self, path):
        self.path = path

        # Load dataset on initialization
        self.raw_dataset = self.__load()

    def __load(self):
        return cPickle.load(open(self.path, 'rb'))

    def split_records(self, delete=False):
        record_path_key = 'filepath'
        records_folder = 'dataset_parser/records'

        for key_spieces in self.raw_dataset:
            spieces_records_folder = os.path.join(records_folder, key_spieces)

            logging.info("Splitting: " + key_spieces)

            # If delete true remove all split parts for records
            if delete:
                for o in os.listdir(spieces_records_folder):
                    record_folder = os.path.join(spieces_records_folder, o)

                    if os.path.isdir(record_folder):
                        shutil.rmtree(record_folder)

            for record in self.raw_dataset[key_spieces][record_path_key]:
                record_path = self.raw_dataset[key_spieces][record_path_key][record].decode("utf-8")

                record = Record(record_path, key_spieces)
                logging.info("Splitting: " + record.get_record_name_without_format())

                record_folder = os.path.join(spieces_records_folder, record.get_record_name_without_format())

                if not record.get_parts() or delete:
                    try:
                        os.mkdir(record_folder)
                    except OSError:
                        print("Creation of the directory %s failed" % record_folder)
                    else:
                        print("Successfully created the directory %s " % record_folder)

                    record.split_parts(record_folder)

                if not record.get_spectograms() or delete:
                    record.create_spectograms()

class Record:
    def __init__(self, record_path, spieces_name):
        self.object = record_path

        self.spieces = spieces_name
        self.name = record_path.rsplit('/', 1)[1]
        self.filepath = record_path
        self.parts_folder = self.filepath[:-4]

        self.parts = []
        self.spectograms = []

        self.__load_parts()

    def __load_parts(self):
        self.parts = []
        self.spectograms = []

        if not os.path.exists(self.parts_folder):
            return

        for file in os.listdir(self.parts_folder):
            if file.endswith(".wav"):
                self.parts.append(os.path.join(self.parts_folder, file))

            if file.endswith(".png"):
                self.spectograms.append(os.path.join(self.parts_folder, file))

    def get_record_name(self):
        return self.name

    def get_record_name_without_format(self):
        return self.name[:-4]

    def get_spieces_name(self):
        return self.spieces

    def get_parts(self):
        return self.parts

    def get_filepath(self):
        return self.filepath

    def get_spectograms(self):
        return self.spectograms

    def split_parts(self, folder, part_duration = 3000):
        self.parts = []

        self.parts = preprocessor.split_records(self.get_filepath(), folder, part_duration)

    def create_spectograms(self):
        for part in self.parts:
            plot_path = part[:-4]+'.png'
            print(plot_path)
            self.spectograms.append(spectogram.plot_audio_spectrogram(part, plot_path=plot_path, argv='s'))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    dataset_path = 'dataset_parser/dataset_info.save'
    dataset = Dataset(dataset_path)

    dataset.split_records(True)
