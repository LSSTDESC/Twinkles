# Reprocessing DIAObjects for Difference Image Forced Photometry

## Purpose
This cookbook intends to suggest a reasonable first step recipe for using the `DIASource` output from the PSF homogenized coadd diffim
procedure, described [here](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/doc/Cookbook/CoaddDiffim.md), to create
`DIAObjects` suitable for creating lightcurves using difference measurement.  The following steps, to be discussed further below, are:</br>
1. Assemble `DIAObjects` from `DIASources`</br>
2. Calculate aggregate quantities for `DIAObjects` based on the constituent `DIASources`</br>
3. Feed the `DIAObjects` to a difference image forced photometry task to compute light curves for each `DIAObject`</br>

## Nomenclature: Level 1 vs. Level 2
There will be processing of the difference image and associated `DIASources` in both prompt (Level 1) and static (Level 2) processing
systems.  The two systems operate quite differently.  The main difference is that the Level 2 systems will have all data available at once
while the Level 1 system will be building `DIAObjects` on the fly and will have to retrieve data for further processing from persistent
storage on a rolling basis.
### Level 1
`DIASources` are detected on a difference images.  Those `DIASources` are associated with existing `DIAObjects`.  The `DIAObject` properties
are updated and forced photometry is performed at the location of the updates position.  If the `DIASource` does not associate with a
`DIAObject`, a new `DIAObject` is formed and forced photometry is performed at that location as well as the previous N-months of images at
that location (nominally 1 month).
### Level 2
The Level 2 system can take the aggregate of all `DIASources` detected over the duration of the survey.  It can then construct the `DIAObjects`
all at once and then use those to feed a single pass of forced photometry at the locations of all `DIAObjects` over the duration of the survey
to that point.  We refer to this as the *Level 2 reprocessing* of the Level 1 data products.

We are initially going to emulate the Level 2 reprocessing system.  The reasons for this are largely related to the I/O complexity of the
Level 1 system.  Each processing step would need to be able to pull images for forced photometry of past images.  In addition, we would
need to keep track of the rolling updates to `DIAObject` aggregate quantities.  We will look at how we could emulate the Level 1 system
in Twinkles 2.

## Emulating the Level 2 Reprocessing
### Associating `DIASources`
The two ways we looked at associating `DIASources` into `DIAObjects` were to:
* Collect `DIASources` into `DIAObject` by doing a close neighbor matching in sequence on each `DIASoure` table adding orphan 
`DIASources` back to the reference catalog thus building up a set of `DIAObjects` with member `DIASources`.
* Use a clustering algorithm to do post-facto association based on the spatial distribution of all the `DIASources` simultaneously.

The second approach is likely closer to what we will do in the production Level 2 system, but we have a utility already in place for
executing the the first technique.  The `afwTable.MultiMatch` tool can take many `SourceCatalogs` and build up associations of the
by repeated application of a proximity cut.  We will use this pre-existing tool as our first go at emulating Level 2 association.  This
will require a new `Task` to fetch the `DIASource` catalogs and feed them through `MultiMatch`.

### Aggregate quantities for `DIAObjects`
We will take the associated catalog from `MultiMatch` and compute aggregate quantities for the columns that impact the forced photometry:
i.e. positions, flags and total number of `DIASources` associated with the `DIAObject`.  The aggregate quantites will be persisted in a
new dataset `reproDIAObjects`.

### Forced Photometry
A new task will read the `reproDIAObjects` catalog.  For each difference image, the task will force photometer at the location of each
`reproDIAObject`.  For each difference image, the task will store the forced photometry catalog in the `forcedDIASource` dataset.

## Recipe
This section will be filled in as we implement the various pieces.  We need:
* `diaObjectMaker.py` to make `diaObjects` from `diaSources`
* Add datasets to the `obs_lsstSim` dataset policy file
* A task to execute the forced photometry
* `forcedDIASource` dataset to persist the forced measurements
