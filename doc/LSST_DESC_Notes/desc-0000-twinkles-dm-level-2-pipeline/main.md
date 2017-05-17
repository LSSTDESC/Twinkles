![](./texmf/logos/header.png)

# The Twinkles Emulated DM Level 2 Pipeline and Results

*Simon Krughoff, Tony Johnson, Brian Van Klaveren and others*

We describe the Twinkles emulation of the expected LSST Data Management Level 2 image processing pipeline. The workflow has two branches, for image coaddition, Source characterization and ForcedSource measurement, and in parallel, for template image generation, image differencing, DIASource characterization and DIAObject measurement. We introduce our 'cookbook' of markdown format 'recipes' for each stage in this pipeline, and describe our implementation of it using the SLAC Workflow Engine at NERSC. On the Cori Haswell partition we were able to process XX images in XXX CPU hours at XX% efficiciency, and discuss prospects for future data challenges.

This Note was generated on: |date|


## Introduction

Phil & Simon: Overall Twinkles philosophy. Goals of Twinkles 1, implications for DM processing. Which measurements and why?

Phil & Simon: Annual release emulation. Level 1 vs Level 2, (prompt, DRP), "reprocessing." 

Phil & Simon: Approach to calculation: workflow engine, caveats; NERSC operation. Twinkles as pathfinder.


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
