##################################
Getting Started on an Apple Laptop
##################################

This page contains our notes on how to set your Mac laptop up to run the LSST DM stack and sims tools. 

.. contents::
   :depth: 4

Please check the "Important Installation Notes" to view current mitigations for known installation issues.

Installation
================================
The Twinkles package uses the LSST DM Stack's `afw` code, and also the LSST
Sims tools (among other things). Here's how to get everything working.

Get Anaconda Python
--------------------------------

Click `here <http://conda.pydata.org/miniconda.html>`_ and download python 
2.7, if you don't have Anaconda python already.

.. code-block:: bash

    bash ~/Downloads/Miniconda-latest-MacOSX-x86_64.sh

This installs miniconda into `${HOME}/miniconda2` by default. You should i
now pre-pend your `PATH` with `${HOME}/miniconda2/bin` so that this becomes
your default version of python.

Install the LSST DM Stack and LSST Sims Tools
---------------------------------------------
These instructions come from the `LSST Science
Pipelines <https://pipelines.lsst.io/install/conda.html>`_. The first thing that they recommend is to make sure `conda` is up to date:

.. code-block:: bash

   conda update conda

The following commands will download and activate the current release versions of the LSST Science Pipelines in a 
new Conda environment named "lsst":

.. code-block:: bash

   conda config --add channels http://conda.lsst.codes/stack  
   conda create --name lsst python=2
   source activate lsst
   conda install lsst-distrib lsst-sims
   source eups-setups.sh


You are now set up to use the DM Stack in the current shell.

Set Up Environment to Use LSST Code
-----------------------------------
Every time you start a new shell, you need to set up its environment to enable use of the LSST code. The following lines could be 
worth adding to your `.bashrc` file or equivalent.
C-shell users would use `eups_setup.csh` and `setenv` in their `.login` file.

.. code-block:: bash

   export LSST_DIR = ${HOME}/miniconda2
   set path = (${LSST_DIR}/bin $path)
   source activate lsst
   source eups-setups.sh
   setup obs_lsstSim
   setup lsst_sims


Install Optional Python Modules Not Included with DMStack
----------------------------

.. code-block:: bash

    conda install nose
    conda install coverge
    conda install iminuit
    
Install PhoSim
-----------------------
The PhoSim Confluence page is available `here <https://confluence.lsstcorp.org/display/PHOSIM>`_.
     
.. code-block:: bash

    mkdir ~/repos
    cd ~/repos
    git clone https://stash.lsstcorp.org/scm/sim/sims_phosim.git
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


Important Installation Notes
---------------
- 2016 July 8
    The 12_0 released version of sims_utils is incompatible with the astropy 1.2.1.  Users need to downgrade astropy after completing their DMStack installation.

.. code-block:: bash

    conda install astropy=1.1.2
