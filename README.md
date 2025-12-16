# Data from published paper

DOI: 10.1038/s41467-025-59055-z

"Three-dimensional genome structures of single mammalian sperm"

Xu et al. 2025

    Accesion GEO: GSE276999

Down load TAR archive of human .3dg and .pairs files for all cells in scHiC analysis:

    wget "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE276999&format=file" -O GSE276999_RAW.tar

Unpack pairs data:

    mkdir -p steps/pairs
    tar -xvf GSE276999_RAW.tar --exclude='*3dg.txt.gz' -C ./steps/pairs/


Meta data sheet contains information about each cell, if it's X or Y-bearing sperm. 

---

This is how it looks after `workflow.py` has run.

```plaintext
(hic) [sojern@fe-open-01 human_sperm_haplo_seperated]$ cooler ls sperm_X.merged.mcool
sperm_X.merged.mcool::/resolutions/1000
sperm_X.merged.mcool::/resolutions/5000
sperm_X.merged.mcool::/resolutions/10000
sperm_X.merged.mcool::/resolutions/50000
sperm_X.merged.mcool::/resolutions/100000
sperm_X.merged.mcool::/resolutions/500000

(hic) [sojern@fe-open-01 human_sperm_haplo_seperated]$ cooler ls sperm_Y.merged.mcool
sperm_Y.merged.mcool::/resolutions/1000
sperm_Y.merged.mcool::/resolutions/5000
sperm_Y.merged.mcool::/resolutions/10000
sperm_Y.merged.mcool::/resolutions/50000
sperm_Y.merged.mcool::/resolutions/100000
sperm_Y.merged.mcool::/resolutions/500000

(hic) [sojern@fe-open-01 human_sperm_haplo_seperated]$ cooler info sperm_X.merged.mcool::/resolutions/1000
{
    "bin-size": 1000,
    "bin-type": "fixed",
    "creation-date": "2025-06-20T10:31:13.748340",
    "format": "HDF5::Cooler",
    "format-url": "https://github.com/open2c/cooler",
    "format-version": 3,
    "generated-by": "cooler-0.10.2",
    "genome-assembly": "GRCh38",
    "nbins": 3099848,
    "nchroms": 194,
    "nnz": 93745182,
    "storage-mode": "symmetric-upper",
    "sum": 94109833
}

(hic) [sojern@fe-open-01 human_sperm_haplo_seperated]$ cooler info sperm_Y.merged.mcool::/resolutions/1000
{
    "bin-size": 1000,
    "bin-type": "fixed",
    "creation-date": "2025-06-20T10:30:46.645659",
    "format": "HDF5::Cooler",
    "format-url": "https://github.com/open2c/cooler",
    "format-version": 3,
    "generated-by": "cooler-0.10.2",
    "genome-assembly": "GRCh38",
    "nbins": 3099848,
    "nchroms": 194,
    "nnz": 77537287,
    "storage-mode": "symmetric-upper",
    "sum": 77836378
}
```