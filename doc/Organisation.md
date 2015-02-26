# Data Generation and Analysis: Pipeline Design

Twinkles simulations must be reproducible - which means laying out a transparent, openly-accessible software pipeline which can be run by anyone. We can achieve this by developing several installations in parallel, for example at SLAC, NERSC and Fermilab, and maintaining various test examples that must always *just run*.

The flow chart below shows the initial pipeline design, color coded to show what remains to be built in red.

![The initial (Feb 2015) Twinkles flow chart](https://github.com/DarkEnergyScienceCollaboration/Twinkles/raw/master/doc/flowchart.png)

This confluence-hosted pipeline design chart is evolving with time [here](https://confluence.slac.stanford.edu/display/LSSTDESC/Twinkles+flow+chart). We'll update this page periodically with newer versions.

# Pipelined Machines

Notes on the various pieces of this pipeline are below, in approximate order of their operation.

## The Pointing Selector

## The Ditherer

## The Sprinkler

## The Light Curve Sampler

## The Twinkles CatSim

This machine generates the input that `PhoSim` needs, and can be based on the `sims_catutils` script, [`generatePhosimInput.py`](https://stash.lsstcorp.org/projects/SIM/repos/sims_catutils/browse/examples/generatePhosimInput.py). At present we have a modified version of this in the `twinkles` module, [here](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/twinkles/generatePhosimInput.py).


## The Analyzer



# Pipeline Infrastructure: the Workflow Engines


