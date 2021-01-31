import requests
import json

class Request :
    def __init__(self):
        self.__url = None
        self.__json_data = None
        self.__json_file = None

    def set_request_attr(self, url, image_path, modules=None):
        self.__url = url
        self.__json_file = {'image_path': image_path}
        if modules is not None :
            self.__json_data = {'modules':modules}
        else :
            self.__json_data = {}

    def get_request_attr(self):
        return self.__url, self.__json_data, self.__json_file

    def send_request_message(self):
        try :
            response = requests.post(url=self.__url, data=self.__json_data, files=self.__json_file)
            response = json.loads(response.content)
        except :
            response = {}

        return response