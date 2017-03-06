GamePlay-deps
=============

Open-source dependencies for GamePlay.

| Host     | Target Platform             | Target Arch                            
|----------|-----------------------------|----------------------------------------
| Windows  | windows                     | x86_64
| Linux    | linux                       | x86_64
|          | android                     | armeabi-v7a
|          |                             | x86
| MacOS    | macos                       | x86_64                                 
|          | ios                         | arm (armv7,armv7s,arm64) 
|          |                             | x86 (i386,x86_64)
|          | android                     | arm (armeabi-v7a)
|          |                             | x86


# Compiling (Host and Target are the same)

## Windows

* Generates Visual Studio 2015 project files. 
* Run commands from 'VS2015 x64 Native Tools Command Prompt'. 
* Builds x86_64(x64) Debug and Release. 

```
> cd GamePlay-deps
> mkdir build
> cd build
> cmake -G "Visual Studio 14 Win64" ..
> msbuild GamePlay-deps.sln /property:Configuration=Debug
> msbuild GamePlay-deps.sln /property:Configuration=Release
```

## Linux and MacOS

* Generates makefile project files.
* Run commands from Terminal console.
* Builds x86_64(x64) Release. 

```
$ cd GamePlay-deps
$ mkdir build
$ cd build
$ cmake ..
$ make install

```

Build outputs:

* Header ----->     out/external-deps/include
* Libraries -->     out/external-deps/lib/\<target platform\>/\<target arch\>

# Cross-Compiling (Host and Target are different)

## Android Setup

Install NVIDIA CodeWorks for Android 1R6 (includes Android SDK and NDK):
https://developer.nvidia.com/codeworks-android

* Once installed, setup a standalone toolchain directory for each architecture you want to build:
* Run from Windows mingw command prompt or Linux/MacOS terminal console:

```
$ cd android-ndk-r12b/build/tools
$ python make_standalone_toolchain.py --arch arm --api 24 --install-dir /path/to/android-toolchain-arm
```

This will install the standalone toolchain directories in: 
/path/to/android-toolchain-arm

## Android Compiling
* Generates ndk-build build targets.
* Run from platform console/terminal.
* Builds the specified android architecture.

```
$ cd GamePlay-deps
$ mkdir build
$ cd build
$ export ANDROID_STANDALONE_TOOLCHAIN=/path/to/android-toolchain-arm
$ cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/android.toolchain.cmake ..
$ make
```
For building the simulator version (or another arch) just change the environment variable:

` $ export ANDROID_STANDALONE_TOOLCHAIN=/path/to/android-toolchain-x86 `


## iOS Setup

Install XCode

## iOS Compiling

* Generates makefile build targets.
* Run from platform terminal.
* Builds the arm architecture that combines armv7,armv7s and arm64.

```
$ cd GamePlay-deps
$ mkdir build
$ cd build
$ cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/ios.toolchain.cmake -DIOS_PLATFORM=OS ..
$ make install
```

For building simulator version we change the IOS_PLATFORM flag:

` $ cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/ios.toolchain.cmake -DIOS_PLATFORM=SIMULATOR .. `
