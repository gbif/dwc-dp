# Darwin Core Data Package (DwC-DP)

[Darwin Core Data Package - Quick Reference Guide](https://gbif.github.io/dwc-dp/qrg/dwc_dp_qrg.html)

This repository contains material to support a proposal for a [Vocabulary Enhancement](https://github.com/tdwg/vocab/blob/master/vms/maintenance-specification.md#4-vocabulary-enhancements) to the [Darwin Core](https://dwc.tdwg.org/) standard. The proposal for the enhancement is scheduled for full **public review beginning 2025-09-01**. The public review will include a [Darwin Core Conceptual Model](#darwin-core-conceptual-model) as a component of a long-awaited Semantic Layer for Darwin Core and a [Darwin Core Data Package (DwC-DP) Publishing Model](#darwin-core-data-package-dwc-dp-publishing-model) that supports sharing deeper and richer data than is possible with a [Darwin Core Archive](https://ipt.gbif.org/manual/en/ipt/latest/dwca-guide). The Semantic Layer will define the explicit relationships between the classes that are seen in DwC-DP and will be based on the understanding of biodiversity-related concepts accumulated in the analysis of myriad use cases during the theoretical Unified Model phase of the project [Diversifying the GBIF Data Model](https://www.gbif.org/new-data-model).

Previous to the public review, we welcome those who are interested to explore the [Darwin Core Data Package (DwC-DP) Publishing Model](#darwin-core-data-package-dwc-dp-publishing-model). This is an opportunity to **test the data publishing model with your real data**. To understand how you can do this, see the [Participating and Getting Help](#participating-and-getting-help) section, below. **This community testing phase will remain open until 2025-08-01**.

## Table of Contents
[Darwin Core Conceptual Model](#darwin-core-conceptual-model)

[Darwin Core Data Package (DwC-DP) Publishing Model](#darwin-core-data-package-dwc-dp-publishing-model)
- [Purpose](#purpose)
- [Structure](#structure)
- [Example Datasets](#example-datasets)

[Implications for Darwin Core](#implications-for-darwin-core)
- [New Classes and Properties](#new-classes-and-properties)
- [Changes to Existing Classes and Properties](#changes-to-existing-classes-and-properties)

[Participating and Getting Help](#participating-and-getting-help)

# Darwin Core Conceptual Model
![Here should be the image of latest Darwin Core Conceptual Model](images/conceptual_model_2025-05-03.png "Darwin Core Conceptual Model")
Figure 1. Conceptual Model behind the Darwin Core Data Package (DwC-DP) Publishing Model showing the primary relationships between key biodiversity-related concepts. Information is most commonly organized around Events. Clipped-corner, blue boxes indicate the Event class and extensions to it for different event types (Occurrences, OrganismInteractions, and Surveys). Other types of Events, such as Observation and MaterialGathering, can also be accommodated, but do not require a specific extension beyond the Event. Unclipped, green boxes represent additional classes. Of these, Agent, Media, Protocol, and Reference can be connected to other classes throughout the model (indicated by the "joins" in small, yellow rectangles, e.g., EventAgentRole). Specific kinds of Assertions (e.g., EventAssertion) and Identifiers (e.g., EventIdentifier) can be connected directly to other classes. The Relationship class is provided to capture any relationship between instances of classes in the model that are not already explicitly defined, should that unexpected need arise.

# Darwin Core Data Package (DwC-DP) Publishing Model
## Purpose
The data publishing model - the Darwin Core Data Package (DwC-DP) - based on a distillation of the [GBIF Unified Model](https://www.gbif.org/new-data-model), supports structured data beyond the restrictions of a [Darwin Core Archive](https://ipt.gbif.org/manual/en/ipt/latest/dwca-guide) star schema for a wide variety of new and traditional biodiversity data sources. The model fully supports datasets traditionally published as [Darwin Core Archives](https://ipt.gbif.org/manual/en/ipt/latest/dwca-guide) (observations and physical specimens, with extensions), but it goes far beyond, allowing richer data to be shared from these traditional datasets than was hitherto supported. Also, it empowers those who desire to share entirely new types of data (biotic surveys with inferred absence and abundance, hierarchical material entities, organism interactions, phylogenetic trees, and nucleotide analyses, among others) via Darwin Core. 

## Structure
The higher-level structure of Darwin Core Data Packages is based on the [Darwin Core Archive](https://ipt.gbif.org/manual/en/ipt/latest/dwca-guide) - they both encapsulate datasets in text files (CSV, TSV) with dataset metadata in an Ecological Markup Language (EML) document that can be packaged and delivered in a compressed archive file. The difference is in the extent to which the data within distinct classes can be stored and shared in distinct text files, and how these files relate to each other, which makes for the DwC-DP internal structure. Its [table schemas](dwc-dp/0.1/table-schemas) (tables, their fields, and relationships between them, defined in .json files) and [index](dwc-dp/0.1/index.json) (a table schema inventory, also in JSON), define this structure, of which the [Darwin Core Conceptual Model](#darwin-core-conceptual-model) provides a quick visual representation. The [table schemas](dwc-dp/0.1/table-schemas) contain the details of the fields, including names, labels, definitions, usage comments, examples, and constraints. The details of the relationships between tables are also in the table schemas, expressed as primary keys (unique identifiers within a table) and foreign keys (fields that contain the identifiers equal to the value of a primary key in another table).

The beauty of DwC-DP is that it is complicated only for those who want or need it to be, because there is no other way to faithfully capture the complexity of their data. Just as with Darwin Core Archives, a version of the GBIF Integrated Publishing Toolkit (IPT) in development can facilitate data structure mapping and produce Darwin Core Data Packages.

## Example Datasets
There is a separate GitHub repository ([gbif/dwc-dp-examples](https://github.com/gbif/dwc-dp-examples)) in which we have been accumulating examples of real datasets mapped to DwC-DP. That repository contains a representation of the DwC-DP as a [database schema](https://github.com/gbif/dwc-dp-examples/blob/master/gbif/dwc_dp_schema.sql) that can be populated with data mapped to DwC-DP and checked for data integrity.

# Implications for Darwin Core
Including the Darwin Core Data Package as a vocabulary enhancement to the Darwin Core standard implies several changes in the standard, including adding terms, modifying existing terms, and providing new documentation accordingly. Two new normative documents will be needed. The first will be a document describing in detail the Darwin Core Semantic Layer, including the [Darwin Core Conceptual Model](#darwin-core-conceptual-model), of which the DwC-DP is an implementation. The second document will be a "Darwin Core Data Package Guide". Much like the [Darwin Core Text Guide](https://dwc.tdwg.org/text/), this second document will describe the requirements for the structure of Darwin Core as a Data Package.

## New Classes and Properties
To enable the Darwin Core Data Package, new terms will have to be added. These include new classes and new properties in those classes. New classes are described below. To explore all classes and their properties in detail, see the [Darwin Core Data Package - Quick Reference Guide](https://gbif.github.io/dwc-dp/qrg/dwc_dp_qrg.html).

### New Classes
**Agent** - A person, group, organization or other entity that can act.

**Collection** - A persistent formal repository in which dwc:MaterialEntities and/or Media are preserved.

**IdentificationTaxon** - A construct of components and positions of dwc:scientificNames in a dwc:Identification.

**Media** - A dcmi:MediaType (dcmi:Sounds, dcmi:StillImages, dcmi:MovingImages or dcmi:Text) with other entities as content. This class accommodates metadata about media from the [Audiovisual Core](https://ac.tdwg.org/) standard.

**MolecularProtocol** - A protocol used to derive and identify a nucleotide sequence from a dwc:MaterialEntity. This class accommodates the [DNA derived data](https://rs.gbif.org/extension/gbif/1.0/dna_derived_data_2024-07-11.xml) Extension.

**NucleotideAnalysis** - A link between a NucleotideSequence and a dwc:Event and a dwc:MaterialEntity from which it was derived, using a specified Protocol.

**NucleotideSequence** - A digital representation of a nucleotide sequence.

**OrganismInteraction** - An interaction between two dwc:Organisms during a dwc:Event.

**PhylogeneticTree** - A branching diagram that shows the evolutionary relationships between dwc:Organisms.

**PhylogeneticTreeTip** - A group of Taxa at the end of a branch of a PhylogeneticTree as determined from relationships between dwc:Organisms.

**Protocol** - A method used during an action.

**Reference** - A bibliographic reference in which an entity is mentioned.

**Survey** - A biotic survey. This class accommodates the [Humboldt Extension for Ecological Inventories](https://eco.tdwg.org/).

**SurveyTarget** - A specification of a characteristic of a dwc:Occurrence that was included or excluded in a Survey. This class accommodates and extended the Scope aspects of the [Humboldt Extension for Ecological Inventories](https://eco.tdwg.org/).

## Changes to Existing Classes and Properties
The Darwin Core Data Package, backed by the semantics embodied in the [Darwin Core Conceptual Model](#darwin-core-conceptual-model), clarifies many of the ambiguities that existed in Darwin Core previously. Some of these ambiguities are mitigated by assigning existing properties to different classes. Other clarifications are made by adding new properties to existing Darwin Core classes and improving definitions, usage comments and examples of existing Darwin Core terms (classes and properties).

### Occurrence
One of the most fundamental advances of the Semantic Layer, reflected in the DwC-DP publishing model, is the disambiguation of the dwc:Occurrence class. Previously, in practice, a dwc:Occurrence was a catch-all for information in support of the existence of a dwc:Organism at a place and time. Under DwC-DP, a dwc:Occurrence is "A state of a dwc:Organism in a dwc:Event." Thus, the material evidence, though it can support the validity of a dwc:Occurrence, is not a property of the Occurrence. Instead, all of the ephemeral characteristics of the state of an Organism are properties of a dwc:Occurrence. In short, the dwc:Occurrence now clearly consists of the things about a dwc:Organism at a given place and time that were observed or inferred.

# Participating and Getting Help
In anticipation of a formal public review, scheduled to begin 2025-09-01, we would like to invite people to gain familiarity with and test the DwC-DP by attempting to map original datasets to it. We are just beginning to work on the "Darwin Core Data Package Guide", which is intended to contain various "recipes" for publishing different types of datasets. Until that document contains useful content, the best way forward is to look at an already-mapped example dataset that is similar to the one you want to test ([gbif/dwc-dp-examples](https://github.com/gbif/dwc-dp-examples)). This community testing phase will remain open until 2025-08-01.

- **Getting started** - The easiest way to start to understand DwC-DP is to look at the [Darwin Core Data Package - Quick Reference Guide](https://gbif.github.io/dwc-dp/qrg/dwc_dp_qrg.html).

- **Mapping datasets to DwC-DP** - If you need help getting started with mapping a dataset to DwC-DP, feel free to contact [John Wieczorek](mailto:gtuco.btuco@gmail.com).

- **Discussion** - For open discussion on the Darwin Core Data Package, see the GBIF [Darwin Core Data Package (DwC-DP) discourse forum topic](https://discourse.gbif.org/t/darwin-core-data-package-dwc-dp/5937).

- **Issues** - To share an issue encountered while trying to map a dataset, feel free to open an [Issue](https://github.com/gbif/dwc-dp/issues) in this repository.