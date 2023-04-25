#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import load, update_conandata, copy, replace_in_file, collect_libs
import os


class LibnameConan(ConanFile):

    name = "optick"
    version = "1.4.0.0"
    description = "A profiler for game engines"
    topics = ("conan", "corrad", "magnum", "filesystem", "console", "environment", "os")
    url = "https://github.com/TUM-CONAN/conan-optick"
    homepage = "https://github.com/bombomby/optick"
    author = "ulrich eck"
    license = "MIT"
    exports = ["LICENSE.md"]

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

    def export(self):
        update_conandata(self, {"sources": {
            "commit": "master",
            "url": "https://github.com/ulricheck/optick.git"
        }})

    def source(self):
        git = Git(self)
        sources = self.conan_data["sources"]
        git.clone(url=sources["url"], target=self.source_folder, args=["--recursive", ])
        git.checkout(commit=sources["commit"])

    def generate(self):
        tc = CMakeToolchain(self)

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str
            tc.variables[var_name] = var_value

        for option, value in self.options.items():
            add_cmake_option(option, value)

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="source_folder")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        # self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "src"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)


