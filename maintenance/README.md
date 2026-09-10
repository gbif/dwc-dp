# DwC-DP Maintenance
## Preparing a new version of the Darwin Core Data Package
- Pull the latest changes from this repository.
- From the latest version of the master branch, create a new working branch in which to capture all of the changes for a new version of the Data Package.
- [Update the canonical source files](#canonical_source_files).
- [Update Quick Reference template](#update_quick_reference_template).
- [Update SQL template](#update_sql_template).
- [Run process_dwcdp.py](#run_process_dwcdp_py).
- [Push version](#push_release).

## Canonical source files
The source files to generate the Darwin Core Data Package artifacts are as follow:
 - **vocabulary/dwc-dp-tables.csv**
 - **vocabulary/dwc-dp-fields.csv**

These two files are the canonical form of the table and field definitions, contextual usage notes and examples for the Darwin Core Data Package. These are maintained manually and updated here.

# Update Quick Reference Template
The file qrg_template.html is a configuration template for the Darwin Core Data Package Quick Reference Guide. Make any needed updates to this file before you [Run process_dwcdp.py](#run_process_dwcdp_py).

# Update SQL Template
The file generate_sql.yaml is a configuration template for the Darwin Core Data Package PostgreSQL Data Definition Language database schema generator. Make any needed updates to this file before you [Run process_dwcdp.py](#run_process_dwcdp_py).

## Run process_dwcdp.py
In the maintenance directory run the script process_dwcdp.py with a target version. For example:
 ```process_dwcdp.py http://rs.tdwg.org/dwc-dp/1.0-RC.1```

This generates and validates:
 - ../dwc-dp/dwc-dp-profile.json - the Darwin Core Data Package Profile
 - ../dwc-dp/table-schemas/*.json - the Darwin Core Data Package table schemas
 - ../qrg/index.html - the Darwin Core Data Package Quick Reference Guide
 - ../sql/dwc-dp.sql - a Darwin Core Data Package PostgreSQL DDL schema

## Push version
Commit and push changes in the new working branch to the remote repository.

Make a pull request for the new working branch on the remote repository.

Once the pull request has been merged, test all published artifacts.