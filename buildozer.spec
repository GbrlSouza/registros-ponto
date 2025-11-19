[app]
title = AppPonto
package.name = appponto
package.domain = org.meuapp
source.dir = .
source.include_exts = py, png, jpg, kv, json
version = 0.1
requirements = python3, kivy
orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2

[android]
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = armeabi-v7a, arm64-v8a

android.release_keystore = mykeystore.jks
android.release_keystore_password = %(env.KEYSTORE_PASSWORD)s
android.release_keyalias = %(env.KEY_ALIAS)s
android.release_keyalias_password = %(env.KEY_PASSWORD)s
