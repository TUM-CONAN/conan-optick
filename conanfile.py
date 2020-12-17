#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os

def sort_libs(correct_order, libs, lib_suffix='', reverse_result=False):
    # Add suffix for correct string matching
    correct_order[:] = [s.__add__(lib_suffix) for s in correct_order]

    result = []
    for expectedLib in correct_order:
        for lib in libs:
            if expectedLib == lib:
                result.append(lib)

    if reverse_result:
        # Linking happens in reversed order
        result.reverse()

    return result

class LibnameConan(ConanFile):
    name = "optick"
    version = "1.3.1.0"
    description =   "A profiler for game engines"
    # topics can get used for searches, GitHub topics, Bintray tags etc. Add here keywords about the library
    topics = ("conan", "corrad", "magnum", "filesystem", "console", "environment", "os")
    url = "https://github.com/TUM-CONAN/conan-optick"
    homepage = "https://github.com/bombomby/optick"
    author = "ulrich eck"
    license = "MIT"  # Indicates license type of the packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    exports = ["LICENSE.md"]
    # exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    short_paths = True  # Some folders go out of the 260 chars path length scope (windows)

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False, 
        "fPIC": True,
    }

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        # "zstd/1.4.3",
    )

    # temporary until release fixes interconnect issues on windows/release builds
    scm = {
        "type": "git",
        "subfolder": _source_subfolder,
        "url": "https://github.com/ulricheck/optick.git",
        "revision": "master", #"%s" % (version),
        "submodule": "recursive",
    }

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    # def configure(self):
    #     if self.settings.compiler == 'Visual Studio' and int(self.settings.compiler.version.value) < 14:
    #         raise ConanException("{} requires Visual Studio version 14 or greater".format(self.name))

    def _configure_cmake(self):

        cmake = CMake(self)
        cmake.verbose = True

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str 
            cmake.definitions[var_name] = var_value

        for option, value in self.options.items():
            add_cmake_option(option, value)

        # cmake.definitions["OPTICK_INSTALL_TARGETS"] = "ON"
        #cmake.definitions["OPTICK_BUILD_CONSOLE_SAMPLE"] = "ON"
        #cmake.definitions["OPTICK_BUILD_GUI_APP"] = "ON"

        # OPTICK_USE_VULKAN
        # OPTICK_USE_D3D12

        # cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)

        return cmake

    def build(self):

        # tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
        #     """add_library(zdepth STATIC ${SOURCE_FILES})""",
        #     """add_library(zdepth ${SOURCE_FILES})""")

        # tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
        #     """if (NOT TARGET zstd)""",
        #     """if (NOT TARGET CONAN_PKG::zstd)
        #     MESSAGE(STATUS \"Target CONAN_PKG::zstd is misisng\")""")

        # tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
        #     """target_link_libraries(zdepth PUBLIC zstd)""",
        #     """target_link_libraries(zdepth PUBLIC CONAN_PKG::zstd)""")

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "src"), keep_path=False)

        # self.copy(pattern="*.a", dst="lib", src=self._build_subfolder, keep_path=False)
        # self.copy(pattern="*.so", dst="lib", src=self._build_subfolder, keep_path=False)
        # self.copy(pattern="*.lib", dst="lib", src=self._build_subfolder, keep_path=False)
        # self.copy(pattern="*.dll", dst="bin", src=self._build_subfolder, keep_path=False)
 
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
