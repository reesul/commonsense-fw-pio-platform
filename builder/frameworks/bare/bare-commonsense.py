# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" 
Bare

For CommonSense projects that do not claim to be part of another framework. This is effectively a baremetal project, which only needs to include links to CMSIS and Atmel files, plus any linker scripts or other necessary files for ensuring the program will boot to a "main" C/Cpp function.

This borrows heavily from scripts developed by Adafruit and Arduino for Platform IO

-Reese Grimsley 6/2020
"""

import os
from SCons.Script import DefaultEnvironment


env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

CMSIS_DIR = platform.get_package_dir("framework-cmsis")
CMSIS_ATMEL_DIR = platform.get_package_dir("framework-cmsis-atmel")

assert all(os.path.isdir(d) for d in (CMSIS_DIR, CMSIS_ATMEL_DIR))


env.Append(

    CPPPATH=[
        os.path.join(CMSIS_DIR, "CMSIS", "Include"),
        os.path.join(CMSIS_ATMEL_DIR, "CMSIS", "Device", "ATMEL"),
        os.path.join(CMSIS_ATMEL_DIR, "CMSIS", "Device", "ATMEL", board.get("build.variant"))
        # os.path.join(FRAMEWORK_DIR, "cores", BUILD_CORE)
    ],

    LIBPATH=[
        os.path.join(CMSIS_DIR, "CMSIS", "Lib", "GCC"),
    ],

    # these have caused issue in the past with the linker, possibly due to lack of true linker file for GCC
    LINKFLAGS=[
        "--specs=nosys.specs",
        "--specs=nano.specs"
    ]
)

env.Prepend(
    CCFLAGS=[
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16"
    ],

    LINKFLAGS=[
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16"
    ],

    LIBS=["arm_cortexM4lf_math"]
)

env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],

    CFLAGS=[
        "-std=gnu11"
    ],

    CCFLAGS=[
        "-Os",  # optimize for size
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-Wall",
        "-mcpu=%s" % board.get("build.cpu"),
        "-mthumb",
        "-nostdlib",
        "--param", "max-inline-insns-single=500"
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions",
        "-std=gnu++11",
        "-fno-threadsafe-statics"
    ],

    LINKFLAGS=[
        "-Os",
        "-mcpu=%s" % board.get("build.cpu"),
        "-mthumb",
        "-Wl,--gc-sections",
        "-Wl,--check-sections",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align"
    ],

    LIBS=["m"]
)
p = env.get("$PLATFORMIO_PLATFORMS_DIR")
print("\n\n\n\n\n")
print(p)
print("\n\n\n\n")

p = os.path.join(p, "commonsense", "linker", "commonsense_linker.ld")
 

if not board.get("build.ldscript", ""):
    # Will this path work? Unsure about the env.get. Would like to avoid making a new framework if possible since it'd be so minimal
    env.Replace(LDSCRIPT_PATH=p)