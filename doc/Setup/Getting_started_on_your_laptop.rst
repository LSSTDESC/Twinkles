################################
Getting Started on your Laptop
################################

Installation Notes
================================
The Twinkles package uses the LSST DM Stack's `afw` code, and also the LSST
Sims tools (among other things). Here's how to get everything working.

Get Anaconda Python
--------------------------------

Click [here](http://conda.pydata.org/miniconda.html) and download python 
2.7, if you don't have Anaconda python already.

```
bash ~/Downloads/Miniconda-latest-MacOSX-x86_64.sh
```
This installs miniconda into `${HOME}/miniconda2` by default. You should i
now pre-pend your `PATH` with `${HOME}/miniconda2/bin` so that this becomes
your default version of python.

Install the LSST DM Stack and LSST Sims Tools
--------------------------
These instructions come from the `LSST Science
Pipelines<https://pipelines.lsst.io/install/conda.html>`

These commands will download and activate the LSST Science Pipelines in a 
new Conda environment named "lsst":

.. code-block:: bash
      :linenos:

   conda config --add channels http://conda.lsst.codes/stack  
   conda create --name lsst python=2
   source activate lsst
   conda install lsst-distrib lsst-sims
   source eups-setups.sh


You are now set up to use the DM Stack in the current shell.

Environment Set up to Use LSST Code
-------------------------------------

.. code-block:: bash

   export LSST_DIR = ${HOME}/miniconda2
   set path = (${LSST_DIR}/bin $path)
   source activate lsst
   source eups-setups.sh
   setup obs_lsstSim
   setup lsst_sims

This needs to be done every time you start a new shell - so these lines 
could be worth adding to your `.bashrc` file or equivalent. Note that 
c-shell users can use `eups_setup.csh` and use `setenv` in their `.login` 
file.

Install Optional Python Modules Not Included with DMStack
----------------------------
.. code-block:: bash
    conda install nose
    conda install coverge
    conda install iminuit

