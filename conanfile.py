# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import platform

# copied from Hulud's bintray hdf5

class Hdf5Conan(ConanFile):
    name = "hdf5"
    version_src = "1.10.1"
    version = version_src
    license = ""
    url = "https://github.com/bldrvnlw/conan-hdf5"
    homepage = "https://bitbucket.hdfgroup.org/projects/HDFFV/repos/hdf5/browse"
    author = "B. van Lew <b.van_lew@lumc.nl>"    
    description = "Makes possible the management of extremely large and complex data collections. https://www.hdfgroup.org"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
            
    def source(self):
        filename = "hdf5-%s.tar.gz" % self.version_src
        if platform.system() == "Windows":
            filename = "hdf5-%s.zip" % self.version_src
            tools.download("https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.10/hdf5-1.10.1/src/CMake-hdf5-1.10.1.zip", filename)
            tools.unzip(filename)
        else: 
            tools.download("https://support.hdfgroup.org/ftp/HDF5/current/src/%s" % filename, filename)
            tools.untargz(filename)
        os.unlink(filename)
        os.rename ("CMake-hdf5-%s" % self.version_src, "hdf5-%s" % self.version)
        os.chdir("hdf5-%s" % self.version)

        tools.replace_in_file("hdf5-%s/CMakeLists.txt" % self.version, "PROJECT (HDF5 C CXX)",
                              """project (HDF5 C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
""")

        file = "hdf5-%s/src/CMakeLists.txt" % self.version
        with open(file, "a") as myfile:
            myfile.write('''
# Hulud : Force threadsafe in static library
if (HDF5_ENABLE_THREADSAFE) 
    set_property (TARGET ${HDF5_LIB_TARGET}
        APPEND PROPERTY COMPILE_DEFINITIONS
            "H5_HAVE_THREADSAFE"
    )
    target_link_libraries (${HDF5_LIB_TARGET} Threads::Threads)
  endif ()
''')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = False  # example
        cmake.configure(build_folder=self._build_subfolder)
        return cmake
        
    def build(self):
        cmake = CMake(self)
        #cmake.configure(source_dir="%s/hdf5-%s" % (self.source_folder, self.version_src))
        #cmake.build()

        # Explicit way:
        self.run('cmake %s/hdf5-1.10.1/hdf5-%s %s -DHDF5_ENABLE_THREADSAFE="ON" -DHDF5_BUILD_HL_LIB="OFF" -DHDF5_BUILD_CPP_LIB="OFF" -DHDF5_BUILD_EXAMPLES="OFF" -DHDF5_BUILD_TOOLS="OFF" -DBUILD_TESTING="OFF" -DCMAKE_INSTALL_PREFIX="%s"' % (self.source_folder, self.version, cmake.command_line, self.package_folder))
        self.run("cmake --build . --target install %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        pass

#    def package_info(self):
#        self.cpp_info.libs = ["libhdf5"]

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        # self.cpp_info.libs = ["libhdf5"]
