from pydub import AudioSegment


def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    """
    Iterate over chunks until you find the first one with sound

    :param sound: pydub.AudioSegment
    :param silence_threshold: in dB
    :param chunk_size: in ms
    :return: start time of first sound
    """
    trim_ms = 0 # ms

    assert chunk_size > 0 # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

# TODO doimplementovať
sound = AudioSegment.from_file("/path/to/file.wav", format="wav")

start_trim = detect_leading_silence(sound)
end_trim = detect_leading_silence(sound.reverse())

duration = len(sound)
trimmed_sound = sound[start_trim:duration-end_trim]