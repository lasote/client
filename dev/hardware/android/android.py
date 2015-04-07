'''
Created on 5/3/2015

@author: laso
'''
from biicode.client.command.process_executor import simple_exe
import platform
import os
from biicode.common.exception import BiiException
from biicode.common.utils.file_utils import save_blob_if_modified
from biicode.common.model.blob import Blob
import shutil


create_project_command = '{android_tool} -s create project --path {path}' \
                         ' --target android-{api_level} ' \
                         ' --name {name}' \
                         ' --package {package}' \
                         ' --activity {activity}'


manifest_native_template = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
      package="{package}"
      android:versionCode="1"
      android:versionName="1.0">
    <uses-sdk android:minSdkVersion="9" />
    <application android:label="@string/app_name"
                 android:hasCode="false" android:debuggable="true">
        <activity android:name="android.app.NativeActivity"
                  android:label="@string/app_name">
            <meta-data android:name="android.app.lib_name" android:value="{libname}" />
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
'''


class Android(object):
    def __init__(self, bii):
        self.bii = bii

    def upload(self):
        # retcode = simple_exe(command, cwd=cwd)
        pass

    def new_app(self, name):

        if self.bii.bii_paths.current_dir not in self.bii.hive_disk_image.disk_blocks.itervalues():
            raise BiiException("Execute this command in a block folder")

        android_settings = self.bii.hive_disk_image.settings.android
        if not android_settings.sdk:
            raise BiiException("Android SDK setting not found. Please, execute "
                               "bii android:settings")
        if not android_settings.api_level:
            raise BiiException("Android api level setting not found. Please, "
                               "execute bii android:settings")

        android_tool = self._android_tool(android_settings.sdk)
        api_level = android_settings.api_level
        # activity = activity or "%sActivity" % name.capitalize()
        activity = "%sActivity" % name
        package = "com.biicode.%s" % name
        command = create_project_command.format(android_tool=android_tool, activity=activity,
                                                name=name, api_level=api_level,
                                                package=package,
                                                path=name
                                                )
        self.bii.user_io.out.info('Executing: "%s"' % command)
        retcode = simple_exe(command)

        new_manifest_content = manifest_native_template.format(libname=name, package=package)

        path = os.path.join(self.bii.bii_paths.current_dir, name)
        save_blob_if_modified(os.path.join(path, "AndroidManifest.xml"), Blob(new_manifest_content))

        try:
            shutil.rmtree(os.path.join(self.bii.bii_paths.current_dir, name, "src"))  # Empty src
        except OSError:
            pass
        return retcode


#     TODO: Make a command to upload with adb?
#     add_custom_command(TARGET ${apk_target} POST_BUILD
#                         COMMAND ${BII_ADB_TOOL} install -r bin/${apk_local_target}-debug.apk
#                         WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${apk_local_target}/android)

    def _android_tool(self, sdk_path):
        if platform.system() == 'Windows':
            return os.path.join(sdk_path, "tools", "android.exe")
        else:
            return os.path.join(sdk_path, "tools", "android")
