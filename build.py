##############################################################################
# Packaging script for building and packaging gameplay-deps-<platform>.zip 
##############################################################################
import os
import glob
import platform
import subprocess
import shutil
import sys
import time
import zipfile
from pathlib import Path
from distutils.dir_util import copy_tree

# constants
##############################################################################

CMAKE_WINDOWS_GENERATOR = "Visual Studio 16 2019"
CMAKE_UNIX_GENERATOR = "Unix Makefiles"

BUILD_FOLDER = "_build"
PACKAGE_FOLDER = "_package"
TOOLS_FOLDER = "_tools"
ZIP_FOLDER = "_zip"

# platform-architecture
##############################################################################
platform_arch = ""
if sys.platform == "win32":
    platform_arch = "windows-x86_64"
elif sys.platform == "darwin":
    platform_arch = "macos-x86_64"
else:
    platform_arch = "linux-x86_64"

# function utils
##############################################################################

def clear_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)
    path = Path(dir_path)
    path.mkdir(parents=True)

def init_vsvars():
    vswhere_path = r"%ProgramFiles(x86)%/Microsoft Visual Studio/Installer/vswhere.exe"
    vswhere_path = os.path.expandvars(vswhere_path)
    if not os.path.exists(vswhere_path):
        raise EnvironmentError("vswhere.exe not found at: %s", vswhere_path)
    vs_path = os.popen('"{}" -latest -property installationPath'.format(vswhere_path)).read().rstrip()
    vsvars_path = os.path.join(vs_path, "VC\\Auxiliary\\Build\\vcvars64.bat")
    output = os.popen('"{}" && set'.format(vsvars_path)).read()
    for line in output.splitlines():
        pair = line.split("=", 1)
        if(len(pair) >= 2):
            os.environ[pair[0]] = pair[1]

def cmake_generator_args(user_args):
    if sys.platform == "win32":
        return f"-G \"{CMAKE_WINDOWS_GENERATOR}\"{user_args}"
    else:
        return f"-G \"{CMAKE_UNIX_GENERATOR}\"{user_args}"

def cmake_build(dep_folder, generator_args, solution, **kwargs):
    project_dir = os.path.join(os.getcwd(), dep_folder)
    build_dir = os.path.join(project_dir, BUILD_FOLDER)
    clear_dir(build_dir)
    cmake_proc = subprocess.Popen(f"cmake {generator_args} ..", cwd=build_dir, shell=True)
    cmake_proc.wait()
    caller_dir = os.getcwd()
    os.chdir(build_dir)
    if sys.platform == "win32":
        init_vsvars()
        cmd = f"msbuild {solution}.sln /property:Configuration=Debug"
        subprocess.run(cmd)
        cmd = f"msbuild {solution}.sln /property:Configuration=Release"
        subprocess.run(cmd)
    else:
        cmd = f"make"
        subprocess.run(cmd)
    os.chdir(caller_dir)

def copy_files(src_dir, dst_dir, match_exp):
    clear_dir(dst_dir)
    for filename in glob.glob(os.path.join(src_dir, match_exp)):
        shutil.copy(filename, dst_dir)

def remove_files(src_dir, match_exp):
    for filename in glob.glob(os.path.join(src_dir, match_exp)):
        os.remove(filename)

def create_package(src_dir, dst_file):
    package = zipfile.ZipFile(dst_file, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            full_path = os.path.join(root, file)
            package.write(full_path, os.path.relpath(full_path, src_dir))
    package.close()

# package outputs
##############################################################################
package_dir = os.path.join(os.getcwd(), PACKAGE_FOLDER)
clear_dir(package_dir)

# pybind11
##############################################################################
dep_folder = "pybind11-2.6.2"
print(f"Preparing {dep_folder}...")
dst_dir = os.path.join(package_dir, "pybind11")
src_include_dir = os.path.join(dep_folder, "include", "pybind11")
dst_include_dir = os.path.join(dst_dir, "include", "pybind11")
copy_tree(src_include_dir, dst_include_dir)

# spdlog
##############################################################################
dep_folder = "spdlog-1.8.2"
print(f"Preparing {dep_folder}...")
dst_dir = os.path.join(package_dir, "spdlog")
src_include_dir = os.path.join(dep_folder, "include", "spdlog")
dst_include_dir = os.path.join(dst_dir, "include", "spdlog")
copy_tree(src_include_dir, dst_include_dir)

# glm
##############################################################################
dep_folder = "glm-0.9.9.8"
print(f"Preparing {dep_folder}...")
src_include_dir = os.path.join(dep_folder, "glm")
dst_include_dir = os.path.join(package_dir, "glm", "include", "glm")
copy_tree(src_include_dir, dst_include_dir)
remove_files(dst_include_dir, "*.txt")

# cpptoml
##############################################################################
dep_folder = "cpptoml-0.1.1"
print(f"Preparing {dep_folder}...")
src_include_dir = os.path.join(dep_folder, "include")
dst_include_dir = os.path.join(package_dir, "cpptoml", "include")
copy_tree(src_include_dir, dst_include_dir)

# stb
##############################################################################
dep_folder = "stb-b42009b"
print(f"Preparing {dep_folder}...")
src_include_dir = os.path.join(dep_folder)
dst_include_dir = os.path.join(package_dir, "stb", "include")
copy_files(src_include_dir, dst_include_dir,"*.h")



# glfw
##############################################################################
dep_folder = "glfw-3.3.2"
print(f"Preparing {dep_folder}...")
dst_dir = os.path.join(package_dir, "glfw")
cmake_build(dep_folder, cmake_generator_args(" -D USE_MSVC_RUNTIME_LIBRARY_DLL=FALSE"), "GLFW")
src_include_dir = os.path.join(dep_folder, "include", "GLFW")
dst_include_dir = os.path.join(dst_dir, "include", "GLFW")
copy_files(src_include_dir, dst_include_dir, "*.*")
dst_bin_dir = os.path.join(dst_dir, "bin", platform_arch)
src_bin_dir = os.path.join(dep_folder, BUILD_FOLDER, "src")
if sys.platform == "win32":
    copy_files(os.path.join(src_bin_dir, "Debug"), os.path.join(dst_bin_dir, "debug"), "*.*")
    copy_files(os.path.join(src_bin_dir, "Release"), os.path.join(dst_bin_dir, "release"), "*.*")
else:
    copy_files(src_bin_dir, dst_bin_dir, "lib*.a")

# freetype
##############################################################################
dep_folder = "freetype-2.10.4"
print(f"Preparing {dep_folder}...")
dst_dir = os.path.join(package_dir, "freetype")
cmake_build(dep_folder, cmake_generator_args(" -D DISABLE_FORCE_DEBUG_POSTFIX=TRUE"), "freetype")
src_include_dir = os.path.join(dep_folder, "include")
dst_include_dir = os.path.join(package_dir, "freetype", "include")
copy_tree(src_include_dir, dst_include_dir)
dst_bin_dir = os.path.join(dst_dir, "bin", platform_arch)
src_bin_dir = os.path.join(dep_folder, BUILD_FOLDER)
if sys.platform == "win32":
    copy_files(os.path.join(src_bin_dir, "Debug"), os.path.join(dst_bin_dir, "debug"), "*.*")
    copy_files(os.path.join(src_bin_dir, "Release"), os.path.join(dst_bin_dir, "release"), "*.*")
else:
    copy_files(src_bin_dir, dst_bin_dir, "lib*.a")

# imgui
##############################################################################
dep_folder = "imgui-1.8.0"
print(f"Preparing {dep_folder}...")
src_dir = dep_folder
dst_dir = os.path.join(package_dir, "imgui")
copy_tree(src_dir, dst_dir)
clear_dir(os.path.join(dst_dir, "examples"))
clear_dir(os.path.join(dst_dir, "docs"))
remove_files(dst_dir, "LICENSE.txt")

# zip file
##############################################################################
zip_dir = ZIP_FOLDER
clear_dir(zip_dir)
zip_filename = ""
if sys.platform == "win32":
    zip_filename = "gameplay-deps-windows.zip"
elif sys.platform == "darwin":
    zip_filename = "gameplay-deps-macos.zip"
else:
    zip_filename = "gameplay-deps-linux.zip"

print(f"Packaging {zip_filename}...")
create_package(package_dir, os.path.join(zip_dir, zip_filename))
