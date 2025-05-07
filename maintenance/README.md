# DwC-DP Maintenance
Scripts in this folder are meant to be used to check various aspects of the data package and prepare the data package for use from the GBIF schema repository rs.gbif.org.

## Checks 
**all_fields_summary.py** - Script to make a CSV file with one entry for each field from the ./dwc-dp/0.1/table-schemas.

**check_dwc_consistency.py** - Script to check that the descriptions, comments, and examples in the local ./dwc-dp/0.1/table-schemas are the same as their corresponding terms in the canonical term_versions files in the TDWG GitHub repositories.

**check_table_consistency.py** - Script to check that the descriptions, comments, and examples in the local ./dwc-dp/0.1/table-schema files follow some consistent patterns.

**check_table_descriptions.py** - Script to check that the table descriptions in the local ./dwc-dp/0.1/index.json file are the same as the table descriptions in the table schema files in ./dwc-dp/0.1/table-schemas.

**data-packages-validation-checks-local.py** - Script to validate the data package locally to the extent possible - no calls to non-local resources.

**data-packages-validation-checks-sandbox.py** - Script to validate the sandbox version of the data package locally.

## Releases
When the local content of the data package schemas is released, the schemas for DwC-DP should be copied to the [schema repository](https://rs.gbif.org/sandbox/experimental/data-packages/) for use by tools, such as the GBIF Integrated Publishing Toolkit (IPT).

- 1. Prepare data package schemas.
- 2. Check data package locally (see [Checks](#checks)).
- 3. Update the data package version in ./dwc-dp/index.json
- 4. Create sandbox-ready data package.
  - **local_to_sandbox.sh** - Make a GBIF sandbox-ready data package in the ./sandbox folder.
- 5. Validate the data package in the local sandbox copy using the script **data-packages-validation-checks-sandbox.py**.
- 6. Clone rs.gbif.org repository or pull the lastest into an existing local copy
- 7. Make a release branch in the local copy of rs.gbif.org (e.g., `git checkout -b dwcdp-r0.1`). 
- 8. Copy sandbox-ready version of data package from this local repository to the new branch in the local copy of the rs.gbif.org repository.
- 9. Make any necessary amendments in this repository and repeat steps **iv** through **viii** until the rs.gbif.org version of the data package validates.
- 10. Commit, push and make a pull request for the changes in the new branch in the rs.gbif.org repository.
- 11. Commit and push the changes in this repository to GitHub.

## Future Plans
The eventual goal is for this repository to be transferred from GBIF to TDWG and for the Darwin Core Maintenance Group to maintain and serve these resources, including schemas, if DwC-DP is ratified as a Vocabulary Enhancement to Darwin Core.
