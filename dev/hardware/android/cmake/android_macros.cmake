#Create android_src folder
if(ANDROID)
   file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/android_src")
endif()

# OVERRIDES BII_ADD_EXECUTABLE
function(BII_ADD_EXECUTABLE exename exesources)
    # We don't want an executable for android, we want a shared library
    ADD_LIBRARY(${exename} SHARED ${BII_${FNAME}_SRC})

    # Link BLOCK_TARGET libraries (its not done in BII_GENERATE_EXECUTABLE)
    TARGET_LINK_LIBRARIES(${exename} PUBLIC ${BII_BLOCK_TARGET})

    # Register the "hooks" for build APK before build the library
    BII_PREPARE_APK_BUILD_CALLBACKS(${FNAME})

endfunction()


#=============================================================================#
# [PRIVATE/INTERNAL]
#
# BII_TO_NATIVE_PATH(path)
#   path is a var name
# converts a string to a path usable by the shell (it is important when cross compiling)
#
#=============================================================================#
macro (BII_TO_NATIVE_PATH path)
    FILE(TO_NATIVE_PATH "${${path}}" ${path})
    # DETECTING ANDROID-WINDOWS CROSS-COMPILING
    IF(${CMAKE_GENERATOR} MATCHES "MinGW")
        STRING(REPLACE "/" "\\" ${path} "${${path}}")
    ENDIF()
endmacro()



#=============================================================================#
# [PRIVATE/INTERNAL]
#
# DECLARE_ANDROID_JAVA_CODE()
#
# useful to include java code into dependant apks. The code with its  class path
# is included into the Apk project that make use of this block
#  base_dir: relative block source dir. i.e.: MyJavaCode  (user/block/MyJavaCode/* is copied)
#  java_base_dir: target base class path. i.e.: com/biicode  (the paths relative to the first param are added to)
#=============================================================================#
macro(BII_DECLARE_JAVA_CODE base_dir)
    set (extra_macro_args ${ARGN})
    list(LENGTH extra_macro_args num_extra_args)
    if (${num_extra_args} GREATER 0)
        list(GET extra_macro_args 0 java_base_dir)
        message ("Got an optional java_base_dir: ${java_base_dir}")
    endif ()

   file(GLOB_RECURSE java_files RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/${base_dir} "${CMAKE_CURRENT_SOURCE_DIR}/${base_dir}/*.*")
   if(java_base_dir)
     file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/${base_dir}/ DESTINATION ${CMAKE_BINARY_DIR}/android_src/${java_base_dir})
   else()
     file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/${base_dir}/ DESTINATION ${CMAKE_BINARY_DIR}/android_src)
   endif()
endmacro()

#=============================================================================#
# [PUBLIC/USER] [[USER BLOCK CMAKELISTS]
#
# BII_USE_ANDROID_APK_PROJECT(target native_so_lib android_project_folder)
#
#        target  -relative to the block, f.e. : myMain (the real cmake target is user_block_myMain)
#        native_so_lib -the name of the dynamic lib (without lib and so extension), specified in the java activity
#        android_project_folder    - Relative path to block, f.e. : android-proyect should be interpreted user/block/android-project
#
# In order to correctly build an apk, an android project structure is needed. This command, allows the user android project
# definition. Biicode would only place the resulting dynamic lib of the target into the lib directory of this project. A copy
# of the android project is modified to match the platform and ANDROID API configured
#
#=============================================================================#
macro (BII_USE_ANDROID_APK_PROJECT target native_so_lib android_project_folder)

    # COPY THE ENTIRE PROJECT TO SUBFOLDER in "android" BUILD
    FILE(COPY ${CMAKE_CURRENT_SOURCE_DIR}/${android_project_folder}/ DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/${target}/android)

    # COPY THE COLLECTED SRCS (THROUGH ) TO DESTINATION PROJECT FOLDER
    file(COPY ${CMAKE_BINARY_DIR}/android_src/ DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/${target}/android/src/)

    # RENAME LIB TO ${native_so_lib}
    set_target_properties(${BII_BLOCK_USER}_${BII_BLOCK_NAME}_${target} PROPERTIES OUTPUT_NAME ${native_so_lib})
endmacro()


macro(BII_PREPARE_APK_BUILD_CALLBACKS apk_local_target )
    set(apk_target ${BII_BLOCK_USER}_${BII_BLOCK_NAME}_${apk_local_target})
    set(ANDROID_TARGET_LIB_OUTDIR ${CMAKE_CURRENT_BINARY_DIR}/${apk_local_target}/android/libs/${ANDROID_NDK_ABI_NAME})

    # Sets the output directory for library
    set_target_properties(${apk_target} PROPERTIES LIBRARY_OUTPUT_DIRECTORY  ${ANDROID_TARGET_LIB_OUTDIR})
    set_target_properties(${apk_target} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_RELEASE ${ANDROID_TARGET_LIB_OUTDIR})
    set_target_properties(${apk_target} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_DEBUG ${ANDROID_TARGET_LIB_OUTDIR})

    # Complete/modify project (fist copied in BII_USE_ANDROID_APK_PROJECT) if needed for the specified target
    add_custom_command(TARGET ${apk_target} COMMAND ${BII_ANDROID_TOOL} -s update project
                            --path "${apk_local_target}/android"
                            --target android-${ANDROID_NATIVE_API_LEVEL}
                            --name ${apk_local_target} --subprojects
                            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                            )

    # Copy the shared library to android build project directory
    set(android_project_apk_lib_location "${CMAKE_HOME_DIRECTORY}/../bin/lib${apk_target}.so")
    BII_TO_NATIVE_PATH(android_project_apk_lib_location)

    add_custom_command(TARGET ${apk_target} POST_BUILD
                       COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${apk_target}> ${android_project_apk_lib_location})

    # Call ant to build apk
    if(NOT ANT_BUILD_TYPE)
        if ("${CMAKE_BUILD_TYPE}" STREQUAL "Release")
            set(ANT_BUILD_TYPE "release")
        else()
            set(ANT_BUILD_TYPE "debug")
        endif()
    endif()

    SET(project_build_dir ${CMAKE_CURRENT_BINARY_DIR}/${apk_local_target}/android)

    add_custom_command(TARGET ${apk_target} POST_BUILD
                       COMMAND ${BII_ANT_TOOL} ${ANT_BUILD_TYPE}
                       WORKING_DIRECTORY ${project_build_dir})

    # Copy from android project bin to biicode project folder
    set(apk_location "${project_build_dir}/bin/${apk_local_target}-${ANT_BUILD_TYPE}.apk")
    BII_TO_NATIVE_PATH(apk_location)


    set(android_output_apk_dir "${CMAKE_HOME_DIRECTORY}/../bin/${apk_target}-${ANT_BUILD_TYPE}.apk")
    BII_TO_NATIVE_PATH(android_output_apk_dir)

    add_custom_command(TARGET ${apk_target} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy ${apk_location} ${android_output_apk_dir})

 endmacro()
