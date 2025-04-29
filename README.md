# Darwin Core Data Package (DwC-DP)

This repository contains material to support the proposal for the Darwin Core Data Package (DwC-DP) model and format, and supports open discussion through [Issues](https://github.com/gbif/dwc-dp/issues).

When a version is ready to release, the schemas for DwC-DP should be copied to the [schema repository](https://rs.gbif.org/sandbox/experimental/data-packages/) for use by tools, such as the GBIF Integrated Publishing Toolkit (IPT).

The goal is for this repository to be transferred from GBIF to TDWG and for the Darwin Core Maintenance Group to maintain the resources, including schemas, if DwC-DP is ratified as a Vocabulary Enhancement to Darwin Core.

Maintenance Files:
**data-packages-validation-checks.py** - To check schema validation before pushing changes to the repository

**data-package-migration.py** - To bulk change schema identifiers and urls for new destinations.

**local_to_sandbox.sh** - To prepare schemas in the local repository for the rs.gbif.org sandbox.

**sandbox_to_local.sh** - To prepare schemas in the rs.gbif.org sandbox for the local repository.

# Conceptual Model
![Here should be the image of latest Darwin Core Data Package (DwC-DP) Conceptual Model](images/conceptual_model_2025-04-24.jpg "Darwin Core Data Package (DwC-DP) Conceptual Model")
Figure 1. Conceptual Model behind the Darwin Core Data Package (DwC-DP) showing the primary relationships between concepts. Clipped corner boxes indicate the Darwin Core Event class and extensions to it for Observations, MaterialGathering, Occurrences, OrganismInteractions, and Surveys. Agent, Protocol, Media, and Reference are classes that can be connected to other classes throughout the model (indicated by the "joins" in small rectangles, e.g., EventAgentRole). Specific instances of Identifiers and Assertions (dwc:MeasurementOrFacts) can be connected directly to other classes (e.g., EventAssertion). The Relationship class (dwc:ResourceRelationship) is provided to capture any relationship between instances of classes in the model that are not already explicitly defined, should that unexpected need arise.