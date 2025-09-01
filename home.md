---
layout: home
title: Darwin Core Review
description: Proposed Conceptual Model, Data Package Guide, and Term Changes
permalink: /
toc: true
---

The members of the <a href="https://www.tdwg.org/community/dwc/" target="_blank">Darwin Core Maintenance Group</a> would like to welcome you to the public review for the set of proposed changes to Darwin Core described below. 
This review is distinctive from previous maintenance reviews in that it includes many term changes and addition of documentation to the Darwin Core standard, hence the minimum review period is set to be a minimum of 90 days rather than the customary minimum 30-days.

Below you will find a summary of the proposals under review and the relevant links to participate in this community process.

Your comments are welcome and important for the evolution of the Darwin Core standard.

Thank you,

The Darwin Core Maintenance Team


This document contains material to support a proposal for a <a href="https://github.com/tdwg/vocab/blob/master/vms/maintenance-specification.md#4-vocabulary-enhancements" target="_blank">Vocabulary Enhancement</a> to the <a href="https://dwc.tdwg.org/" target="_blank">Darwin Core</a> standard. Under consideration are (see Figure 1):
  - **[Darwin Core Conceptual Model](#darwin-core-conceptual-model)** (DwC-CM, an informal "semantic layer" for Darwin Core), 
  - **[Darwin Core Data Package Guide](#darwin-core-data-package-guide)** (a specification for Darwin Core Data Package implementations),
  - **[Changes to Darwin Core Terms](#changes-to-darwin-core-terms):**
    - proposals for new terms 
    - proposals for changes to existing terms
    
     In addition to clarifying the semantics of Darwin Core terms, these changes support for the implementation of the <a href ="https://gbif.github.io/dwc-dp/qrg/"  target="_blank">Darwin Core Data Package Publishing Model</a> (DwC-DP), which is an implementation of the [Darwin Core Conceptual Model](#darwin-core-conceptual-model) following the specifications found in the [Darwin Core Data Package Guide](#darwin-core-data-package-guide).
  - NOTE: The Darwin Core Data Package Publishing Model itself is not part of public review, because the standard does not include implementation schemas. Nevertheless, it is extremely useful for understanding how the Conceptual Model and Data Package specification would be put into practice. It is the application of the theory.

Information about efforts related to the development of the DwC-CM, the DwC-DP Guide, and the DwC-DP Publishing Model can be found in the <a href="docs/dwc_dp_implementation_feature_reports.pdf" target="_blank">Darwin Core Data Package (DwC-DP) Implementation Experience and Feature Report</a>.

![Here should be the image of Darwin Core Conceptual Model Review Schematic](images/dwc_review_schematic.png "Darwin Core Review")
<p style="text-align:left;">Figure 1. Overview of the public review that includes the Darwin Core Conceptual Model (DwC-CM), the Darwin Core Data Package Guide, and proposals for new and changes to existing Darwin Core terms.</p>

## Darwin Core Conceptual Model

The <a href="https://gbif.github.io/dwc-dp/cm/" target="_blank">DwC-CM</a> provides a high‑level framework that describes explicit relationships between Darwin Core classes in typical biodiversity information workflows. DwC-CM is a synthesis of years of discussion and contributions to Biodiversity Information Standards (TDWG) Interest Groups. The synthesis arose during research towards <a href="https://www.gbif.org/new-data-model" target="_blank">"Diversifying the GBIF Data Model"</a>, which brought additional perspectives from the GBIF community and included a series of iterative approaches to refine and validate both a conceptual model and a data publishing model through a wide variety of biodiversity data use cases. Data structures of many operational systems, including all commonly used open source collection management systems, have been studied and have influenced this model. 

## Darwin Core Data Package Guide

The <a href="https://gbif.github.io/dwc-dp/dp/">Darwin Core Data Package Guide</a> is a specification of the requirements for a data package to be a Darwin Core Data Package. It is similar in purpose to the <a href="https://dwc.tdwg.org/text/" target="_blank">Darwin Core Text Guide</a>. Both describe specifications for data publishing models. The Darwin Core Data Package Guide is to a Darwin Core Data Package as the Darwin Core Text Guide is to a Darwin Core Archive.


## Changes to Darwin Core Terms

### New Classes and Properties
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

### Changes to Existing Classes and Properties

The semantics embodied in the <a href="https://gbif.github.io/dwc-dp/cm/" target="_blank">Darwin Core Conceptual Model</a>, and their implementation through the <a href="https://gbif.github.io/dwc-dp/qrg/" target="_blank">Darwin Core Data Package publishing model</a>, clarify many of the ambiguities that existed in Darwin Core previously. Changes needed to mitigate these ambiguities include assigning existing properties to different classes, adding new properties to existing Darwin Core classes and 
improving definitions, usage comments and examples of existing Darwin Core terms (both classes and properties).

#### Occurrence

One of the most fundamental advances of the Semantic Layer, reflected in the DwC-DP publishing model, is the disambiguation of the `dwc:Occurrence` class. Previously, in practice, a `dwc:Occurrence` was a catch-all for information in support of the existence of a `dwc:Organism` at a place and time. Under DwC-CM, a `dwc:Occurrence` is "A state of a `dwc:Organism` in a `dwc:Event`." Thus, material evidence, though it can support the validity of a `dwc:Occurrence`, does not consist of properties of the Occurrence. Instead, all of the ephemeral characteristics of the state of an Organism are properties of a `dwc:Occurrence` while the permanent characteristics remain properties of the Organism. In short, the `dwc:Occurrence` now consists of the changeable things about a `dwc:Organism` at a given place and time that were observed or inferred.

## Participating in the Review

To understand how to participate in the review process, please refer to <a href="https://github.com/tdwg/dwc/wiki/Darwin-Core-Maintenance-Frequently-Asked-Questions" target="_blank">Darwin Core Maintenance Frequently Asked Questions</a>, which provides information on the review process and the maintenance of the Darwin Core standard in general.

Here you can review the <a href="https://gbif.github.io/dwc-dp/cm/" target="_blank">Darwin Core Conceptual Model</a>. This is **a document** describing the conceptual model, seeking ratification. It goes hand in hand with the changes and new terms proposed. To comment on those, see below.

Here you can review the <a href="https://gbif.github.io/dwc-dp/dp/">Darwin Core Data Package Guide</a>. This is **a document** describing a specification for implementing Darwin Core Data Packages, seeking ratification. This document is independent of the Conceptual Model and of the term changes and additions.

Here you can review the <a href="https://github.com/tdwg/dwc/milestone/20" target="_blank">List of term additions and changes proposal</a>. You may comment on each term, as we normally do for Darwin Core enhancements (refer to the <a href="https://github.com/tdwg/dwc/wiki/Darwin-Core-Maintenance-Frequently-Asked-Questions" target="_blank">FAQs</a> above for guidance).

In addition, there are relevant resources closely related and recommended reading:
- <a href="https://dwc.tdwg.org/terms/" target="_blank">Darwin Core Quick Reference Guide</a> (Darwin Core term definitions). Note that this document DOES NOT contain the proposed changes, it will only incorporate them if they are ratified.
- <a href="https://gbif.github.io/dwc-dp/qrg/" target="_blank">Darwin Core Data Package Quick Reference Guide</a> (contextual term definitions for tables and fields for a Darwin Core Data Package implementation of DwC-CM).
- <a href="https://gbif.github.io/dwc-dp/explorer/" target="_blank">Darwin Core Data Package Relationship Explorer</a> (tool to visualize and explore the relationships implemented in the Darwin Core Data Package).
