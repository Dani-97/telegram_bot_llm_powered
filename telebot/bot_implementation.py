import configparser
import re
import telebot
from text_generation import ChatBotFactoryClient
from transcription_generation import TranscriptionGenerationClient
from speech_generation import SpeechGenerationClientFactory

class BaseTeleBotClient():

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.cfg')

        self.__API_TOKEN__ = config['BOT']['API_TOKEN']
        self.__CHATBOT_MODEL__ = config['BOT']['CHATBOT_MODEL']
        self.__VISION_LANGUAGE_CHATBOT_MODEL__ = config['BOT']['VISION_LANGUAGE_CHATBOT_MODEL']
        self.__SPEECH_GENERATOR_MODEL__ = config['BOT']['SPEECH_GENERATOR_MODEL']
        
        self.__OLLAMA_SERVER_URL__ = config['BOT']['OLLAMA_SERVER_URL']
        self.__OLLAMA_PORT_NUMBER__ = config['BOT']['OLLAMA_PORT_NUMBER']

    def build(self):
        self.chatbot_client_factory_obj = ChatBotFactoryClient()
        self.speech_generation_client_factory_obj = SpeechGenerationClientFactory()

        self.vision_language_chatbot_client = \
            self.chatbot_client_factory_obj.create_chatbot(self.__VISION_LANGUAGE_CHATBOT_MODEL__, \
                                                           self.__OLLAMA_SERVER_URL__, \
                                                           self.__OLLAMA_PORT_NUMBER__)

        self.telegram_bot = telebot.TeleBot(self.__API_TOKEN__)
        self.chatbot_client = self.chatbot_client_factory_obj.create_chatbot(self.__CHATBOT_MODEL__, \
                                                                             self.__OLLAMA_SERVER_URL__, \
                                                                             self.__OLLAMA_PORT_NUMBER__)
        self.transcription_client = TranscriptionGenerationClient()        
        self.speech_generation_client = self.speech_generation_client_factory_obj.create_speech_generator(self.__SPEECH_GENERATOR_MODEL__)

    def __send_error_message__(self, chat_id, error_message):
        message_to_send = 'An internal error has occured. The description of the error is the following: '
        message_to_send += error_message

        self.telegram_bot.send_message(chat_id, message_to_send)

    def __handle_text_messages__(self, chat_id, input_text_message):
        audio_regex_result = re.search('^/audio *', input_text_message)
        input_text_message = input_text_message.replace('/audio ', '')
        chatbot_text_answer = self.chatbot_client.get_answer(input_text_message)

        if (audio_regex_result):
            chatbot_audio_answer = self.speech_generation_client.get_speech(chatbot_text_answer)
            self.telegram_bot.send_audio(chat_id, chatbot_audio_answer)
        else:
            self.telegram_bot.send_message(chat_id, chatbot_text_answer)

    def __handle_image_messages__(self, chat_id, input_image_message, caption):
        downloaded_image_path = "./assets/received_image.jpg"
        text_message = 'Describe the image'
        audio_regex_result = False

        if (caption!=None):
            text_message = caption
            audio_regex_result = re.search('^/audio *', text_message)
            text_message = text_message.replace('/audio ', '')
            # If only "/audio" is provided as a caption, "Describe the image"
            # will be used as a default text prompt.
            if (len(text_message.split())==0):
                text_message = 'Describe the image'

        image_file_info = self.telegram_bot.get_file(input_image_message.file_id)
        downloaded_file = self.telegram_bot.download_file(image_file_info.file_path)

        with open(downloaded_image_path, "wb") as new_file:
            new_file.write(downloaded_file)

        chatbot_text_answer = self.vision_language_chatbot_client.get_answer(text_message, [downloaded_image_path])
        if (len(chatbot_text_answer.strip())==0):
            chatbot_text_answer = 'No response has been provided. Try with another caption'
        
        if (audio_regex_result):
            chatbot_audio_answer = self.speech_generation_client.get_speech(chatbot_text_answer)
            self.telegram_bot.send_audio(chat_id, chatbot_audio_answer)
        else:
            self.telegram_bot.send_message(chat_id, chatbot_text_answer)

    def __handle_voice_messages__(self, chat_id, input_voice_message):
        downloaded_voice_note_path = "./assets/received_voice_note.ogg"
        converted_audio_path = downloaded_voice_note_path.replace('.ogg', '.wav')

        image_file_info = self.telegram_bot.get_file(input_voice_message.file_id)
        downloaded_file = self.telegram_bot.download_file(image_file_info.file_path)

        with open(downloaded_voice_note_path, "wb") as new_file:
            new_file.write(downloaded_file)

        self.transcription_client.convert_audio_file_to_wav(downloaded_voice_note_path)
        input_voice_transcribed_text = self.transcription_client.get_transcription(converted_audio_path)

        chatbot_text_answer = self.chatbot_client.get_answer(input_voice_transcribed_text)
        chatbot_audio_answer = self.speech_generation_client.get_speech(chatbot_text_answer)
        self.telegram_bot.send_audio(chat_id, chatbot_audio_answer)
        
    def __handle_non_implemented_answers__(self, chat_id, message_type):
        self.telegram_bot.send_message(chat_id, f'Answers to data type {message_type} have not been implemented yet')

    def handle_messages(self, messages_list):
        try:
            for current_message_aux in messages_list:
                chat_id = current_message_aux.chat.id
                if (current_message_aux.content_type=='text'):
                    input_text_message = current_message_aux.text
                    self.__handle_text_messages__(chat_id, input_text_message)
                elif (current_message_aux.content_type=='photo'):
                    # The index -1 refers to the last image of the list, because it is the one
                    # with the highest resolution.
                    input_image_message = current_message_aux.photo[-1]
                    caption = current_message_aux.caption
                    self.__handle_image_messages__(chat_id, input_image_message, caption)
                elif (current_message_aux.content_type=='voice'):
                    voice = current_message_aux.voice
                    self.__handle_voice_messages__(chat_id, voice)
                else:
                    self.__handle_non_implemented_answers__(chat_id, current_message_aux.content_type)
        except Exception as exception_obj:
            self.__send_error_message__(chat_id, str(exception_obj))

    def run(self):
        print('Setting up the Telegram Bot...')
        self.build()
        print('Running the Telegram Bot...')
        self.telegram_bot.set_update_listener(self.handle_messages)
        self.telegram_bot.infinity_polling()
