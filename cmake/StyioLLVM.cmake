find_package(LLVM 18.1.0 REQUIRED CONFIG)

# LLVM headers pollute the translation unit (e.g. cxxabi); keep them on styio
# targets only so GoogleTest and helper tools can compile without LLVM on the
# direct include path.
separate_arguments(LLVM_DEFINITIONS_LIST NATIVE_COMMAND ${LLVM_DEFINITIONS})

message(STATUS "[LLVM] Include Directory: ${LLVM_INCLUDE_DIRS}")
message(STATUS "[LLVM] Definitions: ${LLVM_DEFINITIONS_LIST}")
message(STATUS "[LLVM] Version: ${LLVM_PACKAGE_VERSION}")
message(STATUS "[LLVM] Using LLVMConfig.cmake in: ${LLVM_DIR}")

llvm_map_components_to_libnames(LLVM_LIBS support core irreader orcjit native)
