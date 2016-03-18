#!/bin/tcsh

set vb = 0

if ($?TWINKLES_DIR) then

    if $vb echo "Twinkles environment variable TWINKLES_DIR is already set to value '${TWINKLES_DIR}'"

else

    # The following doesn't work in all situations, most notably when
    #   source <twinkles directory>/setup/setup.csh
    # is included in your .cshrc file.
    # If the setup script is just being sourced from within the Twinkles directory
    # then it's fine. To run this setup in every shell, you need to add
    #   setenv TWINKLES_DIR <twinkles directory>
    # to your .login

    set sourced = ($_)
    if $vb echo "Variable sourced has value '$sourced' and $#sourced elements"

    set setup_dir = `dirname $sourced[2]`
    if $vb echo "Variable setup_dir has value '$setup_dir' and $#setup_dir elements"

    if $vb then
        echo "Testing setup directory:"
        \ls ${setup_dir}
        \cd ${setup_dir}/.
        pwd -P
    endif

    set inst_dir = `\cd ${setup_dir}/.. ; pwd -P`
    if $vb echo "Variable inst_dir has value '${inst_dir}' and $#inst_dir elements"

    setenv TWINKLES_DIR ${inst_dir}
    if $vb echo "Twinkles environment variable TWINKLES_DIR set to value '${TWINKLES_DIR}'"

endif

setenv PYTHONPATH ${TWINKLES_DIR}/python:${PYTHONPATH}
if $vb echo "PYTHONPATH prepended as follows: $PYTHONPATH" | head
