<p align="center">
  <img src="https://lh3.googleusercontent.com/xDZSHCWwnhFV2CJerQaVhhXlo2voaTNhMb8EdWgt3PZOxTOeFn_gA7tRT6EtOxlF5jY6Dz_r9cYYYC83Lj7EButeS5kyyxgIemTo6dnp1-pTySSZ2kKsukfkpoq5Z33d_6J6m1Oohq6zj7OUEW-mOxKDlTdFXAMqvvag02RDXKuZoVUmfTCnYLNC0gaCuV4y0S_cjDQCnBfmXRfi7yz9t5vvxePwJVpYoz_Dh0m_j1vfqmIibbjB8-3CF799CSGYYE8HkVLynB7LTVRkShsq17Wu2tHUts9saKLX2s35zme-MSjKNWGdhddZ62syOtCjj92y7fYw2BECzZgogH4fG9srRtogM5N4woYYXDHJZnCUWoSBxCIHH751uoUeHdU2HmOSDFivBQWg0s9f5iqQ9ro3i2RL5ottvggyVwJVWcXSApiAEYAIwK_0Z1ud3vuyc2eRsfGGQ0r0mXUQFAIB5FtACTnvmpSSOaQ7LXtapSbqD2aSbdtMREjXQRmrQeZEAM5H7MJ4dP2uam4mcRP8kLk7KC_urVr_WwR-OVmUn8Ox1LTdUn_j_ViZbXZkoYgBW0ExVPNSinIXYQDBdOibKYy6PxKolRdNvb1ZyCKMBRgQaH4V=w600-h500-no">
</p>
---
ArGeWeb 是個基於 [ferris-framework](https://ferris-framework.appspot.com) 的 Google app engine 開發框架

可以將功能模組拆成不同的組件 (plugin), 能對各功能進行啟用與停用

並在此基礎上進行了開發，以期能讓功能可以重覆進行使用

此啟始包一共包含了 4個比較重要的組件

分別為

　　　　具有權限管理功能的使用者
  
　　　　[application_user](https://github.com/argeweb/plugin-application-user)
  
　　　　Material 風格的後台管理介面
  
　　　　[backend_ui_material](https://github.com/argeweb/plugin-backend-ui-material)
  
　　　　組件管理功能
  
　　　　[plugin_manager](https://github.com/argeweb/plugin-plugin-manager)
  
　　　　提供網站使用者進行檔案上傳
  
　　　　[user_file](https://github.com/argeweb/plugin-user-file)


# 快速上手

安裝啟始包

    git clone https://github.com/argeweb/start.git
    
更新預設的組件

    cd plugins
    bower update

更新預設的前端元件

    cd static
    bower update

也可以直接執行 [manage.py](https://github.com/argeweb/start/blob/master/manage.py) 來進行更新，[manage.py](https://github.com/argeweb/start/blob/master/manage.py) 會調用 argeweb/manage/ 目錄下的相關功能

    manage.py update

實際上是運行 argeweb/manage/ 目錄下的 [update.py](https://github.com/argeweb/start/blob/master/argeweb/manage/update.py)
下列是 Windows 下的批次檔，可以協助你更快的完成這些事

    @echo off
    set /p project= Enter Project Name:
    git clone https://github.com/argeweb/start.git %project%
    cd %project%
    cd argeweb\manage
    update.py
    run.py
    open.py

# 佈署到 Google App Engine
佈署到 Google App Engine 上，使用 argeweb/manage/deploy.py，或是

    manage.py update

這將會在 argeweb/manage 下建一個 project.json 的設定檔，若你需要佈署不同版本時，你也可以使用下面方式來建立其它設定，
    
    manage.py deploy [config-name]
    如
    manage.py deploy a01
  
同樣的，他這將會在 argeweb/manage 下建一個 a01.json 的設定檔

    
# 預設使用組件
目前預設使用的組件有

    "backend_ui_material": "argeweb/plugin-backend-ui-material",
    "plugin_manager": "argeweb/plugin-plugin-manager",

這2個組件還另外依賴了

    "application_user": "argeweb/plugin-application-user",
    "user_file": "argeweb/plugin-user-file",
    
目前預設使用的前端元件有

    "bootstrap": "^3.3.7",
    "jquery": "^2.1.4",
    "jquery-ui": "1.10.4",
    "jquery.steps": "jquery-steps#^1.1.0",
    "jquery-validation": "^1.15.1",
    "sweetalert2": "^4.1.9",
    "tinymce": "^4.4.1",
    "codemirror": "^5.18.2",
    "moment": "^2.14.1",
    "keymaster": "^1.6.3",
    "push.js": "^0.0.11",
    "bootstrap-table": "^1.11.0",
    "animate.css": "^3.5.2"

# 管理工具
  
  位於 argeweb/manage/ 下的工具可以幫助我們更快的完成一些工作
  使用 dev_appserver.py . 運行，或是利用下列的方式
     
    manage.py run
    
  安裝組件
     
    manage.py install
    manage.py install code
    manage.py install argeweb/plugin-code
   
  
  
 
# 相關工具與程式
* [Python 2.7](https://www.python.org/downloads/)
* [Google App Engine Quickstart for python](https://cloud.google.com/appengine/docs/python/quickstart) 

由於組件的管理使用 bower 所以需要 nodejs 與 bower

* [Node js](https://nodejs.org/en/) 
* [bower](https://bower.io/)    安裝 ( npm install -g bower )

---
# License
#### ArGeWeb Framework

Copyright (C) 2016 QiLiang Wen

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#### Third-party libraries
 
That are in the packages directory have varying licenses. Please check the license file that is included within each package.

* Ferris: Apache License, Version 2
* httplib2 : MPL 1.1/GPL 2.0/LGPL 2.1
* ProtoPigeon: Apache License v2
* WTForms: BSD
* PyTZ: MIT
* mosql: MIT
* GData Client Library: Apache License v2
* Google API Python Client Library: Apache License v2

若有疏露沒有列舉到的地方，請多多見諒，再麻煩告知我們