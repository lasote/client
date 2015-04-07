import argparse
from biicode.client.dev.hardware.serial_monitor import monitor
from biicode.common.exception import BiiException
from biicode.client.workspace.hive_disk_image import HiveDiskImage
from biicode.client.client_hive_manager import ClientHiveManager
from biicode.client.dev.cpp.cpptoolchain import CPPToolChain
from biicode.client.dev.hardware.android.android import Android
from biicode.client.dev.hardware.android.cmaketool import install_android_toolchain,\
    regenerate_android_settings_cmake


class AndroidToolChain(CPPToolChain):
    '''Android commands'''
    group = 'android'

    def __init__(self, bii):
        super(AndroidToolChain, self).__init__(bii)
        self.bii = bii
        self.arduino = Android(bii)

    def configure(self, *parameters):
        '''HIDDEN not show configure from cmake_tool_chain '''
        raise BiiException('''Use "cpp:configure"''')

    def test(self, *parameters):
        '''HIDDEN not show test from cmake_tool_chain '''
        raise BiiException('''Use "cpp:test"''')

    def build(self, *parameters):
        '''HIDDEN'''
        raise BiiException(''' Build your program with:

  > bii cpp:build

NOTE: Before building an Android project you should configure your project (just once):

    1. "bii android:settings": Configure IDE, board, etc
    2. "bii cpp:configure -t android": Activate toolchain

''')

    def new_app(self, *parameters):
        '''Generate new default Android project'''
        parser = argparse.ArgumentParser(description=self.settings.__doc__,
                                         prog="bii %s:generate_project" % self.group)
        parser.add_argument('name', type=str, help='Name of project')
        # parser.add_argument("--activity", type=str, nargs="?", default=None)
        # parser.add_argument("--package", type=str, nargs="?", default=None)
        args = parser.parse_args(*parameters)  # for -h
        self.arduino.new_app(args.name)

    def settings(self, *parameters):
        '''Configure project settings for android'''
        parser = argparse.ArgumentParser(description=self.settings.__doc__,
                                         prog="bii %s:settings" % self.group)
        parser.parse_args(*parameters)  # for -h
        settings = self.bii.hive_disk_image.settings
        # android_settings_wizard(self.bii.user_io, settings)

        # TODO: Make a wizard connected with the setup
        sdk_path = self.bii.user_io.request_string("Enter android SDK path", settings.android.sdk)
        ndk_path = self.bii.user_io.request_string("Enter android NDK path", settings.android.ndk)
        ant_path = self.bii.user_io.request_string("Enter ANT tool exe path", settings.android.ant)

        sdk_path = sdk_path.replace('\\', '/')
        ndk_path = ndk_path.replace('\\', '/')
        ant_path = ant_path.replace('\\', '/')

        api_level = self.bii.user_io.request_string("Enter API level",
                                                    settings.android.api_level or 20)
        abi = self.bii.user_io.request_string("Enter ABI", settings.android.abi or "x86")

        settings.android.sdk = sdk_path
        settings.android.ndk = ndk_path
        settings.android.ant = ant_path
        settings.android.api_level = api_level
        settings.android.abi = abi

        self.bii.hive_disk_image.settings = settings
        install_android_toolchain(self.bii)
        regenerate_android_settings_cmake(self.bii)
