find_package(pybind11 REQUIRED)

pybind11_add_module(log_pybind MODULE)
set_target_properties(log_pybind PROPERTIES OUTPUT_NAME "log")

target_sources(log_pybind PRIVATE
    log.cc
)

target_link_libraries(log_pybind PRIVATE
    log
)

install(TARGETS log_pybind DESTINATION ${CMAKE_INSTALL_PREFIX}/python/lsst/log/log)
