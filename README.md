<p align="center">
  <img src="https://lh3.googleusercontent.com/xDZSHCWwnhFV2CJerQaVhhXlo2voaTNhMb8EdWgt3PZOxTOeFn_gA7tRT6EtOxlF5jY6Dz_r9cYYYC83Lj7EButeS5kyyxgIemTo6dnp1-pTySSZ2kKsukfkpoq5Z33d_6J6m1Oohq6zj7OUEW-mOxKDlTdFXAMqvvag02RDXKuZoVUmfTCnYLNC0gaCuV4y0S_cjDQCnBfmXRfi7yz9t5vvxePwJVpYoz_Dh0m_j1vfqmIibbjB8-3CF799CSGYYE8HkVLynB7LTVRkShsq17Wu2tHUts9saKLX2s35zme-MSjKNWGdhddZ62syOtCjj92y7fYw2BECzZgogH4fG9srRtogM5N4woYYXDHJZnCUWoSBxCIHH751uoUeHdU2HmOSDFivBQWg0s9f5iqQ9ro3i2RL5ottvggyVwJVWcXSApiAEYAIwK_0Z1ud3vuyc2eRsfGGQ0r0mXUQFAIB5FtACTnvmpSSOaQ7LXtapSbqD2aSbdtMREjXQRmrQeZEAM5H7MJ4dP2uam4mcRP8kLk7KC_urVr_WwR-OVmUn8Ox1LTdUn_j_ViZbXZkoYgBW0ExVPNSinIXYQDBdOibKYy6PxKolRdNvb1ZyCKMBRgQaH4V=w600-h500-no">
</p>
---
ArGeWeb 是個基於 ferris-framework 的 Google app engine 開發框架

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
    
