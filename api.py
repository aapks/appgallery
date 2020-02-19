'''AppGallery.'''

__author__ = 'healplease'

import json

import requests

from utils import AccessToken, Credentials, Upload, Message, AppInfo, AuditInfo, LangInfo, FileInfo, HuaweiException

class App():
    def __init__(self, client, parsed: dict):
        self.client = client
        self.package_name = parsed.get('packageName')
        self.id = parsed.get('appId')
        self.upload = None

    def __repr__(self):
        return self.id

    def query_app_info(self, lang: str=None, release_type: int=None):
        return self.client.query_app_info(self, lang, release_type)

    def update_app_info(self, info: AppInfo, release_type: int=None):
        return self.client.update_app_info(self, info, release_type)

    def update_lang_info(self, lang: LangInfo):
        return self.client.update_lang_info(self, lang)

    def delete_lang_info(self, lang: (LangInfo, str)):
        return self.client.delete_lang_info(self, lang)

    def obtain_upload_URL(self, extension: str):
        return self.client.obtain_upload_URL(self, extension)

    def update_app_file_info(self, lang: (LangInfo, str), file_type: int, file_info: (FileInfo, list), **kwargs):
        return self.client.update_app_file_info(self, lang, file_type, file_info, **kwargs)

    def submit_for_release(self, release_time: str=None, remark: str=None, channel_ID: str=None, release_type: int=1):
        return self.client.submit_for_release(self, release_time, remark, channel_ID, release_type)

class Client():
    API_URL = 'https://connect-api.cloud.huawei.com/api'
    def __init__(self, client_id: str=None, client_secret: str=None, grant_type: str=None):
        self.credentials = Credentials(client_id, client_secret, grant_type)
        self.obtain_token()

    def obtain_token(self):
        url = Client.API_URL + '/oauth2/v1/token'
        data = {
            'grant_type': self.credentials.grant_type,
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret,
        }
        headers = {

        }
        self.last_response = requests.get(url, params=data, headers=headers)
        if self.last_response.status_code == 200:
            response_parsed = json.loads(self.last_response.text)
            self.token = AccessToken(response_parsed)
        else:
            raise requests.RequestException(f'Unsuccessful request. Error code: {self.last_response.status_code}')

    def query_app(self, package_name: str):
        url = Client.API_URL + '/publish/v2/appid-list'
        data = {
            'packageName': package_name
        }
        headers = {
            'client_id': self.credentials.client_id,
            'Authorization': self.token.auth()
        }
        self.last_response = requests.get(url, params=data, headers=headers)
        if self.last_response.status_code == 200:
            response_parsed = json.loads(self.last_response.text)
            message = Message(response_parsed)
            if message.code > 0:
                raise HuaweiException(response_parsed.get('ret'))
            else:
                appId_list = response_parsed.get('appId')
                return [App(self, x) for x in appId_list]
        else:
            raise requests.RequestException(f'Unsuccessful request. Error code: {self.last_response.status_code}')

    def query_app_info(self, app: App, lang: str=None, release_type: int=None):
        url = Client.API_URL + 'publish/v2/app-info'
        data = {
            'appId': app.id
        }

        if lang:
            data.update({ 'lang': lang })
        if release_type:
            data.update({ 'releaseType': release_type })

        headers = {
            'client_id': self.credentials.client_id,
            'Authorization': self.token.auth()
        }
        self.last_response = requests.get(url, params=data, headers=headers)
        if self.last_response.status_code == 200:
            response_parsed = json.loads(self.last_response.text)
            message = Message(response_parsed)
            if message.code > 0:
                raise HuaweiException(response_parsed.get('ret'))
            else:
                info = response_parsed.get('appInfo')
                audit = response_parsed.get('auditInfo')
                languages = response_parsed.get('languages')
                return AppInfo(info), AuditInfo(audit), list(map(LangInfo, languages))
        else:
            raise requests.RequestException(f'Unsuccessful request. Error code: {self.last_response.status_code}')

    def update_app_info(self, app: App, info: AppInfo, release_type: int=None):
        url = Client.API_URL + 'publish/v2/app-info'
        data = {
            'appId': app.id,
            'appInfo': info.JSON()
        }
        if release_type:
            data.update({ 'releaseType': release_type })

        headers = {
            'client_id': self.credentials.client_id,
            'token': self.token.token
        }
        self.last_response = requests.put(url, data=data, headers=headers)
        if self.last_response.status_code == 200:
            response_parsed = json.loads(self.last_response.text)
            message = Message(response_parsed)
            if message.code > 0:
                raise HuaweiException(response_parsed.get('ret'))
            else:
                return None
        else:
            raise requests.RequestException(f'Unsuccessful request. Error code: {self.last_response.status_code}')

    def update_lang_info(self, app: App, lang: LangInfo):
        url = Client.API_URL + 'publish/v2/app-language-info?appId=' + app.id
        body = {
            'lang': lang.language
        }
        if lang.app_name:
            body.update({ 'appName': lang.app_name })
        if lang.app_description:
            body.update({ 'appDesc': lang.app_name })
        if lang.brief_info:
            body.update({ 'briefInfo': lang.app_name })
        if lang.new_features:
            body.update({ 'newFeatures': lang.app_name })

        headers = {
            'client_id': self.credentials.client_id,
            'Authorization': self.token.auth()
        }
        self.last_response = requests.put(url, json=body, headers=headers)
        if self.last_response.status_code == 200:
            response_parsed = json.loads(self.last_response.text)
            message = Message(response_parsed)
            if message.code > 0:
                raise HuaweiException(response_parsed.get('ret'))
            else:
                return None
        else:
            raise requests.RequestException(f'Unsuccessful request. Error code: {self.last_response.status_code}')

    def delete_lang_info(self, app: App, lang: (LangInfo, str)):
        url = Client.API_URL + 'publish/v2/app-language-info'
        data = {
            'appId': app.id,
            'lang': lang if isinstance(lang, str) else lang.language
        }
        headers = {
            'client_id': self.credentials.client_id,
            'Authorization': self.token.auth()
        }
        self.last_response = requests.delete(url, data=data, headers=headers)
        if self.last_response.status_code == 200:
            response_parsed = json.loads(self.last_response.text)
            message = Message(response_parsed)
            if message.code > 0:
                raise HuaweiException(response_parsed.get('ret'))
            else:
                return None
        else:
            raise requests.RequestException(f'Unsuccessful request. Error code: {self.last_response.status_code}')

    def obtain_upload_URL(self, app: App, extension: str):
        url = Client.API_URL + 'publish/v2/upload-url'
        data = {
            'appId': app.id,
            'suffix': extension
        }
        headers = {
            'client_id': self.credentials.client_id,
            'Authorization': self.token.auth()
        }
        self.last_response = requests.delete(url, data=data, headers=headers)
        if self.last_response.status_code == 200:
            response_parsed = json.loads(self.last_response.text)
            message = Message(response_parsed)
            if message.code > 0:
                raise HuaweiException(response_parsed.get('ret'))
            else:
                app.upload = Upload(response_parsed)
                return Upload(response_parsed)
        else:
            raise requests.RequestException(f'Unsuccessful request. Error code: {self.last_response.status_code}')

    def update_app_file_info(self, app: App, lang: (LangInfo, str), file_type: int, file_info: (FileInfo, list), **kwargs):
        url = Client.API_URL + '/publish/v2/app-file-info?appId=' + app.id
        body = {
            'lang': lang if isinstance(lang, str) else lang.language,
            'fileType': file_type,
            'files' : file_info if isinstance(file_info, list) else [file_info,]
        }
        body.update(kwargs)

        headers = {
            'client_id': self.credentials.client_id,
            'Authorization': self.token.auth()
        }
        self.last_response = requests.put(url, json=body, headers=headers)
        if self.last_response.status_code == 200:
            response_parsed = json.loads(self.last_response.text)
            message = Message(response_parsed)
            if message.code > 0:
                raise HuaweiException(response_parsed.get('ret'))
            else:
                return None
        else:
            raise requests.RequestException(f'Unsuccessful request. Error code: {self.last_response.status_code}')

    def submit_for_release(self, app: App, release_time: str=None, remark: str=None, channel_ID: str=None, release_type: int=1):
        url = Client.API_URL + 'publish/v2/app-submit'
        data = {
            'appId': app.id,
            'releaseType': release_type
        }
        if release_time:
            data.update({ 'releaseTime': release_time })
        if remark:
            data.update({ 'remark': remark })
        if channel_ID:
            data.update({ 'channelId': channel_ID })

        headers = {
            'client_id': self.credentials.client_id,
            'Authorization': self.token.auth()
        }

        self.last_response = requests.post(url, data=data, headers=headers)
        if self.last_response.status_code == 200:
            response_parsed = json.loads(self.last_response.text)
            message = Message(response_parsed)
            if message.code > 0:
                raise HuaweiException(response_parsed.get('ret'))
            else:
                return None
        else:
            raise requests.RequestException(f'Unsuccessful request. Error code: {self.last_response.status_code}')