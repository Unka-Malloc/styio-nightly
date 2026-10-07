# Build identity is descriptive, not proof of release provenance or support.
set(STYIO_BUILD_VERSION "0.0.1" CACHE STRING
    "Compiler build version (numeric major.minor.patch; does not certify a release)")
set(STYIO_FULL_RELEASE_CHANNEL "nightly" CACHE STRING
    "Full compiler build channel (safe identifier; does not certify a release)")

if(NOT STYIO_BUILD_VERSION MATCHES "^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$")
  message(FATAL_ERROR "STYIO_BUILD_VERSION must be numeric major.minor.patch without leading zeros")
endif()
string(REPLACE "." ";" _styio_version_components "${STYIO_BUILD_VERSION}")
foreach(_styio_component IN LISTS _styio_version_components)
  string(LENGTH "${_styio_component}" _styio_component_length)
  if(_styio_component_length GREATER 5 OR _styio_component GREATER 65535)
    message(FATAL_ERROR "STYIO_BUILD_VERSION components must be between 0 and 65535")
  endif()
endforeach()
unset(_styio_version_components)
unset(_styio_component)
unset(_styio_component_length)

if(NOT STYIO_FULL_RELEASE_CHANNEL MATCHES "^[A-Za-z0-9][A-Za-z0-9._-]*$")
  message(FATAL_ERROR "STYIO_FULL_RELEASE_CHANNEL must be a nonempty safe identifier (letters, digits, dots, underscores, hyphens)")
endif()
