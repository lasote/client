from biicode.client.workspace.hive_disk_image import HiveDiskImage
from biicode.client.dev.hardware.android import DEV_ANDROID_DIR
from biicode.common.utils.file_utils import save_blob_if_modified, load_resource
import os
from biicode.common.model.blob import Blob
from biicode.common.output_stream import Color


def install_android_toolchain(bii):
    '''Arduino Toolchain uses AVR-GCC & AVR-G++ compilers
    '''
    bii.user_io.out.write('Creating toolchain for Android\n', Color.BLUE)

    android_toolchain_files = ["android_macros.cmake", "android_toolchain.cmake"]

    modified = False
    for android_file in android_toolchain_files:
        source_path = os.path.join(DEV_ANDROID_DIR, "cmake", android_file)
        dest_path = os.path.join(bii.hive_disk_image.paths.bii, android_file)
        android_cmake = load_resource(DEV_ANDROID_DIR, source_path)
        modified |= save_blob_if_modified(dest_path, Blob(android_cmake))

    if modified:
        bii.user_io.out.warn("Android toolchain defined, regenerating project")
        bii.hive_disk_image.delete_build_folder()

    bii.user_io.out.success('Run "bii configure -t android" to activate it')
    bii.user_io.out.success('Run "bii configure -t" to disable it')


def save_android_settings(bii, new_settings):
    '''
    Save settings and regenerate arduino_settings.cmake from current settings. Cleans project if needed
    '''
    # Clean build if settings change
    if new_settings.android != bii.hive_disk_image.settings.android:
        bii.hive_disk_image.delete_build_folder()

    # Generate cmake content
    android_settings_cmake = load_resource(DEV_ANDROID_DIR, "cmake/android_settings.cmake")
    settings_cmake = android_settings_cmake.format(abi=new_settings.android.abi,
                                                   api_level=new_settings.android.api_level,
                                                   ndk=new_settings.android.ndk,
                                                   sdk=new_settings.android.sdk,
                                                   ant=new_settings.android.ant
                                                   )
    # Save android_settings.cmake
    settings_path = os.path.join(bii.hive_disk_image.paths.bii, "android_settings.cmake")
    save_blob_if_modified(settings_path, Blob(settings_cmake))

    # Save settings
    bii.hive_disk_image.settings = new_settings
