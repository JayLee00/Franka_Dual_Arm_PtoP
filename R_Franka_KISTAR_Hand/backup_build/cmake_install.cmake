# Install script for directory: /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/soem" TYPE FILE FILES
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/soem/ethercat.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/soem/ethercatbase.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/soem/ethercatcoe.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/soem/ethercatconfig.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/soem/ethercatconfiglist.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/soem/ethercatdc.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/soem/ethercateoe.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/soem/ethercatfoe.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/soem/ethercatmain.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/soem/ethercatprint.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/soem/ethercatsoe.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/soem/ethercattype.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/osal/linux/osal_defs.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/osal/osal.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/oshw/linux/nicdrv.h"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/oshw/linux/oshw.h"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libfranka.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libfranka.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libfranka.so"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/build/libfranka.so")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libfranka.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libfranka.so")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libfranka.so"
         OLD_RPATH "/opt/openrobots/lib:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libfranka.so")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE DIRECTORY FILES
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/include/"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/libfranka/common/include/"
    USE_SOURCE_PERMISSIONS)
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/libfranka/cmake/Franka" TYPE FILE FILES
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/build/libfranka/FrankaConfig.cmake"
    "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/build/libfranka/FrankaConfigVersion.cmake"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libfranka/cmake/Franka/FrankaTargets.cmake")
    file(DIFFERENT EXPORT_FILE_CHANGED FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libfranka/cmake/Franka/FrankaTargets.cmake"
         "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/build/CMakeFiles/Export/lib/libfranka/cmake/Franka/FrankaTargets.cmake")
    if(EXPORT_FILE_CHANGED)
      file(GLOB OLD_CONFIG_FILES "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libfranka/cmake/Franka/FrankaTargets-*.cmake")
      if(OLD_CONFIG_FILES)
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libfranka/cmake/Franka/FrankaTargets.cmake\" will be replaced.  Removing files [${OLD_CONFIG_FILES}].")
        file(REMOVE ${OLD_CONFIG_FILES})
      endif()
    endif()
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/libfranka/cmake/Franka" TYPE FILE FILES "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/build/CMakeFiles/Export/lib/libfranka/cmake/Franka/FrankaTargets.cmake")
  if("${CMAKE_INSTALL_CONFIG_NAME}" MATCHES "^()$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/libfranka/cmake/Franka" TYPE FILE FILES "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/build/CMakeFiles/Export/lib/libfranka/cmake/Franka/FrankaTargets-noconfig.cmake")
  endif()
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/build/libfranka/common/cmake_install.cmake")
  include("/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/build/test/cmake_install.cmake")

endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/build/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
