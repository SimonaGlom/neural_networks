from pydub import AudioSegment
import librosa
import numpy

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    """
    Iterate over chunks until you find the first one with sound

    :param sound: pydub.AudioSegment
    :param silence_threshold: in dB
    :param chunk_size: in ms
    :return: start time of first sound
    """
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[trim_ms:trim_ms + chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

def from_mp3_to_wav(audio_path):
    """
       Implement convertor from mp3 to wav

       :param audio_path: path to audio
       """
    sound = AudioSegment.from_mp3(audio_path)
    sound.export(audio_path.replace('.mp3', '.wav'), format="wav")

def mfcc_spectogram(file_name):
    """
           Implement extract features from wav file to mfcc spectogram features

           :param audio_path: path to audio
           :return: Mfcc spectogram in numerical array
    """
    try:
        audio, sample_rate = librosa.load(file_name, res_type='kaiser_fast')
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        mfccsscaled = numpy.mean(mfccs.T, axis=0)
        print(sample_rate, mfccs)

    except Exception as e:
        print("Error encountered while parsing file: ", file_name)
        return None

    return mfccsscaled


# TODO doimplementovať
"""
sound = AudioSegment.from_file("/path/to/file.wav", format="wav")

start_trim = detect_leading_silence(sound)
end_trim = detect_leading_silence(sound.reverse())

duration = len(sound)
trimmed_sound = sound[start_trim:duration - end_trim]
"""