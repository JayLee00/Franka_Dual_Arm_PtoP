
set(SOURCES L_Franka_Gripper.cpp
   ${PROJECT_SOURCE_DIR}/libfranka/examples/examples_common.cpp
)

include_directories(
  include
  include/kistar_hand
  )

add_executable(L_Franka_Gripper ${SOURCES})
target_link_libraries(L_Franka_Gripper 
  soem
  franka
  Eigen3::Eigen
)

install(TARGETS L_Franka_Gripper DESTINATION bin)

target_include_directories(L_Franka_Gripper PRIVATE
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/include/kistar_hand
    ${PROJECT_SOURCE_DIR}/libfranka/examples
)

set(FRANKA_IS_FOUND TRUE)

## Tools
file(GLOB_RECURSE SOURCES
  libfranka/src/*.cpp
  libfranka/examples/*.cpp
  libfranka/common/*.cpp
)
file(GLOB_RECURSE HEADERS
  libfranka/include/*.h
  libfranka/src/*.h
  libfranka/examples/*.h
  libfranka/common/*.h
)
file(GLOB_RECURSE TIDY_IGNORED_FILES
  libfranka/src/libfcimodels.h
)