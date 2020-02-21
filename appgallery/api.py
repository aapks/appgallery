'''AppGallery.'''

__author__ = 'healplease'

import json

import requests

from .utils import AccessToken, Credentials, Upload, Message, AppInfo, AuditInfo, LangInfo, FileInfo, HuaweiException

class App():
    '''This class represents App.
    
    You can use all methods of client (except for obtain_token) through App instance.
    
    Example of usage:
        app = client.query_app('com.example')[0]
        app.query_app_info('ru')
        app.obtain_upload_URL('apk')
        app.upload.upload_file('my_file.apk')
        app.update_app_file_info('ru', 5, my_file_info)'''
    def __init__(self, client, parsed: dict):
        self.client = client
        self.package_name = parsed.get('key')
        self.id = parsed.get('value')
        self.upload = None

    def __repr__(self):
        return self.id

    def query_app_info(self, lang: str=None, release_type: int=None):
        '''Use this method to gain information about app.
        
        This method return instances of three classes as tuple:
        
        `AppInfo` contains detailed information about app.
        
        `AuditInfo` contains details of your app audition.
        
        List of `LangInfo` contains info about all languages of app if `lang` keyword is not specified, 
        otherwise contains info about specified language.
        
        Every of classes said has a `.JSON()` method to represent all it's data in JSON format.'''
        return self.client.query_app_info(self, lang, release_type)

    def update_app_info(self, info: AppInfo, release_type: int=None):
        '''Use this method to update main info about app.
        
        Example of usage:
            app_info, audit_info, lang_infos = my_app.query_app_info()
            app_info.privacy_policy = 'https://mysite.com/newprivacypolicy'
            app_info.is_free = False
            my_app.update_app_info(info=app_info)
            
        Look utils.py for full list of AppInfo fields.'''
        return self.client.update_app_info(self, info, release_type)

    def update_lang_info(self, lang: LangInfo):
        '''Use this method to update specified language info about app.
        
        Example of usage:
            app_info, audit_info, lang_infos = my_app.query_app_info()
            en_us_info = list(filter(lambda x: x.language == 'en_US', lang_infos))[0]
            en_us_info.app_name = 'Marvelous Pete 2'
            en_us_info.new_features = 'In this update we changed everything!'
            client.update_lang_info(app=my_app_instance, lang=lang_info)

        Only several fields can be updated through this method:
        `app_name`, `app_description`, `brief_info`, `new_features`.
            
        Look `utils.py` for full list of `LangInfo` fields.'''
        return self.client.update_lang_info(self, lang)

    def delete_lang_info(self, lang: (LangInfo, str)):
        '''Use this method to delete specified language off the app.
        
        `lang` can be `str` or `LangInfo` instance (`language` field will be used)'''
        return self.client.delete_lang_info(self, lang)

    def obtain_upload_URL(self, extension: str):
        '''Use this method to obtain upload URL.
        
        URL stored in `Upload` object. After obtaining of URL, you can interact with upload in both ways:

        Through `App` instance (preferrable):
            my_app.obtain_upload_URL('apk')
            file_info = my_app.upload.upload_file('test.apk')
            
        Through "independent" instance of `Upload`:
            my_upload = my_app.obtain_upload_URL('apk')
            file_info = my_upload.upload_file('test.apk')
            
        Be sure you store the FileInfo instance as it's needed for updating the app.'''
        return self.client.obtain_upload_URL(self, extension)

    def update_app_file_info(self, lang: (LangInfo, str), file_type: int, file_info: (FileInfo, list), **kwargs):
        '''Use this method to update your app with uploaded files.
        
        Specify the current lang, type of uploaded file (better to use utils.FT_ constants) and FileInfo of your file.
        
        Example of usage:
            my_upload = client.obtain_upload_URL(app=my_app, 'apk')
            file_info = my_app.upload.upload_file('test.apk')
            my_app.update_file_info(lang='en_US', file_type=utils.FT_APK_OR_RPK, file_info=file_info)
            
        Additional keywords can be obtained from official documentation:
            https://developer.huawei.com/consumer/en/service/hms/catalog/AGCConnectAPI.html?page=hmssdk_appGalleryConnect_api_reference_update_file_info_V2#Request%20Body'''
        return self.client.update_app_file_info(self, lang, file_type, file_info, **kwargs)

    def submit_for_release(self, release_time: str=None, remark: str=None, channel_ID: str=None, release_type: int=1):
        '''Use this method to submit your app for release.
        
        As you do this, your app will be reviewed by AppGallery for release.'''
        return self.client.submit_for_release(self, release_time, remark, channel_ID, release_type)

class Client():
    '''This is class for interaction with Huawei AppGallery Connect.
    
    You can pass the credentials for API through os.environ['HUAWEI_CREDENTIALS_PATH'] or as parameters while creating instance. 
    Keyword parameters have higher priority than environ path.

    You can obtain your `client_id` and `client_secret` in your AppGallery cabinet.
    
    `grant_type` must have value of `client_credentials`.'''
    API_URL = 'https://connect-api.cloud.huawei.com/api'
    def __init__(self, client_id: str=None, client_secret: str=None, grant_type: str=None):
        self.credentials = Credentials(client_id, client_secret, grant_type)
        self.obtain_token()

    def obtain_token(self):
        '''This method is for obtaining the token for access to other AppGallery functions.
        
        You don't need to call it yourself: it's obtaining and refreshing on expire automatically.'''
        url = Client.API_URL + '/oauth2/v1/token'
        data = {
            'grant_type': self.credentials.grant_type,
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret,
        }
        self.last_response = requests.post(url, json=data)
        if self.last_response.status_code == 200:
            response_parsed = json.loads(self.last_response.text)
            self.token = AccessToken(response_parsed)
        else:
            raise requests.RequestException(f'Unsuccessful request. Error code: {self.last_response.status_code}')

    def query_app(self, package_name: str):
        '''Use this method to gain the list of App() instances. 
        
        This returns list, as you can list for package names divided by comma.'''
        url = Client.API_URL + '/publish/v2/appid-list'
        data = {
            'packageName': package_name
        }
        headers = {
            'client_id': self.credentials.client_id,
            'Authorization': self.token.auth()
        }
        if self.token.is_expired():
            self.obtain_token()
        self.last_response = requests.get(url, params=data, headers=headers)
        print(self.last_response.text)
        if self.last_response.status_code == 200:
            response_parsed = json.loads(self.last_response.text)
            message = Message(response_parsed)
            if message.code > 0:
                raise HuaweiException(response_parsed.get('ret'))
            else:
                appId_list = response_parsed.get('appids')
                return [App(self, x) for x in appId_list]
        else:
            raise requests.RequestException(f'Unsuccessful request. Error code: {self.last_response.status_code}')

    def query_app_info(self, app: App, lang: str=None, release_type: int=None):
        '''Use this method to gain information about app.
        
        This method return instances of three classes as tuple:
        
        `AppInfo` contains detailed information about app.
        
        `AuditInfo` contains details of your app audition.
        
        List of `LangInfo` contains info about all languages of app if `lang` keyword is not specified, 
        otherwise contains info about specified language.
        
        Every of classes said has a `.JSON()` method to represent all it's data in JSON format.'''
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
        if self.token.is_expired():
            self.obtain_token()
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
        '''Use this method to update main info about app.
        
        Example of usage:
            app_info, audit_info, lang_infos = client.query_app_info(app=my_app_instance)
            app_info.privacy_policy = 'https://mysite.com/newprivacypolicy'
            app_info.is_free = False
            client.update_app_info(app=my_app_instance, info=app_info)
            
        Look utils.py for full list of AppInfo fields.'''
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
        if self.token.is_expired():
            self.obtain_token()
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
        '''Use this method to update specified language info about app.
        
        Example of usage:
            app_info, audit_info, lang_infos = client.query_app_info(app=my_app_instance)
            en_us_info = list(filter(lambda x: x.language == 'en_US', lang_infos))[0]
            en_us_info.app_name = 'Marvelous Pete 2'
            en_us_info.new_features = 'In this update we changed everything!'
            client.update_lang_info(app=my_app_instance, lang=lang_info)

        Only several fields can be updated through this method:
        `app_name`, `app_description`, `brief_info`, `new_features`.
            
        Look `utils.py` for full list of `LangInfo` fields.'''
        url = Client.API_URL + 'publish/v2/app-language-info?appId=' + app.id
        body = {
            'lang': lang.language
        }
        if lang.app_name:
            body.update({ 'appName': lang.appName })
        if lang.app_description:
            body.update({ 'appDesc': lang.appDesc })
        if lang.brief_info:
            body.update({ 'briefInfo': lang.briefInfo })
        if lang.new_features:
            body.update({ 'newFeatures': lang.newFeatures })

        headers = {
            'client_id': self.credentials.client_id,
            'Authorization': self.token.auth()
        }
        if self.token.is_expired():
            self.obtain_token()
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
        '''Use this method to delete specified language off the app.
        
        `lang` can be `str` or `LangInfo` instance (`language` field will be used)'''
        url = Client.API_URL + 'publish/v2/app-language-info'
        data = {
            'appId': app.id,
            'lang': lang if isinstance(lang, str) else lang.lang
        }
        headers = {
            'client_id': self.credentials.client_id,
            'Authorization': self.token.auth()
        }
        if self.token.is_expired():
            self.obtain_token()
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
        '''Use this method to obtain upload URL.
        
        URL stored in `Upload` object. After obtaining of URL, you can interact with upload in both ways:

        Through `App` instance (preferrable):
            client.obtain_upload_URL(app=my_app, 'apk')
            file_info = my_app.upload.upload_file('test.apk')
            
        Through "independent" instance of `Upload`:
            my_upload = client.obtain_upload_URL(app=my_app, 'apk')
            file_info = my_upload.upload_file('test.apk')
            
        Be sure you store the FileInfo instance as it's needed for updating the app.'''
        url = Client.API_URL + 'publish/v2/upload-url'
        data = {
            'appId': app.id,
            'suffix': extension
        }
        headers = {
            'client_id': self.credentials.client_id,
            'Authorization': self.token.auth()
        }
        if self.token.is_expired():
            self.obtain_token()
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
        '''Use this method to update your app with uploaded files.
        
        Specify the current lang, type of uploaded file (better to use utils.FT_ constants) and FileInfo of your file.
        
        Example of usage:
            my_upload = client.obtain_upload_URL(app=my_app, 'apk')
            file_info = my_app.upload.upload_file('test.apk')
            my_app.update_file_info(lang='en_US', file_type=utils.FT_APK_OR_RPK, file_info=file_info)
            
        Additional keywords can be obtained from official documentation:
            https://developer.huawei.com/consumer/en/service/hms/catalog/AGCConnectAPI.html?page=hmssdk_appGalleryConnect_api_reference_update_file_info_V2#Request%20Body'''
        url = Client.API_URL + '/publish/v2/app-file-info?appId=' + app.id
        body = {
            'lang': lang if isinstance(lang, str) else lang.lang,
            'fileType': file_type,
            'files' : file_info if isinstance(file_info, list) else [file_info,]
        }
        body.update(kwargs)

        headers = {
            'client_id': self.credentials.client_id,
            'Authorization': self.token.auth()
        }
        if self.token.is_expired():
            self.obtain_token()
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
        '''Use this method to submit your app for release.
        
        As you do this, your app will be reviewed by AppGallery for release.'''
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
        if self.token.is_expired():
            self.obtain_token()
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