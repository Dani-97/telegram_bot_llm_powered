from pydub import AudioSegment
import speech_recognition as sr

class TranscriptionGenerationClient():

    def __init__(self):
        pass

    def convert_audio_file_to_wav(self, audio_filepath):
        audio_segment_obj = AudioSegment.from_file(audio_filepath)
        audio_segment_obj.export(audio_filepath.replace('.ogg', '.wav'), format='wav')

    def get_transcription(self, audio_filename_to_transcribe):
        recognizer = sr.Recognizer()

        with sr.AudioFile(audio_filename_to_transcribe) as source:
            # listen for the data (load audio to memory)
            audio_data = recognizer.record(source)
            # recognize (convert from speech to text)
            transcribed_text = recognizer.recognize_google(audio_data)
        
        return transcribed_text