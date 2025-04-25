# Darwin Core Data Package (DwC-DP)

This repository contains material to support the proposal for the Darwin Core Data Package (DwC-DP) model and format, and supports open discussion through [Issues](https://github.com/gbif/dwc-dp/issues).

When a version is ready to release, the schemas for DwC-DP should be copied to the [schema repository](https://rs.gbif.org/sandbox/experimental/data-packages/) for use by tools, such as the GBIF Integrated Publishing Toolkit (IPT).

The goal is for this repository to be transferred from GBIF to TDWG and for the Darwin Core Maintenance Group to maintain the resources, including schemas, if DwC-DP is ratified as a Vocabulary Enhancement to Darwin Core.

Maintenance Files:
**data-packages-validation-checks.py** - To check schema validation before pushing changes to the repository

**data-package-migration.py** - To bulk change schema identifiers and urls for new destinations.

**local_to_sandbox.sh** - To prepare schemas in the local repository for the rs.gbif.org sandbox.

**sandbox_to_local.sh** - To prepare schemas in the rs.gbif.org sandbox for the local repository.
