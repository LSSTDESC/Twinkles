# Recipe: Emulating the Level 1 Reprocessing of DIAObjects: Difference Image Forced Photometry

## Purpose
This recipe suggests a reasonable first step towards creating `DIAObjects` complete with `DIASources` that have appropriately flagged forced photometry, starting from the `DIASource` output from the PSF-homogenized coadd diffim
procedure, described [here](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/doc/Cookbook/CoaddDiffim_Recipe.md).

The following steps, to be discussed further below, are:

1. Assemble `DIAObjects` from `DIASources`
2. Calculate aggregate quantities for `DIAObjects` based on the constituent `DIASources`
3. Feed the `DIAObjects` to a difference image forced photometry task to compute light curves for each `DIAObject`, which can then be stored in a new `DIASource` table. 

This sequence of steps represents a minimal subset of those defined in the [LSST Data Products Definition Document, LSE-163](https://docushare.lsstcorp.org/docushare/dsweb/Get/LSE-163). 
In Twinkles 1 our goal is to emulate the production of cosmology-ready LSST supernova and lensed quasar light curves, and so we focus on the _Level 2 reprocessing of Level 1 difference images_.

## Nomenclature: Level 1 vs. Level 2
There will be processing of the difference image and associated `DIASources` in both prompt (Level 1) and static (Level 2) processing systems.  
The two systems operate quite differently.  
The main difference is that the Level 2 systems will have all data available at once, while the Level 1 system will be building `DIAObjects` on the fly and will have to retrieve data for further processing from persistent storage on a rolling basis.
Note that the Level 2 reprocessing of the (Level 1) image differences is not required to take place on an annual basis: reprocessed `DIAObjects` may be released less (but probably not more) frequently than that.

Let's review the DPDD outline for light curve measurement.

**Level 1:** 
`DIASources` are detected on a difference image.  Those `DIASources` are associated with existing `DIAObjects`.  
The `DIAObject` properties are updated and forced photometry is performed at the location of the updates position.  
If the `DIASource` does not associate with a `DIAObject`, a new `DIAObject` is formed and forced photometry is performed at that location in the current image and also the previous N-months of images at that location. 
("N" is nominally 1 month).

**Level 2:**
The Level 2 system can aggregate all the `DIASources` detected over the duration of the survey to date, constructing new, "reprocessed" `DIAObjects` all at once and then using those to feed a single pass of forced photometry at the locations of all these reprocessed `DIAObjects` over the duration of the survey to that point.  
We refer to this as the *Level 2 reprocessing* of the Level 1 data products.

In Twinkles 1 we emulate only this Level 2 reprocessing system.
The reasons for this are largely related to the I/O complexity of the Level 1 system.  
Each processing step would need to be able to pull images for forced photometry of past images.  
In addition, we would need to keep track of the rolling updates to `DIAObject` aggregate quantities.  
We will return to how we could emulate the Level 1 system in Twinkles 2.

## Emulating the Level 2 Reprocessing

### Associating `DIASources`
The two ways we looked at associating Level 1 `DIASources` into reprocessed `DIAObjects` were to:

* Collect `DIASources` into `DIAObjects` by doing a close neighbor match, in sequence, on each `DIASource` table, adding orphan `DIASources` back to the reference `DIAObject` catalog and thus building up a set of `DIAObjects` with member `DIASources`. Note that something like this online algorithm will need to be carried out in Level 1 during operations. 
* Use a clustering algorithm to do post-facto association based on the spatial distribution of all the `DIASources` simultaneously.

The second approach is likely closer to what will be done in the production Level 2 system, but the LSST DM Stack already contains a utility for executing the first technique.  
The `afwTable.MultiMatch` tool can take many `SourceCatalogs` and build up associations of the `DIASources` by repeated application of a proximity cut.  
We use this pre-existing tool as our first go at emulating Level 2 association.  
This will require a new `Task` to fetch the `DIASource` catalogs and feed them through `MultiMatch`.

### Aggregate quantities for `DIAObjects`
We will take the associated catalog from `MultiMatch` and compute aggregate quantities for the columns that impact the forced photometry:
i.e. positions, flags, and the total number of `DIASources` associated with the `DIAObject`. 
The aggregate quantites will be persisted in a new dataset `reproDIAObjects`.

### Forced Photometry
A new task will read the `reproDIAObjects` catalog.  
For each difference image, the task will force photometer at the location of each `reproDIAObject`.  
For each difference image, the task will store the forced photometry catalog in the `reproDIASource` dataset.

## Recipe
This section will be filled in as we implement the various pieces.  We need:

* A `diaObjectMaker.py` to make `diaObjects` from `diaSources`;
* A tool to add datasets to the `obs_lsstSim` dataset policy file;
* A task to execute the forced photometry;
* A `reproDIASource` dataset to persist the forced measurements in.
