add_subdirectory(log)

install(
    DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/ DESTINATION ${CMAKE_INSTALL_PREFIX}/python/lsst/log
    PATTERN "CMakeLists.txt" EXCLUDE
    PATTERN "SConscript" EXCLUDE
    PATTERN "*.cc" EXCLUDE
)

file(GENERATE OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/version.py CONTENT "\
__version__ = 'unknown'
__all__ = ('__version__',)
")

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/version.py DESTINATION ${CMAKE_INSTALL_PREFIX}/python/lsst/log)
