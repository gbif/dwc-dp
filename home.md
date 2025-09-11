---
layout: home
title: Darwin Core Review
description: Proposed Conceptual Model, Data Package guide, and term changes
permalink: /
toc: true
---

## Introduction

{:.lead}
The members of the [Darwin Core Maintenance Group](https://www.tdwg.org/community/dwc/) would like to welcome you to the **public review for the set of proposed changes to Darwin Core** described below. The proposed changes are developed to support richer, more complex types of biodiversity data than what is currently possible with a Darwin Core Archive.

This review is distinctive from previous maintenance reviews in that it includes many term changes and addition of documentation to the Darwin Core standard, hence the minimum review period is set to be a minimum of 90 days rather than the customary minimum 30 days.

Below you will find a summary of the proposals under review and the relevant links to participate in this community process.

{:.alert .alert-info}
Your comments are welcome and important for the evolution of the Darwin Core standard. [See below](#participate) how you can participate.

## What is under review?

This is not a proposal for a new standard. Instead, this proposal contains material for a [Vocabulary Enhancement](https://github.com/tdwg/vocab/blob/master/vms/maintenance-specification.md#4-vocabulary-enhancements) of the existing [Darwin Core](https://dwc.tdwg.org/) standard. Under consideration are **three items** (see Figure 1):

     In addition to clarifying the semantics of Darwin Core terms, these changes support for the implementation of the <a href ="https://gbif.github.io/dwc-dp/qrg/"  target="_blank">Darwin Core Data Package Publishing Model</a> (DwC-DP), which is an implementation of the [Darwin Core Conceptual Model](#darwin-core-conceptual-model) following the specifications found in the [Darwin Core Data Package Guide](#darwin-core-data-package-guide).
1. [**Darwin Core Conceptual Model**](#cm): a new specification for a non-normative "semantic layer" for Darwin Core.

2. [**Darwin Core Data Package guide**](#dp): a new specification for creating Darwin Core datasets as Frictionless Data Packages. It is one implementation of the conceptual model.

3. [**Changes to Darwin Core terms**](#term-changes): proposals for new terms and changes to existing terms, mainly to clarify semantics and support the above.

[![Here should be a schematic of the Darwin Core review](images/dwc_review_schematic.png "Darwin Core Review")](images/dwc_review_schematic.png)
_Figure 1: Overview of the public review that includes the Darwin Core Conceptual Model, the Darwin Core Data Package guide, and proposals for new and changes to existing Darwin Core terms._

{:id="cm"}
### Darwin Core Conceptual Model

[Explore the model](cm/){:.btn .btn-primary}

The **Darwin Core Conceptual Model (DwC-CM)** provides a high‑level framework that describes explicit relationships between Darwin Core classes in typical biodiversity information workflows. DwC-CM is a synthesis of years of discussion and contributions to Biodiversity Information Standards (TDWG) Interest Groups. The synthesis arose during research towards [“Diversifying the GBIF Data Model”](https://www.gbif.org/new-data-model), which brought additional perspectives from the GBIF community and included a series of iterative approaches to refine and validate both a conceptual model and a data publishing model through a wide variety of biodiversity data use cases. Data structures of many operational systems, including all commonly used open source collection management systems, have been studied and have influenced this model.

{:id="dp"}
### Darwin Core Data Package guide

[Read the guide](dp/){:.btn .btn-primary}

The **Darwin Core Data Package guide** is a specification for creating “Darwin Core Data Packages” (DwC-DP): an exchange format for biodiversity data. It extends the [Data Package specification](https://specs.frictionlessdata.io/) (developed by Frictionless Data) as an implementation for the Darwin Core Conceptual Model. It is similar in purpose to the [Darwin Core Text guide](https://dwc.tdwg.org/text/), which is a specification for Darwin Core Archives.

The Darwin Core Data Package guide references a [DwC-DP profile](dp/#32-package-level-properties) and [table schemas](dp/#dwc-dp-tables), but these are not part of the public review, because the standard does not include those implementation schemas. Nevertheless, it is extremely useful for understanding how the Conceptual Model and Data Package specification would be put into practice. It is the application of the theory.

{:id="term-changes"}
### Changes to Darwin Core terms

[See suggested changes](https://github.com/tdwg/dwc/milestone/20){:.btn .btn-primary}
[Explore all classes and terms](qrg/){:.btn .btn-outline-primary}

#### New classes and properties

To enable an implementation of a Darwin Core Data Package as a new publishing model, new terms are added in Darwin Core. These include new classes and new properties in those classes. New classes are described below. To explore all classes and their properties in detail, see the <a href="https://gbif.github.io/dwc-dp/qrg/" target="_blank">Darwin Core Data Package - Quick Reference Guide</a>.

**Agent** - A person, group, organization or other entity that can act.

**BibliographicResource** - A book, article, or other documentary resource.

**Media** - A `dcmi:MediaType` (`dcmi:Sounds`, `dcmi:StillImages`, `dcmi:MovingImages` or `dcmi:Text`) with other entities as content. This class accommodates metadata about media from the <a href="https://ac.tdwg.org/" target="_blank">Audiovisual Core</a> standard.

**MolecularProtocol** - A protocol used to derive and identify a nucleotide sequence from a `dwc:MaterialEntity`. This class accommodates the <a href="https://rs.gbif.org/extension/gbif/1.0/dna_derived_data_2024-07-11.xml" target="_blank">DNA derived data extension</a>.

**NucleotideAnalysis** - A link between a NucleotideSequence and a `dwc:Event` and a `dwc:MaterialEntity` from which it was derived, using a specified Protocol.

**NucleotideSequence** - A digital representation of a nucleotide sequence.

**OrganismInteraction** - An interaction between two `dwc:Organisms` during a `dwc:Event`.

**Protocol** - A method used during an action.

**Provenance** - Information about an entity’s origins.

**Survey** - A biotic survey or inventory. This class accommodates the <a href="https://eco.tdwg.org/" target="_blank">Humboldt Extension for Ecological Inventories</a>.

**SurveyTarget** - A specification of a characteristic of a `dwc:Occurrence` that was included or excluded in a Survey. This class accommodates and extended the Scope aspects of the <a href="https://eco.tdwg.org/" target="_blank">Humboldt Extension for Ecological Inventories</a>.

**UsagePolicy** - Information about rights, usage, and attribution statements applicable to an entity.

#### Changes to existing classes and properties

The semantics embodied in the <a href="https://gbif.github.io/dwc-dp/cm/" target="_blank">Darwin Core Conceptual Model</a>, and their implementation through the <a href="https://gbif.github.io/dwc-dp/qrg/" target="_blank">Darwin Core Data Package publishing model</a>, clarify many of the ambiguities that existed in Darwin Core previously. Changes needed to mitigate these ambiguities include assigning existing properties to different classes, adding new properties to existing Darwin Core classes and 
improving definitions, usage comments and examples of existing Darwin Core terms (both classes and properties).

##### Occurrence

One of the most fundamental advances of the Semantic Layer, reflected in the DwC-DP publishing model, is the disambiguation of the `dwc:Occurrence` class. Previously, in practice, a `dwc:Occurrence` was a catch-all for information in support of the existence of a `dwc:Organism` at a place and time. Under DwC-CM, a `dwc:Occurrence` is "A state of a `dwc:Organism` in a `dwc:Event`." Thus, material evidence, though it can support the validity of a `dwc:Occurrence`, does not consist of properties of the Occurrence. Instead, all of the ephemeral characteristics of the state of an Organism are properties of a `dwc:Occurrence` while the permanent characteristics remain properties of the Organism. In short, the `dwc:Occurrence` now consists of the changeable things about a `dwc:Organism` at a given place and time that were observed or inferred.

{:id="participate"}
## Participating in the review

To understand how to participate in the review process, please refer to <a href="https://github.com/tdwg/dwc/wiki/Darwin-Core-Maintenance-Frequently-Asked-Questions" target="_blank">Darwin Core Maintenance Frequently Asked Questions</a>, which provides information on the review process and the maintenance of the Darwin Core standard in general.

Here you can review the <a href="https://gbif.github.io/dwc-dp/cm/" target="_blank">Darwin Core Conceptual Model</a>. This is **a document** describing the conceptual model, seeking ratification. It goes hand in hand with the changes and new terms proposed. To comment on those, see below.

Here you can review the <a href="https://gbif.github.io/dwc-dp/dp/">Darwin Core Data Package Guide</a>. This is **a document** describing a specification for implementing Darwin Core Data Packages, seeking ratification. This document is independent of the Conceptual Model and of the term changes and additions.
## Who's behind this?

This proposal was developed by representives from the [Darwin Core Maintenance Group](https://www.tdwg.org/community/dwc/) and the [Global Biodiversity Information Facility (GBIF)](http://www.gbif.org), using numerous use cases submitted by third parties.

Here you can review the <a href="https://github.com/tdwg/dwc/milestone/20" target="_blank">List of term additions and changes proposal</a>. You may comment on each term, as we normally do for Darwin Core enhancements (refer to the <a href="https://github.com/tdwg/dwc/wiki/Darwin-Core-Maintenance-Frequently-Asked-Questions" target="_blank">FAQs</a> above for guidance).
The proposal is the result of an iterative and open approach. Whether you were involved in this process or not, everyone has a chance to review.

In addition, there are relevant resources closely related and recommended reading:
- <a href="https://dwc.tdwg.org/terms/" target="_blank">Darwin Core Quick Reference Guide</a> (Darwin Core term definitions). Note that this document DOES NOT contain the proposed changes, it will only incorporate them if they are ratified.
- <a href="https://gbif.github.io/dwc-dp/qrg/" target="_blank">Darwin Core Data Package Quick Reference Guide</a> (contextual term definitions for tables and fields for a Darwin Core Data Package implementation of DwC-CM).
- <a href="https://gbif.github.io/dwc-dp/explorer/" target="_blank">Darwin Core Data Package Relationship Explorer</a> (tool to visualize and explore the relationships implemented in the Darwin Core Data Package).
Information about efforts related to the development of this proposal can be found in the [Darwin Core Data Package (DwC-DP) Implementation Experience and Feature Report](docs/dwc_dp_implementation_feature_reports.pdf).
