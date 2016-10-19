<p align="center">
  <img src="https://lh3.googleusercontent.com/xDZSHCWwnhFV2CJerQaVhhXlo2voaTNhMb8EdWgt3PZOxTOeFn_gA7tRT6EtOxlF5jY6Dz_r9cYYYC83Lj7EButeS5kyyxgIemTo6dnp1-pTySSZ2kKsukfkpoq5Z33d_6J6m1Oohq6zj7OUEW-mOxKDlTdFXAMqvvag02RDXKuZoVUmfTCnYLNC0gaCuV4y0S_cjDQCnBfmXRfi7yz9t5vvxePwJVpYoz_Dh0m_j1vfqmIibbjB8-3CF799CSGYYE8HkVLynB7LTVRkShsq17Wu2tHUts9saKLX2s35zme-MSjKNWGdhddZ62syOtCjj92y7fYw2BECzZgogH4fG9srRtogM5N4woYYXDHJZnCUWoSBxCIHH751uoUeHdU2HmOSDFivBQWg0s9f5iqQ9ro3i2RL5ottvggyVwJVWcXSApiAEYAIwK_0Z1ud3vuyc2eRsfGGQ0r0mXUQFAIB5FtACTnvmpSSOaQ7LXtapSbqD2aSbdtMREjXQRmrQeZEAM5H7MJ4dP2uam4mcRP8kLk7KC_urVr_WwR-OVmUn8Ox1LTdUn_j_ViZbXZkoYgBW0ExVPNSinIXYQDBdOibKYy6PxKolRdNvb1ZyCKMBRgQaH4V=w600-h500-no">
</p>
---
ArGeWeb 是個基於 [ferris-framework](https://ferris-framework.appspot.com) 的 Google app engine 開發框架

可以將功能模組拆成不同的組件 (plugin), 能對各功能進行啟用與停用

並在此基礎上進行了開發，以期能讓功能可以重覆進行使用

此啟始包還包含了 2個比較重要的組件

分別為

　　　　具有權限管理功能的使用者
  
　　　　[application_user](https://github.com/argeweb/plugin-application-user)
  
　　　　Material 風格的後台管理介面
  
　　　　[backend_ui_material](https://github.com/argeweb/plugin-backend-ui-material)


# 快速上手

安裝啟始包

    git clone https://github.com/argeweb/start.git
    
更新預設的組件

    cd plugins
    bower update

更新預設的前端元件

    cd static
    bower update

也可以直接執行 update.py 來進行更新
    
    
---
目前預設使用的組件有

    "backend_ui_material": "argeweb/plugin-backend-ui-material",
    "plugin_manager": "argeweb/plugin-plugin-manager",
    
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

# 相關工具與程式
* [Python 2.7](https://www.python.org/downloads/)
* [Google App Engine Quickstart for python](https://cloud.google.com/appengine/docs/python/quickstart) 

由於組件的管理使用 bower 所以需要 nodejs 與 bower

* [Node js](https://nodejs.org/en/) 
* [bower](https://bower.io/)    安裝 ( npm install -g bower )


