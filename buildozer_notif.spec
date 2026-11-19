[app]
title = DyslexiaLiFT Notificaciones
package.name = dyslexialiftnotif
package.domain = org.dyslexialift
source.dir = .
source.include_exts = py,kv,json,db
version = 0.1

requirements = python3,kivy==2.3.1,plyer,pyjnius
orientation = portrait
fullscreen = 0

android.permissions = INTERNET, POST_NOTIFICATIONS, VIBRATE, WAKE_LOCK

android.api = 34
android.minapi = 24
android.ndk_api = 24
android.ndk_version = 25b
android.build_tools_version = 34.0.0

android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True
android.enable_jetifier = True

entrypoint = notificaciones.py

[buildozer]
log_level = 2
