#!/bin/bash
# Shell Script to change the schema url locations from the rs.gbif.org sandbox to
# the gbif/dwc-dp GitHub repository.

# sh sandbox_to_dwcdp.sh

python data-package-migration.py ./dwc-dp/0.1 -u "http://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1" -U "https://github.com/gbif/dwc-dp/blob/master/dwc-dp/0.1"
python data-package-migration.py ./dwc-dp/0.1/table-schemas -u "http://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1" -U "https://github.com/gbif/dwc-dp/blob/master/dwc-dp/0.1"
