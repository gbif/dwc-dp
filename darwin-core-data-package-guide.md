---
permalink: /dp/
toc: true
---

# Darwin Core data package guide

**Title**  
: Darwin Core data package guide

**Date version issued**  
: 2025-09-01

**Date created**  
: 2025-08-12

**Part of TDWG Standard**  
: <http://www.tdwg.org/standards/450>

**This version**  
: <http://rs.tdwg.org/dwc/terms/guides/dp/2025-09-01>

**Latest version**  
: <http://rs.tdwg.org/dwc/terms/guides/dp/>

**Previous version**  
: —

**Abstract**  
: Guidelines for implementing Darwin Core in Frictionless Data Packages.

**Contributors**  
: [Peter Desmet](https://orcid.org/0000-0002-8442-8025) ([INBO](https://www.wikidata.org/wiki/Q131900338)), [Tim Robertson](https://orcid.org/0000-0001-6215-3617) ([Global Biodiversity Information Facility](http://www.wikidata.org/entity/Q1531570)), [John Wieczorek](https://orcid.org/0000-0003-1144-0290) Rauthiflor LLC

**Creator**  
Darwin Core Maintenance Group

**Bibliographic citation**  
Darwin Core Maintenance Group. 2025. Darwin Core data package guide. Biodiversity Information Standards (TDWG). http://rs.tdwg.org/dwc/terms/guides/dp/2025-09-01.

---

## Table of Contents

- [1 Introduction (non-normative)](#1-introduction-non-normative)

  - [1.1 Purpose (non-normative)](#11-purpose-non-normative)
  - [1.2 Audience (non-normative)](#12-audience-non-normative)
  - [1.3 Associated Documents (non-normative)](#13-associated-documents-non-normative)
  - [1.4 Status of the content of this document (normative)](#14-status-of-the-content-of-this-document-normative)
  - [1.5 RFC 2119 key words (normative)](#15-rfc-2119-key-words-normative)
  - [1.6 Namespace abbreviations (non-normative)](#16-namespace-abbreviations-non-normative)
- [2. Descriptor content](#2-descriptor-content)

  - [2.1 What is the package descriptor (`datapackage.json`)?](#21-what-is-the-package-descriptor-datapackagejson)

    - [Package-level properties](#package-level-properties)
    - [Minimal compliant `datapackage.json` (instance)](#minimal-compliant-datapackagejson-instance)
  - [2.2 Resource objects](#22-resource-objects)
  - [2.3 Table Schema](#23-table-schema)
  - [2.4 Field descriptors](#24-field-descriptors)
  - [2.5 Keys and relationships](#25-keys-and-relationships)
  - [2.6 Table dialects and data files](#26-table-dialects-and-data-files)
  - [2.7 Putting it together, a richer, but still small package](#27-putting-it-together-a-richer-but-still-small-package)
  - [2.8 Conformance checklist](#28-conformance-checklist)

---

## 1 Introduction

### 1.1 Purpose (non-normative)

**Darwin Core Data Package (DwC‑DP)** is a community‑developed implementation profile of the [Frictionless Data Package](https://specs.frictionlessdata.io/data-package/) for the exchange of primary biodiversity data. A DwC‑DP consists of a `datapackage.json` file (describing the dataset and its structure) and one or more tabular data files (resources) that contain the data for the dataset.

This guide explains the goals and scope of DwC‑DP and provides practical direction for structuring packages that use Darwin Core terms. It focuses on how to:

  - represent tables as resources and declare their Table Schemas;

  - define fields, types, and constraints aligned with Darwin Core definitions;

  - declare primary keys and foreign keys to model relationships; and

  - record packaging details needed for reliable exchange.

### 1.2 Audience (non-normative)

This guide is intended for biodiversity data providers, curators, aggregators, researchers, software implementers, and standards developers who prepare or consume datasets using Darwin Core. It assumes familiarity with CSV/TSV tabular data but not with Frictionless specifications. Where helpful, it references relevant parts of the Frictionless documentation and the Darwin Core standard.

### 1.3 Associated Documents (non-normative)

The following resources are closely related and are recommended reading:

  - [Darwin Core Data Package Quick Reference Guide](https://gbif.github.io/dwc-dp/qrg/) (DwC‑DP tables, fields, and links to term definitions)

  - [Frictionless Data Package specification](https://specs.frictionlessdata.io/data-package/) (descriptor keywords, table schemas, field types, constraints, keys, dialects)

  - [Darwin Core text guide](https://dwc.tdwg.org/text/) (conceptual and usage guidance for Darwin Core as text)

### 1.4 Status of the content of this document (normative)

Sections may be either normative (defines what is required to comply with the standard) or non-normative (supports understanding but is not binding) and are marked as such.

Any sentence or phrase beginning with "For example" or "e.g.", whether in a normative section or a non-normative section, is non-normative.

### 1.5 RFC 2119 key words (normative)

The key words **“MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”,** and **“OPTIONAL”** in this document are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they are written in capitals as shown here.

### 1.6 Namespace abbreviations (non-normative)

The following namespace abbreviations are used in this document:

| Abbreviation | Namespace |
| ------------ | --------- |
| chrono:      | http://rs.tdwg.org/chrono/terms/ |
| dc:          | http://purl.org/dc/elements/1.1/ |
| dcterms:     | http://purl.org/dc/terms/ |
| dwc:         | http://rs.tdwg.org/dwc/terms/ |
| dwciri:      | http://rs.tdwg.org/dwc/iri/ |
| eco:         | http://rs.tdwg.org/eco/terms/ |
| rdf:         | http://www.w3.org/1999/02/22-rdf-syntax-ns# | 
| rdfs:        | http://www.w3.org/2000/01/rdf-schema# |

## 2 Descriptor content

### 2.1 What is the package descriptor?
The file `datapackage.json` is the JSON file that describes your dataset: its basic metadata, the profile it conforms to, and the list of data files (“resources”) together with their table schemas.

A Darwin Core Data Package (DwC-DP):
- **MUST** be a valid [Frictionless Data Package](https://specs.frictionlessdata.io/data-package/), and  
- **MUST** declare conformance to the DwC-DP profile using either the `profile` property or the `$schema` property.

#### Package-level properties
- **name**: **MUST** be included.  
- **resources**: **MUST** include one or more resources, each describing a tabular data file.  
- **profile** or **$schema**: **MUST** declare DwC-DP conformance, either is acceptable.  
- **title**: **SHOULD** be included.  
- **description**: **SHOULD** be included.  
- **created**: **SHOULD** be an RFC 3339 date-time.  
- **licenses**: **SHOULD** be included.  

Additional dataset-level metadata, such as contributors, sources, and bibliographicCitation, **MAY** be included. An external EML document **MAY** accompany the package as supplementary metadata.

#### Minimal compliant `datapackage.json` (instance)
```json
{
  "name": "my-dwc-dp",
  "profile": "https://raw.githubusercontent.com/tdwg/dwc-dp/1.0.0/dwc-dp-profile.json",
  "title": "Example dataset",
  "description": "Occurrences and events for demonstration purposes.",
  "created": "2025-09-01T00:00:00Z",
  "licenses": [
    { "name": "CC-BY-4.0", "path": "https://creativecommons.org/licenses/by/4.0/" }
  ],
  "resources": [
    {
      "name": "event",
      "profile": "tabular-data-resource",
      "path": "event.csv",
      "schema": "https://example.org/table-schemas/event.table-schema.json"
    }
  ]
}
```

> Tip: You can inline the table schema instead of linking to a URL, see 2.3.

---

### 2.2 Resource objects
Each dataset entity (CSV table) is a **resource**. In DwC-DP, every resource **MUST** be a **Tabular Data Resource** and **MUST** include a **Table Schema**.

**Resource MUST contain**
- `name`: stable table identifier (for example, `event`, `occurrence`, `agent`).  
- `profile`: the string `"tabular-data-resource"`.  
- `schema`: a **Table Schema** object, or a URL to one.  

**Resource MAY contain**
- `path` (for file-based data) or `data` (for inline rows).  
- `format`, `mediatype`, `encoding`, and `dialect` (CSV parsing hints).  
- `bytes` and `hash` (recommended for fixity).  

**Example (resource with inline schema)**
```json
{
  "name": "occurrence",
  "profile": "tabular-data-resource",
  "path": "occurrence.csv",
  "encoding": "utf-8",
  "dialect": { "delimiter": "," },
  "schema": {
    "fields": [
      { "name": "occurrenceID", "type": "string", "constraints": { "required": true, "unique": true } },
      { "name": "eventID", "type": "string", "constraints": { "required": true } }
    ],
    "primaryKey": "occurrenceID",
    "foreignKeys": [
      {
        "fields": "eventID",
        "reference": { "resource": "event", "fields": "eventID" },
        "predicateLabel": "observed during",
        "predicateIRI": "http://example.org/predicate/observedDuring"
      }
    ],
    "missingValues": [""]
  }
}
```

---

### 2.3 Table Schema
A **Table Schema** declares the structure and integrity rules for a single resource.

**Table Schema MUST contain**
- `fields`: an array of field descriptors.  
- If the table is referenced by other tables, a `primaryKey`.  

**Table Schema MAY contain**
- `foreignKeys`: relationships to other resources.  
- `missingValues`: tokens to treat as nulls (for example, `[""]`).  

> Self-references are allowed. For the classic form, set `reference.resource` to an empty string (`""`) and `reference.fields` to the local primary key. Newer tooling may allow omitting `resource`. Both patterns are acceptable in DwC-DP.

---

### 2.4 Field descriptors
Field descriptors follow Frictionless Table Schema and support DwC-DP linking metadata.

**Field MUST contain**
- `name`: the local column name (for example, `eventID`, `decimalLatitude`).  

**Field SHOULD contain**
- `type`: a Table Schema type (`string`, `integer`, `number`, `boolean`, `date`, `datetime`).  
- `description`: the Darwin Core definition, or an adapted description when the field is a DwC-DP addition.  
- `constraints`: as needed, for example, `required`, `unique`, `enum`, `minimum`, `maximum`, `pattern`.  
- `title`: a human-readable label.  

**DwC-DP field-level linking metadata, optional but recommended**
- `namespace`: abbreviation for the term’s namespace (`"dwc"`, `"dcterms"`, `"rdfs"`, `"rdf"`, and so on).  
- `dcterms:isVersionOf`: IRI for the unversioned source term (for example, `http://rs.tdwg.org/dwc/terms/eventID`).  
- `dcterms:references`: IRI for the versioned source term (for example, `http://rs.tdwg.org/dwc/terms/version/eventID-2023-06-28`).  
- `rdfs:comment`: the canonical definition text copied from the source term.  
- `comments`: usage notes that are specific to this table’s context.  

**Example field using DwC linking**
```json
{
  "name": "eventID",
  "title": "Event ID",
  "type": "string",
  "constraints": { "required": true, "unique": true },
  "namespace": "dwc",
  "dcterms:isVersionOf": "http://rs.tdwg.org/dwc/terms/eventID",
  "dcterms:references": "http://rs.tdwg.org/dwc/terms/version/eventID-2023-06-28",
  "rdfs:comment": "An identifier for the set of information associated with a dwc:Event."
}
```

---

### 2.5 Keys and relationships
Relationships are expressed with Table Schema keys.

**Primary keys**
- Present on any table that other tables reference.  
- Values should be stable and, when feasible, globally unique.  

**Foreign keys**
- Each FK declares local `fields` and a `reference` with a target `resource` and target `fields`.  
- Repeatable relationships are permitted.  
- For many-to-many relations, use an explicit join table with two foreign keys.  
- To document relationship semantics, you may add `predicateLabel` and `predicateIRI` alongside each foreign key; these do not affect validation.  

**Join table snippet, non-normative**
```json
{
  "fields": [
    { "name": "identificationID", "type": "string", "constraints": { "required": true } },
    { "name": "occurrenceID", "type": "string", "constraints": { "required": true } },
    { "name": "role", "type": "string" }
  ],
  "primaryKey": ["identificationID", "occurrenceID"],
  "foreignKeys": [
    { "fields": "identificationID", "reference": { "resource": "identification", "fields": "identificationID" } },
    { "fields": "occurrenceID", "reference": { "resource": "occurrence", "fields": "occurrenceID" } }
  ]
}
```

---

### 2.6 Table dialects and data files
- **CSV or TSV**: DwC-DP resources **SHOULD** use UTF-8 encoded CSV or TSV with a header row.  
- **Dialect**: If you use non-default quoting, delimiter, or line endings, declare a `dialect` at the resource.  
- **Missing values**: Declare `missingValues` so validators convert those tokens to null before applying constraints.  
- **Fixity**: Including `bytes` and `hash` on resources is recommended for integrity checks.

---

### 2.7 Putting it together, a richer, but still small package
```json
{
  "name": "amphibia-survey-2024",
  "$schema": "https://raw.githubusercontent.com/tdwg/dwc-dp/1.0.0/dwc-dp-profile.json",
  "title": "Amphibian Survey 2024",
  "description": "Events and occurrences from the 2024 wet-season survey.",
  "created": "2025-01-15T12:34:56Z",
  "licenses": [
    { "name": "CC-BY-4.0", "path": "https://creativecommons.org/licenses/by/4.0/" }
  ],
  "resources": [
    {
      "name": "event",
      "profile": "tabular-data-resource",
      "path": "event.csv",
      "schema": {
        "fields": [
          {
            "name": "eventID",
            "type": "string",
            "constraints": { "required": true, "unique": true },
            "namespace": "dwc",
            "dcterms:isVersionOf": "http://rs.tdwg.org/dwc/terms/eventID",
            "dcterms:references": "http://rs.tdwg.org/dwc/terms/version/eventID-2023-06-28"
          },
          { "name": "eventDate", "type": "date" },
          { "name": "decimalLatitude", "type": "number" },
          { "name": "decimalLongitude", "type": "number" }
        ],
        "primaryKey": "eventID",
        "missingValues": [""]
      }
    },
    {
      "name": "occurrence",
      "profile": "tabular-data-resource",
      "path": "occurrence.csv",
      "schema": {
        "fields": [
          { "name": "occurrenceID", "type": "string", "constraints": { "required": true, "unique": true } },
          { "name": "eventID", "type": "string", "constraints": { "required": true } },
          {
            "name": "recordedByID",
            "type": "string",
            "namespace": "dwc",
            "dcterms:isVersionOf": "http://rs.tdwg.org/dwc/terms/recordedByID",
            "dcterms:references": "http://rs.tdwg.org/dwc/terms/version/recordedByID-2023-06-28"
          }
        ],
        "primaryKey": "occurrenceID",
        "foreignKeys": [
          {
            "fields": "eventID",
            "reference": { "resource": "event", "fields": "eventID" },
            "predicateLabel": "observed during"
          }
        ],
        "missingValues": [""]
      }
    }
  ]
}
```

---

### 2.8 Conformance checklist (normative)
- Package MUST have `name`, at least one `resource`, and declare DwC-DP conformance via `profile` or `$schema`.  
- Every resource MUST have `profile: "tabular-data-resource"` and a `schema` (inline or URL).  
- Each table schema SHOULD define `fields`, use sensible `type` and `constraints`, and set `missingValues` if needed.  
- Tables that are referenced by other tables MUST define a `primaryKey`.  
- Foreign keys MUST declare both local `fields` and `reference` to target `resource` and `fields`. Note: In Data Package version 1.0, self-referential foreign keys MUST leave the reference property blank ("").
- Links to terms in standard vocabularies, when used, SHOULD include `namespace`, `dcterms:isVersionOf`, `dcterms:references`, and `rdfs:comment`.
