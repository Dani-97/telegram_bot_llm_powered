import ollama

class ChatBotFactoryClient():

    def __init__(self):
        pass

    def create_chatbot(self, chatbot_type, host_url, port_number):
        chatbot_obj = None

        if (chatbot_type=='DeepSeekR1-1.5b'):
            chatbot_obj = Ollama_DeepSeekR1_1_5b_Client(host_url, port_number)
        elif (chatbot_type=='Gemma3-1b'):
            chatbot_obj = Ollama_Gemma3_1b_Client(host_url, port_number)
        elif (chatbot_type=='Moondream-1.8b'):
            chatbot_obj = Ollama_Moondream_1_8b_Client(host_url, port_number)

        return chatbot_obj

class Ollama_BaseCustomChatBot_Client():

    def __init__(self, host_url, port_number):
        full_host_url = f'{host_url}:{port_number}'
        self.client = ollama.Client(
            host=full_host_url
        )

    def get_answer(self, message):
        response = self.client.chat(model=self.model_type, options={'num_predict': -1}, messages=[
            {
                'role': 'user',
                'content': message
            },
        ])
        chatbot_text_answer = response.message.content
        chatbot_text_answer_snippets = chatbot_text_answer.split('</think>')

        if (len(chatbot_text_answer_snippets)>1):
            chatbot_text_answer = chatbot_text_answer.split('</think>')[1]

        return chatbot_text_answer

class Ollama_DeepSeekR1_1_5b_Client(Ollama_BaseCustomChatBot_Client):

    def __init__(self, host_url, port_number):
        super().__init__(host_url, port_number)
        self.model_type = 'deepseek-r1:1.5b'
        ollama.pull(self.model_type)

class Ollama_Gemma3_1b_Client(Ollama_BaseCustomChatBot_Client):

    def __init__(self, host_url, port_number):
        super().__init__(host_url, port_number)
        self.model_type = 'gemma3:1b'
        ollama.pull(self.model_type)

class Ollama_Moondream_1_8b_Client(Ollama_BaseCustomChatBot_Client):

    def __init__(self, host_url, port_number):
        super().__init__(host_url, port_number)
        self.model_type = 'moondream:1.8b'
        ollama.pull(self.model_type)

    def get_answer(self, message, images_list):
        response = self.client.chat(model=self.model_type, options={'num_predict': -1}, messages=[
            {
                'role': 'user',
                'content': message,
                'images': images_list
            },
        ])

        return response.message.content
