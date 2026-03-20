# DwC-DP Maintenance
## Preparing new release
To prepare a new release of the Darwin Core Data Package
- Pull from master. Create a new release branch
- [Update the canonical source files](#canonical_source_files)
- [Generate the table schemas](#generate_table_schemas)
- [Validate the table schemas](#validate_table_schemas)
- [Generate Quick Reference Guide](#generate_quick_reference_guide)
- [Generate PostgreSQL script](#generate_postgresql_script)
- [Prepare sandbox](#prepare_sandbox)
- [Push release](#push_release)

## Canonical source files
The source files to generate the Darwin Core Data Package artifacts are 
 - **vocabulary/dwc-dp-tables.csv** and
 - **vocabulary/dwc-dp-fields.csv**.

These two files are the canonical form of the table and field definitions, comments and examples for the Darwin Core Data Package. These are maintained manually.

## Generate table schemas
Use the script 
 - **maintenance/qrg/generate_qrg.py**

to generate the table schemas (**dwc-dp/table_schemas**) from the canonical source files. Run the script from the **maintenance/qrg** folder with a version parameter:
```
cd maintenance/qrg
python generate_qrg.py 0.1
```

## Validate table schemas
Use the script 
 - **maintenance/data-packages-validation-checks-local.py**

to validate the table schemas locally to the extent possible. This validation makes no calls to non-local resources.

## Generate Quick Reference Guide
Use the script 
 - **maintenance/qrg/generate_qrg.py**

to generate the Darwin Core Data Package Quick Reference Guide (**qrg/index.html**) in addition to the table schemas.

## Generate PostgreSQL script
Use the script 
 - **maintenance/sql/generate_sql.py**

to create an SQL script that generates a PostgreSQL database compliant with the table schemas. Additional configuration for the build is in  
- **maintenance/sql/generate_sql.yaml**

Run the script from the **maintenance/sql** folder:
```
python generate_sql.py --schemas ../../dwc-dp/table-schemas --config generate_sql.yaml --output generated_from_schemas.sql
```
## Prepare sandbox folder
Clone the **rs.gbif.org** repository or pull the lastest into an existing local copy. Make a release branch (e.g., `git checkout -b dwcdp-n.x`). Structural changes (tables and their relationships) should initiate a major release (e.g., 2.0), otherwise the release can be a minor one (e.g., 2.1).

Use the script 
 - **maintenance/local_to_sandbox.sh**

to make artifacts needed by GBIF in the **maintenance/sandbox** folder. 

Use the script 
 - **maintenance/data-packages-validation-checks-sandbox.py**

to validate the validate the sandbox artifacts locally.

Copy the validated artifacts in **maintenance/sandbox** to the new branch in the local copy of the **rs.gbif.org** repository.

## Push release
Commit, push and make a pull request for the changes in the new branch in the **rs.gbif.org** repository.
Commit, push and make a pull request for the release branch in this repository.

Once the pull request has been merged, test all published artifacts. When satisfied, create a release in GitHub.