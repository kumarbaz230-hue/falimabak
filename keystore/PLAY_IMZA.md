# Release imzalama

Keystore dosyasini bu klasore koyma — `.gitignore` ile haric tutulur.

## Olusturma

```powershell
keytool -genkey -v -keystore falimabak-release.keystore -alias falimabak -keyalg RSA -keysize 2048 -validity 10000
```

## GitHub Secret icin base64

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("falimabak-release.keystore")) | Set-Clipboard
```

Bu ciktiyi `KEYSTORE_BASE64` secret olarak ekle.

## Ortam degiskenleri (buildozer release)

```
P4A_RELEASE_KEYSTORE
P4A_RELEASE_KEYSTORE_PASSWD
P4A_RELEASE_KEYALIAS
P4A_RELEASE_KEYALIAS_PASSWD
```
