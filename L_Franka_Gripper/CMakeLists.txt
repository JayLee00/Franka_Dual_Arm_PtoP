cmake_minimum_required(VERSION 3.0.0)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/libfranka/include/franka/cmake")

project(Franka_Hand_Test1 
VERSION 0.1.1 
LANGUAGES C CXX)

set(libfranka_VERSION 0.9.2)

set(SOEM_INCLUDE_INSTALL_DIR include/soem)
set(SOEM_LIB_INSTALL_DIR lib)


if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  message(STATUS "SOEM: Build Shared Memory Test for Hand-arm system")
  set(BUILD_TESTS TRUE)
else()
  message(STATUS "SOEM: not building tests when built as dependency")
  set(BUILD_TESTS FALSE)
endif()
list(INSERT CMAKE_MODULE_PATH 0 "${CMAKE_CURRENT_SOURCE_DIR}/libfranka/include/franka/cmake")

set(OS "linux")
set(OS_LIBS pthread rt)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(MSVC)
  add_compile_options(/W0)
else()
  add_compile_options(-Wall -Wextra)
endif()


find_package(Poco REQUIRED COMPONENTS Net Foundation)
find_package(Eigen3 REQUIRED)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

file(GLOB SOEM_SOURCES soem/*.c)
file(GLOB OSAL_SOURCES osal/${OS}/*.c)
file(GLOB OSHW_SOURCES oshw/${OS}/*.c)

file(GLOB SOEM_HEADERS soem/*.h)
file(GLOB OSAL_HEADERS osal/osal.h osal/${OS}/*.h)
file(GLOB OSHW_HEADERS oshw/${OS}/*.h)

add_library(soem STATIC
  ${SOEM_SOURCES}
  ${OSAL_SOURCES}
  ${OSHW_SOURCES}
  ${OSHW_EXTRA_SOURCES}
)
target_link_libraries(
  soem ${OS_LIBS}
  pthread
  ) 

target_include_directories(soem PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/soem>
  $<INSTALL_INTERFACE:include/soem>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/osal>
  $<INSTALL_INTERFACE:include/soem>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/osal/${OS}>
  $<INSTALL_INTERFACE:include/soem>
  PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/oshw/${OS}>
  $<INSTALL_INTERFACE:include/soem>
 
  ${PROJECT_SOURCE_DIR}/include
  ${PROJECT_SOURCE_DIR}/include/kistar_hand
  ${PROJECT_SOURCE_DIR}
  ${PROJECT_SOURCE_DIR}/libfranka/include
  ${PROJECT_SOURCE_DIR}/libfranka/common/include
  ${PROJECT_SOURCE_DIR}/libfranka/examples
  )
install(FILES
  ${SOEM_HEADERS}
  ${OSAL_HEADERS}
  ${OSHW_HEADERS}
  DESTINATION ${SOEM_INCLUDE_INSTALL_DIR})

  include_directories(
  include
  include/kistar_hand
)

add_subdirectory(libfranka/common)


add_library(franka SHARED
  libfranka/src/control_loop.cpp
  libfranka/src/control_tools.cpp
  libfranka/src/control_types.cpp
  libfranka/src/duration.cpp
  libfranka/src/errors.cpp
  libfranka/src/exception.cpp
  libfranka/src/gripper.cpp
  libfranka/src/gripper_state.cpp
  libfranka/src/library_downloader.cpp
  libfranka/src/library_loader.cpp
  libfranka/src/load_calculations.cpp
  libfranka/src/log.cpp
  libfranka/src/logger.cpp
  libfranka/src/lowpass_filter.cpp
  libfranka/src/model.cpp
  libfranka/src/model_library.cpp
  libfranka/src/network.cpp
  libfranka/src/rate_limiting.cpp
  libfranka/src/robot.cpp
  libfranka/src/robot_impl.cpp
  libfranka/src/robot_state.cpp
  libfranka/src/vacuum_gripper.cpp
  libfranka/src/vacuum_gripper_state.cpp
)
add_library(Franka::Franka ALIAS franka)


target_compile_features(franka INTERFACE
  cxx_attribute_deprecated
  cxx_constexpr
  cxx_defaulted_functions
  cxx_deleted_functions
  cxx_generalized_initializers
  cxx_noexcept
  cxx_uniform_initialization
)
if(MSVC)
  target_compile_definitions(franka PUBLIC
    _USE_MATH_DEFINES # for M_PI in cmath
    NOMINMAX # avoid conflict with std::min
  )
endif()

target_include_directories(franka PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/libfranka/include>
  $<INSTALL_INTERFACE:include>
)

target_link_libraries(franka PRIVATE
  Poco::Foundation
  Poco::Net
  Eigen3::Eigen
  Threads::Threads
  libfranka-common
)



## Installation
include(GNUInstallDirs)
set(INSTALL_CMAKE_CONFIG_DIR ${CMAKE_INSTALL_LIBDIR}/libfranka/cmake/Franka)

install(TARGETS franka libfranka-common
  EXPORT FrankaTargets
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(DIRECTORY include/ libfranka/common/include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  USE_SOURCE_PERMISSIONS
)

export(EXPORT FrankaTargets
  NAMESPACE Franka::
  FILE ${CMAKE_CURRENT_BINARY_DIR}/FrankaTargets.cmake
)

include(CMakePackageConfigHelpers)
write_basic_package_version_file(${CMAKE_CURRENT_BINARY_DIR}/FrankaConfigVersion.cmake
  COMPATIBILITY SameMajorVersion
)
configure_package_config_file(libfranka/cmake/FrankaConfig.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/libfranka/FrankaConfig.cmake
  INSTALL_DESTINATION ${INSTALL_CMAKE_CONFIG_DIR}
)

install(FILES
  ${CMAKE_CURRENT_BINARY_DIR}/libfranka/FrankaConfig.cmake
  ${CMAKE_CURRENT_BINARY_DIR}/libfranka/FrankaConfigVersion.cmake
  DESTINATION ${INSTALL_CMAKE_CONFIG_DIR}
)
install(EXPORT FrankaTargets
  NAMESPACE Franka::
  DESTINATION ${INSTALL_CMAKE_CONFIG_DIR}
)

add_subdirectory(test)
