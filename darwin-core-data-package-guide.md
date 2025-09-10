---
permalink: /dp/
toc: true
---

# Darwin Core Data Package guide

Title
: Darwin Core Data Package guide

Date version issued
: 2025-09-10

Date created
: 2025-08-12

Part of TDWG Standard
: <http://www.tdwg.org/standards/450>

This version
: < http://rs.tdwg.org/dwc/doc/dp/2025-09-03>

Latest version
: <http://rs.tdwg.org/dwc/terms/guides/dp/>

Previous version
: —

Abstract
: Guidelines for implementing Darwin Core in Frictionless Data Packages.

Contributors
: [Peter Desmet](https://orcid.org/0000-0002-8442-8025) ([INBO](https://www.wikidata.org/wiki/Q131900338)), [John Wieczorek](https://orcid.org/0000-0003-1144-0290) (Rauthiflor LLC)

Creator
: Darwin Core Maintenance Group

Bibliographic citation
: Darwin Core Maintenance Group. 2025. Darwin Core Data Package guide. Biodiversity Information Standards (TDWG). <http://rs.tdwg.org/dwc/terms/guides/dp/2025-09-10>.

## 1 Introduction

### 1.1 Purpose (non-normative)

**Darwin Core Data Package (DwC‑DP)** is a community‑developed implementation profile of [Frictionless Data Package](https://specs.frictionlessdata.io/data-package/) for the exchange of primary biodiversity data. A DwC‑DP consists of a `datapackage.json` file (describing the dataset and its structure) and one or more tabular data files (resources) that contain the data for the dataset.

This guide explains the goals and scope of DwC‑DP and provides practical direction for structuring packages that use Darwin Core terms. It focuses on how to:

- represent tables as resources and declare their Table Schemas;

- define fields, types, and constraints aligned with Darwin Core definitions;

- declare primary keys and foreign keys to model relationships; and

- record packaging details needed for reliable exchange.

### 1.2 Audience (non-normative)

This guide is intended for biodiversity data providers, curators, aggregators, researchers, software implementers, and standards developers who prepare or consume datasets using Darwin Core. It assumes familiarity with CSV/TSV tabular data but not with the Frictionless Data Package specification (hereafter referred to as “Data Package”). Where helpful, it references relevant parts of the Data Package documentation and the Darwin Core standard.

### 1.3 Associated documents (non-normative)

The following resources are closely related and are recommended reading:

- [Darwin Core Data Package Quick Reference Guide](https://gbif.github.io/dwc-dp/qrg/) (DwC‑DP tables, fields, and links to term definitions)

- [Data Package specification](https://specs.frictionlessdata.io/data-package/) (descriptor, table schemas, field types, constraints, keys, dialects)

- [Darwin Core text guide](https://dwc.tdwg.org/text/) (conceptual and usage guidance for Darwin Core as text)

### 1.4 Status of the content of this document

All sections of this document are normative (defines what is required to comply with the standard), except for sections that are explicitly marked as non-normative (support understand but is not binding).

### 1.5 RFC 2119 key words

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).


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


## 2 Example (non-normative)

Consider a dataset containing four bird Occurrences observed during a single Event. It can be described as two CSV files, each representing a Darwin Core table:

**events.csv**

```text
eventID,eventDate,locationID
S229876476,2025-04-26T08:57:00+02:00,L43523233
```

**occurrences.csv**

```text
eventID,scientificName,organismQuantity,organismQuantityType
S229876476,Apus apus,3,individuals
S229876476,Troglodytes troglodytes,1,individuals
S229876476,Turdus merula,1,individuals
S229876476,Erithacus rubecula,1,individuals
```

This dataset can be described as a DwC-DP with the following **descriptor** (`datapackage.json`):

```json
{
  "profile": "http://rs.tdwg.org/dwc-dp/0.1/dwc-dp-profile.json",
  "id": "dwc-dp-example-dataset",
  "created": "2025-09-08T09:52:03Z",
  "version": "1.0",
  "resources": [
    {
      "name": "event",
      "path": "event.csv",
      "profile": "tabular-data-resource",
      "format": "csv",
      "mediatype": "text/csv",
      "encoding": "UTF-8",
      "schema": {
        "fields": [
          {
            "name": "eventID",
            "title": "Event ID",
            "description": "An identifier for a dwc:Event.",
            "type": "string",
            "dcterms:isVersionOf": "http://rs.tdwg.org/dwc/terms/eventID",
            "dcterms:references": "http://rs.tdwg.org/dwc/terms/version/eventID-2023-06-28"
          },
          {
            "name": "eventDate",
            "title": "Event Date",
            "description": "A date or time interval during which a dwc:Event occurred.",
            "type": "string",
            "dcterms:isVersionOf": "http://rs.tdwg.org/dwc/terms/eventDate",
            "dcterms:references": "http://rs.tdwg.org/dwc/terms/version/eventDate-2025-06-12"
          },
          {
            "name": "locationID",
            "title": "Location ID",
            "description": "An identifier a dcterms:Location.",
            "type": "string",
            "dcterms:isVersionOf": "http://rs.tdwg.org/dwc/terms/locationID",
            "dcterms:references": "http://rs.tdwg.org/dwc/terms/version/locationID-2023-06-28"
          }
        ],
        "primaryKey": ["eventID"]
      }
    },
    {
      "name": "occurrence",
      "path": "occurrence.csv",
      "profile": "tabular-data-resource",
      "format": "csv",
      "mediatype": "text/csv",
      "encoding": "UTF-8",
      "schema": {
        "fields": [
          {
            "name": "eventID",
            "title": "Event ID",
            "description": "An identifier for a dwc:Event.",
            "type": "string",
            "dcterms:isVersionOf": "http://rs.tdwg.org/dwc/terms/eventID",
            "dcterms:references": "http://rs.tdwg.org/dwc/terms/version/eventID-2023-06-28"
          },
          {
            "name": "scientificName",
            "title": "Scientific Name",
            "description": "A full scientific name, with authorship and date information if known. When forming part of a dwc:Identification, this should be the name in lowest level taxonomic rank that can be determined. This term should not contain identification qualifications, which should instead be supplied in dwc:verbatimIdentification.",
            "type": "string",
            "dcterms:isVersionOf": "http://rs.tdwg.org/dwc/terms/scientificName",
            "dcterms:references": "http://rs.tdwg.org/dwc/terms/version/scientificName-2023-06-28"
          },
          {
            "name": "organismQuantity",
            "title": "Organism Quantity",
            "description": "A number or enumeration value for the quantity of dwc:Organisms.",
            "type": "string",
            "dcterms:isVersionOf": "http://rs.tdwg.org/dwc/terms/organismQuantity",
            "dcterms:references": "http://rs.tdwg.org/dwc/terms/version/organismQuantity-2023-06-28"
          },
          {
            "name": "organismQuantityType",
            "title": "Organism Quantity Type",
            "description": "A type of quantification system used for the quantity of dwc:Organisms.",
            "type": "string",
            "dcterms:isVersionOf": "http://rs.tdwg.org/dwc/terms/organismQuantityType",
            "dcterms:references": "http://rs.tdwg.org/dwc/terms/version/organismQuantityType-2023-06-28"
          }
        ],
        "foreignKeys": [
          {
            "fields": "eventID",
            "reference": {
              "resource": "event",
              "fields": "eventID"
            }
          }
        ]
      }
    }
  ]
}
```

## 3 Descriptor content

[dp.v1]: https://specs.frictionlessdata.io/
[dp.v2]: https://datapackage.org/
[package.descriptor]: https://specs.frictionlessdata.io/data-package/#descriptor
[package.resources]: https://specs.frictionlessdata.io/data-package/#required-properties
[package.profile]: https://specs.frictionlessdata.io/data-package/#profile
[package.id]: https://specs.frictionlessdata.io/data-package/#id
[package.created]: https://specs.frictionlessdata.io/data-package/#created
[package.version]: https://specs.frictionlessdata.io/data-package/#version
A DwC-DP has a **descriptor**: a JSON file named `datapackage.json` that acts as an entry point to the dataset. It contains a reference to the profile the dataset conforms to, a list of data files (resources) and (optionally) dataset-level metadata. The requirements for these elements are described below.

{:.alert .alert-info}
All requirements and examples in this guide use [version 1][dp.v1] of the Data Package specification, which is RECOMMENDED for DwC-DPs. Users MAY create descriptors using [version 2][dp.v2] of the Data Package specification, which offers functionality that can relax some of the requirements below (e.g. [`fieldMatch`][schema.fieldMatch]), but has limited software support at the time of writing.

### 3.1 Descriptor file

The descriptor MUST follow the [Data Package specification][package.descriptor] and MUST be named `datapackage.json`.

### 3.2 Package-level properties

1. The descriptor MUST have a `resources` property, with an array of data files that are considered part of a dataset. It MUST follow the [Data Package specification][package.resources] and MUST contain at least one resource. See [section 3.3](#33-resources) for details.

2. The descriptor MUST have a `profile` property, with a URL referencing the [profile][package.profile] the dataset conforms to. This MUST be a string representing the URL to a **DwC-DP profile** served from `http://rs.tdwg.org`. The URL MUST include the version of the profile (e.g. `http://rs.tdwg.org/dwc-dp/1.0/dwc-dp-profile.json` where `1.0` is the version).

    {:.alert .alert-info}
    The DwC-DP profile imports all [Data Package requirements](https://specs.frictionlessdata.io/schemas/data-package.json). A dataset that conforms to the DwC-DP profile will therefore also conform to the Data Package requirements. In other words: a DwC-DP is also a Data Package.

3. The descriptor SHOULD have an `id` property, with an identifier for the dataset, preferably a DOI. It MUST follow the [Data Package specification][package.id].

4. The descriptor SHOULD have a `created` property, with a timestamp indicating when the dataset was created. It MUST follow the [Data Package specification][package.created].

5. The descriptor SHOULD have a `version` property, indicating the version of the dataset. It MUST follow the [Data Package specification][package.version].

6. The descriptor MAY have additional package-level properties. This includes dataset-level metadata defined by the Data Package specification (e.g. `title`, `description`, `contributors`, `sources`, `licenses`) or custom properties.

7. An external EML document MAY accompany the dataset as supplementary metadata.

### 2.2 Resources (normative)

Each data file included in the dataset (e.g. CSV file) is a _resource_. If the resource represents a table described in the DwC-DP profile, it **MUST** be a _Tabular Data Resource_ and **MUST** include a _Table Schema_. 

Each of those resources **MUST** contain:

- [`name`](https://specs.frictionlessdata.io/data-resource/#name) with the DwC-DP profile table name (e.g. `event`, `occurrence`, `agent`).
- [`path` or `data`](https://specs.frictionlessdata.io/data-resource/#data-location) with a `path` to the data file or `data` containing inline data.
- [`profile`](https://specs.frictionlessdata.io/data-resource/#profile) with `"tabular-data-resource"` to indicate that the resource is tabular in nature.
- [`schema`](https://specs.frictionlessdata.io/data-resource/#resource-schemas) with a _Table Schema_ object or URL to one (see 2.3).

Each of those resource **MAY** contain additional resource-level properties, such as `format`, `mediatype`, `encoding`, `dialect`, `bytes`, and `hash`.

You **MAY** also include additional resources, that do not represent tables described in DwC-DP profile.

#### Example (resource with inline schema)

```json
{
  "name": "occurrence",
  "path": "occurrence.csv",
  "profile": "tabular-data-resource",
  "format": "csv",
  "mediatype": "text/csv",
  "encoding": "UTF-8",
  "schema": {
    "fields": [
      {
        "name": "occurrenceID",
        "type": "string",
        "constraints": {
          "required": true,
          "unique": true
        }
      },
      {
        "name": "eventID",
        "type": "string", "constraints": {
          "required": true
        }
      }
    ],
    "primaryKey": "occurrenceID",
    "foreignKeys": [
      {
        "fields": "eventID",
        "reference": {
          "resource": "event",
          "fields": "eventID"
        },
        "predicateLabel": "observed during",
        "predicateIRI": "http://example.org/predicate/observedDuring"
      }
    ],
    "missingValues": [""]
  }
}
```

### 2.3 Table Schemas (normative)

A _Table Schema_ declares the structure and integrity rules for a Tabular Data Resource. When representing a table described by the DwC-DP profile:

The table schema **MUST** contain:

- [`fields`](https://specs.frictionlessdata.io/table-schema/#descriptor) with an array of field descriptors, in the same order as and describing all columns in the tabular data file.
- [`primaryKey`](https://specs.frictionlessdata.io/table-schema/#primary-key) if the table is referenced by other tables.

The table schema **MAY** contain:

- [`foreignKeys`](https://specs.frictionlessdata.io/table-schema/#foreign-keys) to express relationships with other tables or within-table relationships (e.g. `parentEventID -> eventID`). For the latter, set the `reference.resource` to `""`.
- [`missingValues`](https://specs.frictionlessdata.io/table-schema/#missing-values) with strings to treat as `null` values (e.g. `""`).

### 2.4 Field descriptors (normative)

Field descriptors follow Table Schema and support DwC-DP linking metadata.

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

### 2.5 Keys and relationships (normative)

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

### 2.6 Table dialects and data files (normative)

- **CSV or TSV**: DwC-DP resources **SHOULD** use UTF-8 encoded CSV or TSV with a header row.
- **Dialect**: If you use non-default quoting, delimiter, or line endings, declare a `dialect` at the resource.
- **Missing values**: Declare `missingValues` so validators convert those tokens to null before applying constraints.
- **Fixity**: Including `bytes` and `hash` on resources is recommended for integrity checks.

---

### 2.7 A richer, compliant `datapackage.json` (non-normative)

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
