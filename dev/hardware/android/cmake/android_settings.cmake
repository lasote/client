set(ANDROID_ABI {abi})
set(ANDROID_NATIVE_API_LEVEL {api_level})
set(ANDROID_NDK {ndk})
set(ANDROID_SDK {sdk})
set(BII_ANT_TOOL {ant})

IF(WIN32)
    set(BII_ANDROID_TOOL {sdk}/tools/android.bat)
    set(BII_ADB_TOOL {sdk}/tools/adb.exe)
ELSE()
    set(BII_ANDROID_TOOL {sdk}/tools/android)
    set(BII_ADB_TOOL {sdk}/platform-tools/adb)
ENDIF()
