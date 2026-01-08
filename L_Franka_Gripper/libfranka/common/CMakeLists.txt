cmake_minimum_required(VERSION 2.8.3)

add_library(libfranka-common INTERFACE)
target_include_directories(libfranka-common
  INTERFACE
    # 빌드 트리 내부에서 다른 타겟이 사용할 때의 경로
    $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/include>
    
    # 이 라이브러리를 설치한 후 외부 프로젝트에서 사용할 때의 경로
    $<INSTALL_INTERFACE:include>
)
