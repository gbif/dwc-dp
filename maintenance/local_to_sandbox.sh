#!/bin/bash
# Shell Script to make a copy of the local data package changing the schema url locations 
# from the gbif/dwc-dp GitHub repository to the sandbox in the rs.gbif.org repository.

# sh local_to_sandbox.sh

python data-package-migration.py -u "https://github.com/gbif/dwc-dp/blob/master/dwc-dp/0.1" -U "https://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1"
