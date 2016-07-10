##################################
Getting Started on an Apple Laptop
##################################

This page contains our notes on how to set your Mac laptop up to run the LSST DM stack and sims tools. 

.. contents::
   :depth: 4


DM Stack and Sims Installation
================================
The Twinkles package uses the LSST DM Stack's `afw` code, and also the LSST
Sims tools (among other things). Here's how to get everything working.

Get Anaconda Python
--------------------------------

Click `here <http://conda.pydata.org/miniconda.html>`_ and download python 
2.7, if you don't have Anaconda python already.

.. code-block:: bash

    bash ~/Downloads/Miniconda-latest-MacOSX-x86_64.sh

This installs miniconda into `${HOME}/miniconda2` by default. You should 
now pre-pend your `PATH` with `${HOME}/miniconda2/bin` so that this becomes
your default version of python.

Install the LSST DM Stack and LSST Sims Tools
---------------------------------------------
These instructions come from the `LSST Science
Pipelines <https://pipelines.lsst.io/install/conda.html>`_. The first thing that they recommend is to make sure `conda` is up to date:

.. code-block:: bash

   conda update conda

The following commands will download and activate the current release versions of the LSST Science Pipelines in a 
new Conda environment named "lsst". At various times they need to to type "`y`", so unfortunately you cannot leave them too long. They 
each take a few minutes, except for the `conda install`, which takes about an hour.  

.. code-block:: bash

   conda config --add channels http://conda.lsst.codes/stack  
   conda create --name lsst python=2
   
You are now ready to install the `lsst` software. 

If you are a C-shell user, the `source activate` command below
will not work, as that script only supports `bash` and `zsh`. A workaround is to switch to a `bash` shell at this point (by typing 
`bash`), and then stay in that `bash` shell to do the other two commands below. It's not really a workaround though - because you 
will have to come back to `bash` and re-do this environment set-up every time you want to use the LSST software anyway.

.. code-block:: bash

   source activate lsst
   conda install lsst-distrib lsst-sims
   source eups-setups.sh

You should now be set up to use the DM Stack in the current `bash` shell.

Set Up Environment to Use LSST Code
-----------------------------------
Every time you start a new shell, you need to set up its environment to enable use of the LSST code. The following lines could be 
worth adding to your `~/.bash_profile` file or equivalent.

.. code-block:: bash

   export LSST_DIR = ${HOME}/miniconda2
   set path = (${LSST_DIR}/bin $path)
   source ${LSST_DIR}/bin/activate lsst
   source eups-setups.sh
   setup obs_lsstSim
   setup lsst_sims

C-shell users: there doesn't seem to be a way round using `bash` when working with LSST software. Once you have added the above lines 
to a file called `~/.bash_profile`, you can make an alias that starts a login `bash` shell and executes this `~/.bash_profile`. In your 
`~/.cshrc` file, add:

.. code-block:: csh

    alias LSST "bash -l"
    echo "Type 'LSST' to set up the LSST environment"


Install Optional Python Modules Not Included with DMStack
----------------------------

.. code-block:: bash

    conda install nose
    conda install coverage
    conda install iminuit


Important DM Stack Installation Notes
-------------------------------------
- 2016 July 8
    The `12_0` released version of `sims_utils` is incompatible with the `astropy` 1.2.1.  You'll need to downgrade `astropy` after completing your DM Stack installation:

.. code-block:: bash

    conda install astropy=1.1.2

    
PhoSim Installation
================================
`PhoSim` is not distributed with the rest of the LSST sims tools, but is readily available as an independent package. 
The PhoSim confluence page is available `here <https://confluence.lsstcorp.org/display/PHOSIM>`_. The code is obtained 
from LSST via `git`, and needs the `cfitsio` and `fftw3` libraries: you'll be asked to point to their locations by the `PhoSim` 
configure script, or if you can't, it will offer to install them for you from source.
     
.. code-block:: bash

    mkdir ~/repos
    cd ~/repos
    git clone https://stash.lsstcorp.org/scm/sim/sims_phosim.git

This takes a few minutes, as the `sims_phosim` repo is large. Once it has been downloaded,
 
.. code-block:: bash

    cd sims_phosim
    setup cfitsio
    setup fftw
    ./configure
    make

You'll have to point to the correct cfitsio and fftw3 libraries and headers for your system.

Test `PhoSim`
---------------

.. code-block:: bash

    mkdir ~/TwinklesData
    cd ~/TwinklesData
    python $SIMS_CATUTILS_DIR/examples/generatePhosimInput.py
    ./phosim ~/TwinklesData/phoSim_example.txt --sensor="R22_S11" -c examples/nobackground

This produces a file `PhoSim` can run.
Images show up in the "output" directory.


Twinkles-specific Installation Notes
====================================
The notes above should be helpful for anyone looking to use either the Stack or the Sims tools, or both. We now turn to the 
additional code needed by the Twinkles project, to sprinkle in the twinkly objects.

Gravitational Lens Sprinkling Setup
---------------------------------------

#. Follow instructions above to setup DM Stack and LSST Sims

#. Install and setup `OM10 <https://github.com/drphilmarshall/OM10>`_.

#. Open an SSH tunnel for database connection to UW. See
`here <https://confluence.lsstcorp.org/display/SIM/Accessing+the+UW+CATSIM+Database>`_ for more information.
This is where the objects that will populate the catalog are stored.

#. You'll also need the OpSim sqlite repository from `this page <https://confluence.lsstcorp.org/display/SIM/OpSim+Datasets+for+Cadence+Workshop+LSST2015>`_

#. Now you're ready to go with:

.. code-block:: bash

    python generatePhosimInput.py


Supernova Sprinkling Setup
---------------------------
Coming soon!


