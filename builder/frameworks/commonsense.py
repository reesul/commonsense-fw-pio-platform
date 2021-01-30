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
framework = "framework-commonsense"

CMSIS_DIR = platform.get_package_dir("framework-cmsis")
CMSIS_ATMEL_DIR = platform.get_package_dir("framework-cmsis-atmel")
FRAMEWORK_DIR = platform.get_package_dir(framework)

assert all(os.path.isdir(d) for d in (CMSIS_DIR, CMSIS_ATMEL_DIR, FRAMEWORK_DIR))


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
        "-mthumb",
        "-nostdlib",
        "--param", "max-inline-insns-single=500"
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16",
        "-march=armv7e-m"
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions",
        "-std=gnu++11",
        "-fno-threadsafe-statics"
    ],

    CPPDEFINES=[
        ("F_CPU", "$BOARD_F_CPU")
    ],

    LINKFLAGS=[
        "-Os",
        "-mthumb",
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16",
        "-march=armv7e-m"
        # "-Wl,--cref", # don't enable it, it prints Cross Reference Table
        "-Wl,--gc-sections",
        "-Wl,--check-sections",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align",
        "--specs=nosys.specs",
        "--specs=nano.specs"
    ],

    LIBS=["m"],

    CPPPATH=[
        os.path.join(CMSIS_DIR, "CMSIS", "Include"),
        os.path.join(CMSIS_ATMEL_DIR, "CMSIS", "Device", "ATMEL"),
        os.path.join(CMSIS_ATMEL_DIR, "CMSIS", "Device", "ATMEL", board.get("build.variant")),
        os.path.join(FRAMEWORK_DIR),
        os.path.join(FRAMEWORK_DIR, "core"),
        os.path.join(FRAMEWORK_DIR, "atmel_studio_drivers/hal"),
        os.path.join(FRAMEWORK_DIR, "atmel_studio_drivers/hal/include"),
        os.path.join(FRAMEWORK_DIR, "atmel_studio_drivers/hal/utils/include"),
        os.path.join(FRAMEWORK_DIR, "atmel_studio_drivers/hal/utils/src"),
        os.path.join(FRAMEWORK_DIR, "atmel_studio_drivers/hal/src"),
        os.path.join(FRAMEWORK_DIR, "atmel_studio_drivers/hpl"),
        os.path.join(FRAMEWORK_DIR, "atmel_studio_drivers/hri"),
        os.path.join(FRAMEWORK_DIR, "atmel_studio_drivers/Config"),
        # os.path.join(FRAMEWORK_DIR, "sample"),

    ],

    LIBPATH=[
        os.path.join(CMSIS_DIR, "CMSIS", "Lib", "GCC"),
        os.path.join(FRAMEWORK_DIR, "linker")
    ],
)

if "BOARD" in env:
    env.Append(
        CCFLAGS=[
            "-mcpu=%s" % board.get("build.cpu")
        ],
        LINKFLAGS=[
            "-mcpu=%s" % board.get("build.cpu")
        ]
    )


env.Prepend(
    CCFLAGS=[

    ],

    LINKFLAGS=[


    ],

    LIBS=["arm_cortexM4lf_math"]
)

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])


# include a path to the linker script. This will make the binary start at the Reset_Handler function, which calls main after some initialization
if not board.get("build.ldscript", ""):
    env.Replace(LDSCRIPT_PATH="commonsense_linker.ld")


libs = []

libs.append(env.BuildLibrary(
    os.path.join("$BUILD_DIR", "FrameworkCommonSense"),
    os.path.join(FRAMEWORK_DIR, "core")
))

libs.append(env.BuildLibrary(
    os.path.join("$BUILD_DIR", "AtmelStudioDrivers"),
    os.path.join(FRAMEWORK_DIR, "atmel_studio_drivers")
))

env.Prepend(LIBS=libs)
 
 #TODO: make board specific files that have a few different flags
# env.Append(
#     CPPDEFINES = ("__CS_V_2_0__")
# )