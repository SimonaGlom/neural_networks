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
        self.record_path_key = 'filepath'
        self.records_folder = 'dataset_parser/records'


    def __load(self):
        return cPickle.load(open(self.path, 'rb'))

    def get_animals(self, min_samples=0, only_with_spieces_name=False):
        animals = []

        for key_spieces in self.raw_dataset:
            raw_animal = self.raw_dataset[key_spieces]
            spectograms = []

            if self.record_path_key in self.raw_dataset[key_spieces]:
                for record in self.raw_dataset[key_spieces][self.record_path_key]:
                    record_path = self.raw_dataset[key_spieces][self.record_path_key][record].decode("utf-8")
                    record = Record(record_path, key_spieces)
                    spectograms += record.get_spectograms()

            animal = Animal(key_spieces, raw_animal['name'], raw_animal['spieces'], spectograms)

            if animal.get_spectograms_count() > min_samples and (not only_with_spieces_name or animal.has_assigned_spieces()):
                animals.append(animal)

        return animals

    def split_records(self, delete=False):

        for key_spieces in self.raw_dataset:
            spieces_records_folder = os.path.join(self.records_folder, key_spieces)

            logging.info("Splitting: " + key_spieces)

            # If delete true remove all split parts for records
            if delete:
                for o in os.listdir(spieces_records_folder):
                    record_folder = os.path.join(spieces_records_folder, o)

                    if os.path.isdir(record_folder):
                        shutil.rmtree(record_folder)

            for record in self.raw_dataset[key_spieces][self.record_path_key]:
                record_path = self.raw_dataset[key_spieces][self.record_path_key][record].decode("utf-8")

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


class Animal:
    def __init__(self, name, animal_name_sk, spieces_name, spectograms):
        self.name = name
        self.animal_name_sk = animal_name_sk
        self.spieces_name = spieces_name
        self.spectograms = spectograms

    def get_spectograms_count(self):
        return len(self.spectograms)

    def get_spectograms(self, max_spectograms=False):
        if not max:
            return self.spectograms

        return self.spectograms[:max_spectograms]

    def get_name(self):
        return self.name

    def get_name_sk(self):
        return self.animal_name_sk

    def has_assigned_spieces(self):
        return not self.get_spieces()

    def get_spieces(self):
        return self.spieces_name


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

    def split_parts(self, folder, part_duration=3000):
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

    animals = dataset.get_animals(min_samples=0, only_with_spieces_name=False)
    print(len(animals))
