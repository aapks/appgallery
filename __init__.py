'''The AppGallery Connect API provides RESTful APIs that can be used to customize services provided by AppGallery Connect or implement process automation, thereby improving your work efficiency. 

Currently, this API package includes Publishing API. Reports API will be asap.

Official documentation: https://developer.huawei.com/consumer/en/service/hms/catalog/AGCConnectAPI.html?page=AGC_appGalleryConnect_connectApiIntroduction

Examples of usage:

Setting up credentials:
    import os
    import appgallery
    from appgallery import utils

    os.environ['HUAWEI_CREDENTIALS_PATH'] = 'path/to/credentials.json'
    client = appgallery.Client()

Working with apps:
    apps = client.query_app(package_name='com.example.app')
    my_app = apps[0]
    app_info, audit_info, lang_info = my_app.query_app_info(lang='en_US')

Uploading files:
    my_app.obtain_upload_URL(extension='apk')
    file_info = my_app.upload.upload_file(filepath='path/to/package.apk')

Upload can be used as object too:
    my_upload = my_app.obtain_upload_URL(extension='png')
    file_info = my_upload.upload_file(filepath='path/to/picture.png')

Updating and submitting your app:
    my_app.update_app_file_info(lang='en_US', filetype=utils.FT_APK_OR_RPK, file_info=file_info)
    my_app.submit_for_release()

'''
import os

from api import Client

os.environ['HUAWEI_CREDENTIALS_PATH'] = r'D:\healplease\PYTHON\huawei_upload\huawei_credentials.json'
client = Client()

apps = client.query_app('com.absolutist.littleelephanthidden.huawei')

app = apps[0]
print(app)