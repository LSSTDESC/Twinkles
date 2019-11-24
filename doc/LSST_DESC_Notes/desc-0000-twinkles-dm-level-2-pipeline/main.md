![](./texmf/logos/header.png)

# The Twinkles Emulated DM Level 2 Pipeline and Results

*Simon Krughoff, Tony Johnson, Brian Van Klaveren, Phil Marshall and others*

We describe the Twinkles emulation of the expected LSST Data Management Level 2 image processing pipeline. The workflow has two branches, for image coaddition, Source characterization and ForcedSource measurement, and in parallel, for template image generation, image differencing, DIASource characterization and DIAObject measurement. We introduce our 'cookbook' of markdown format 'recipes' for each stage in this pipeline, and describe our implementation of it using the SLAC Workflow Engine at NERSC. On the Cori Haswell partition we were able to process XX images in XXX CPU hours at XX% efficiciency, and discuss prospects for future data challenges.

This Note was generated on: |date|


## Introduction

Twinkles is a pathfinder project, to carry out a small end-to-end test of a DESC analysis of LSST data. During LSST operations, we expect to use LSST data catalog products to do cosmology, investigating the systematic errors present in those data using our own simulated images. These images will need to be processed in exactly the same way as the LSST images were, in order for us to be able to interpret the catalogs accurately, which means that the DESC will need to maintain and operate its own emulation of the LSST DM pipeline. In this Note we describe the first version of this emulated pipeline, assembled for the Twinkles 1 project, and investigate its performance at NERSC on the Twinkles 1 images.

The science goals of Twinkles 1 are to understand the error properties of the LSST-measured light curves of type Ia supernovae and strongly lensed quasars, such that they can be simulated at much larger scale using simple catalog-level approximations. These larger simulations will be used for sensitive tests of detection, classification and light curve measurement. The multi-purpose nature of the intended application of the Twinkles results means that we need the DM pipeline to return a realistically wide variety of measurements. For light curve measurement we require forced photometry of DIAObjects; for the blended lensed quasars, we are also interested in the measurements of flux, position and second moments of the DIASources. Detection and classification of both supernovae and lensed quasars is likely to be enhanced by the measurements of Objects ad Sources characterized during the static sky analysis; forced photometry on the Objects is also of interest. 

The above considerations lead us to focus on emulation of the Annual Data Release Processing (DRP), including re-processing of the prompt difference imaging analysis images to make refined DIAObject light curves. Since detection and classification is only a secondary goal in Twinkles 1, we do not emulate the prompt, "Level 1" processing; in Twinkles 1 and in this Note we focus on the "Level 2" DRP, including DIA image re-processing. This gives rise to a pipeline with two parallel branches, which can be used to produce a "data release" set of catalogs:

1. **Image Coaddition and Object Characterization**. Visit images from years 1 through K are combined to make a Coadd image, and CoaddSources detected. These are used to build an Object table. ForcedSources are then measured in every visit image at the Object positions.

2. **Image Differencing and DIA Source/Object Characterization**. Visit images from years 1 through (K-1) are combined to make a good seeing template image. Visit images from year K are then difference with that template, and DIASources detected. These are associated (clustered) into DIAObjects. ForcedDIASources are then measured in every visit difference image at the DIAObject positions.

The LSST DM Stack tasks used in this branched pipeline are described in the Twinkles "cookbook", introduced in Section 2 below. The tasks themselves are run by a workflow engine, introduced in Section 3. Results from processing the Twinkles 1 images at NERSC are presented in Section 4. We provide some discussion of these results in Section 5 before concluding.


## The Twinkles DM Cookbook

The details of the DM stack processing steps are contained in a set of markdown-format "cookbook recipes," as follows:

### [Static Sky Analysis](https://github.com/LSSTDESC/Twinkles/blob/master/doc/Cookbook/DM_Level2_Recipe.md)

### [Level 1 Difference Imaging Analysis](https://github.com/LSSTDESC/Twinkles/blob/master/doc/Cookbook/Coadd_Diffim_Recipe.md)

### [Level 2 DIA Reprocessing](https://github.com/LSSTDESC/Twinkles/blob/master/doc/Cookbook/Reprocessed_DIAObjects_Recipe.md)


## DM Level 2 Processing with the SLAC Workflow Engine

Tony: Brief notes on SLAC workflow engine, w/references. Basics of implementation. Flow diagram. Internal methodology: Simon wrote cookbook recipes, Tony translated their steps into workflow engine scripts.

Brian: Operating at NERSC, what did it take?

## Results

Tony: Throughput. Success rate. Remaining bugs.

Tony: Efficiency: wallclock vs CPU time.

Tony: Plots!


## Discussion and Conclusions

Simon: Overall success of pipeline as implemented.

Simon: Deficiencies of pipeline - what's missing? Amp images (Twinkles 2), full focal plane. Additional measurements?

Tony: Memory useage. Implications for KNL.



-----


## Appendix: LSST DESC Notes `Markdown` Reference

You can delete all of this whenever you're ready.

## Introduction

This is a template [`Markdown`](https://github.com/adam-p/Markdown-here/wiki/Markdown-Cheatsheet) LSST DESC Note, for you to adapt for
your own work.

## Sectioning

As you can see above, your content can easily be divided into sections.
You can also make subsections, as follows.

### A Subsection

You can even have subsubsections, like this:

#### A Subsubsection

See? This is a subsubsection.

#### Another Subsubsection

And so is this.

### Another Subsection

And so on.

Math
----

You can typeset mathematics using latex commands like this:

$$\langle f(k) \rangle = \frac{ \sum_{t=0}^{N}f(t,k) }{N}$$

While this does not render on GitHub, it should get [picked up by
Sphinx](http://www.sphinx-doc.org/en/stable/ext/math.html) later and
will be available for you to re-use in future latex documents.

Code
----

You can show code in blocks like this:

```python
print "Hello World"
```

or this:

```bash
echo "Hello World"
```

Inline mentions of code `objects` can be made using pairs of backquotes.

## Figures

To add figures, add the required image file (PNG, SVG or JPG preferred)
to the `figures` subdirectory in your Note's folder. Here's an example:

![](./figures/example.jpg)
This is the figure caption: above we have the LSST DESC logo, in JPG format.

And then the text continues. Note that GitHub ignores the image sizing
commands when presenting [`Markdown`](https://github.com/adam-p/Markdown-here/wiki/Markdown-Cheatsheet) format documents; Sphinx might not.

## Tables

Tables can be fiddly in [`Markdown`](https://github.com/adam-p/Markdown-here/wiki/Markdown-Cheatsheet). A good place to start is an online table generator like [this one](http://www.tablesgenerator.com/Markdown_tables). Then, you'll need some patience. For more on table formatting, see the [`Markdown` cheat-sheet](https://github.com/adam-p/Markdown-here/wiki/Markdown-Cheatsheet#tables).

|   A   |   B   |      C         |  D  |
|:-----:|:-----:|:--------------:|:---:|
| (deg) | (kpc) | ($M_{\odot}$)  |     |
|  0.4  |  3.4  |  $10^{12.2}$   | R,S |
|  9.6  |  8.2  |  $10^{10.4}$   |  S  |


## References

You can cite papers (or anything else) by providing hyperlinks. For
example, you might have been impressed by the DESC White Paper [(LSST
Dark Energy Science Collaboration
2012)](http://arxiv.org/abs/1211.0310). It should be possible to convert
these links to latex citations automatically later.

## Further Resources

For a guide to writing `Markdown` documents, check out this [useful little cheatsheet](https://github.com/adam-p/Markdown-here/wiki/Markdown-Cheatsheet).
