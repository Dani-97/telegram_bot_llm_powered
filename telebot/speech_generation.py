import os
from text_to_speech import save
# import torch
# from TTS.api import TTS

class SpeechGenerationClientFactory():

    def __init__(self):
        pass

    def create_speech_generator(self, speech_generator_type):
        speech_generator_obj = None

        if (speech_generator_type=='Basic'):
            speech_generator_obj = BasicSpeechGenerationClient()
        # elif (speech_generator_type=='Coqui-TTS'):
        #     speech_generator_obj = CoquiSpeechGenerationClient()

        return speech_generator_obj

class BasicSpeechGenerationClient():

    def __init__(self):
        pass

    def get_speech(self, input_text):
        language = "en"
        audio_file_path = "./assets/generated_voice.mp3"

        save(input_text, language, slow=False, file=audio_file_path)

        audio = open(audio_file_path, 'rb')

        return audio

# class CoquiSpeechGenerationClient():

#     def __init__(self):
#         os.environ["COQUI_TOS_AGREED"] = "1"

#     def get_speech(self, input_text):
#         audio_file_path = "./assets/generated_voice.mp3"
#         device = "cuda" if torch.cuda.is_available() else "cpu"

#         tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

#         tts.tts_to_file(
#             text=input_text,
#             speaker="Craig Gutsy",
#             language="en",
#             file_path=audio_file_path
#         )

#         audio = open(audio_file_path, 'rb')

#         return audio