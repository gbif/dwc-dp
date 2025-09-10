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
: <http://rs.tdwg.org/dwc/dp/2025-09-10>

Latest version
: <http://rs.tdwg.org/dwc/dp/>

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
[resource]: https://specs.frictionlessdata.io/data-resource/
[csv-dialect]: https://specs.frictionlessdata.io/csv-dialect/
[tabular-data-resource]: https://specs.frictionlessdata.io/tabular-data-resource/
[resource.name]: https://specs.frictionlessdata.io/data-resource/#name
[resource.path]: https://specs.frictionlessdata.io/data-resource/#path-data-in-files
[resource.profile]: https://specs.frictionlessdata.io/data-resource/#profile
[resource.format]: https://specs.frictionlessdata.io/data-resource/#optional-properties
[resource.mediatype]: https://specs.frictionlessdata.io/data-resource/#optional-properties
[resource.dialect]: https://specs.frictionlessdata.io/tabular-data-resource/#csv-dialect
[resource.schema]: https://specs.frictionlessdata.io/data-resource/#resource-schemas
[resource.encoding]: https://specs.frictionlessdata.io/data-resource/#metadata-properties
[schema]: https://specs.frictionlessdata.io/table-schema/
[schema.fields]: https://specs.frictionlessdata.io/table-schema/#descriptor
[schema.fieldMatch]: https://datapackage.org/standard/table-schema/#fieldsMatch
[schema.primaryKey]: https://specs.frictionlessdata.io/table-schema/#primary-key
[schema.foreignKeys]: https://specs.frictionlessdata.io/table-schema/#foreign-keys
[schema.missingValues]: https://specs.frictionlessdata.io/table-schema/#missing-values

A DwC-DP has a **descriptor**: a JSON file named `datapackage.json` that acts as an entry point to the dataset. It contains a reference to the profile the dataset conforms to, a list of data files (resources) and (optionally) dataset-level metadata. The requirements for these elements are described below.

All requirements and examples in this guide use [version 1][dp.v1] of the Data Package specification, which is RECOMMENDED for DwC-DPs. Users MAY create descriptors using [version 2][dp.v2] of the Data Package specification, which offers functionality that can relax some of the requirements below (e.g. [`fieldMatch`][schema.fieldMatch]), but has limited software support at the time of writing.

### 3.1 Descriptor file

The descriptor MUST follow the [Data Package specification][package.descriptor] and MUST be named `datapackage.json`.

### 3.2 Package-level properties

1. The descriptor MUST have a `resources` property, with an array of data files that are considered part of a dataset. It MUST follow the [Data Package specification][package.resources] and MUST contain at least one resource. See [section 3.3](#33-resources) for details.

2. The descriptor MUST have a `profile` property, with a URL referencing the [profile][package.profile] the dataset conforms to. This MUST be a string representing the URL to a **DwC-DP profile** served from `http://rs.tdwg.org`. The URL MUST include the version of the profile (e.g. `http://rs.tdwg.org/dwc-dp/1.0/dwc-dp-profile.json` where `1.0` is the version).

    {:.alert .alert-info}
    (non-normative) The DwC-DP profile imports all [Data Package requirements](https://specs.frictionlessdata.io/schemas/data-package.json). A dataset that conforms to the DwC-DP profile will therefore also conform to the Data Package requirements. In other words: a DwC-DP is also a Data Package.

3. The descriptor SHOULD have an `id` property, with an identifier for the dataset, preferably a DOI. It MUST follow the [Data Package specification][package.id].

4. The descriptor SHOULD have a `created` property, with a timestamp indicating when the dataset was created. It MUST follow the [Data Package specification][package.created].

5. The descriptor SHOULD have a `version` property, indicating the version of the dataset. It MUST follow the [Data Package specification][package.version].

6. The descriptor MAY have additional package-level properties. This includes dataset-level metadata defined by the Data Package specification (e.g. `title`, `description`, `contributors`, `sources`, `licenses`) or custom properties.

7. An external EML document MAY accompany the dataset as supplementary metadata.

### 3.3 Resources

Each data file included in DwC-DP is a **resource**. Each resource MUST follow the [Data Resource specification][resource].

Of special interest are resources with (biodiversity) data organized in tables that implement the [Darwin Core Conceptual Model (DwC-CM)](../cm/). These resources/tables (hereafter referred to as “**DwC-DP tables**”) have additional requirements.

#### 3.3.1 DwC-DP table file requirements

Data files representing a DwC-DP table MUST be delimited text files (hereafter referred to as “**CSV files**”, irrespective of the chosen delimiter). CSV files MUST follow [RFC 4180](https://tools.ietf.org/html/rfc4180), with the following exceptions:

1. A CSV file MUST be encoded as UTF-8 OR when deviating from that encoding, the DwC-DP table MUST have an `encoding` property that MUST follow the [Data Resource specification][resource.encoding] and the files MUST follow that encoding.

2. When a CSV file deviates from RFC 4180 regarding dialect (e.g. line terminators, field delimiters, quote characters), the DwC-DP table MUST have a `dialect` property describing the dialect. That property MUST follow the [CSV Dialect specification][csv-dialect]. Only dialect properties deviating from the default SHOULD be provided. If the CSV file follows all defaults, a `dialect` property SHOULD NOT be provided.

#### 3.3.2 DwC-DP table properties

1. A DwC-DP table MUST have a `name` property, with the name of the table. It MUST follow the [Data Resource specification][resource.name] and MUST be one of the reserved table names defined in the DwC-DP profile (e.g. `"event"`, `"occurrence"`). See [section 4](#4-dwc-dp-tables-non-normative) for an overview.

2. A DwC-DP table MUST have a `path` property, with the path to the data file. It MUST follow the [Data Resource specification][resource.path].

3. A DwC-DP table MUST have a `profile` property, indicating the type of resource. It MUST be the value `"tabular-data-resource"`, thereby indicating that it follows the [Tabular Data Resource][tabular-data-resource] specification.

4. A DwC-DP table SHOULD have a `format` property, indicating the standard file extension of the data file (e.g. `"csv"`, `"tsv"`). It MUST follow the [Data Resource specification][resource.format].

5. A DwC-DP table SHOULD have a `mediatype` property, indicating the mediatype of the data file (e.g. `"text/csv"`). It MUST follow the [Data Resource specification][resource.mediatype] and MUST be the value `"text/csv"`.

6. A DwC-DP table MUST have a `schema` property, with a **table schema** describing the fields and relationships of the table. It MUST follow the [Data Resource specification][resource.schema], but MUST be an object representing the schema (and not a string referencing it). See [section 3.4](#34-table-schemas) for details.

    {:.alert .alert-info}
    (non-normative) By verbosely including the `schema`, a descriptor does not rely on externally hosted files (except for the DwC-DP profile) to describe the data it represents.

7. A DwC-DP table MAY have additional properties. This includes those defined by the Data Package specification (e.g. `bytes`, `hash`) or custom properties.

#### 3.3.3 Other resources

A DwC-DP MAY include other resources that do not represent a DwC-DP table. They MUST NOT have a `name` that is one of the reserved table names defined in the DwC-DP profile. See [section 4](#4-dwc-dp-tables-non-normative) for an overview.

### 3.4 Table Schemas

A **table schema** describes the fields, relationships and missing values of a tabular data file. A table schema MUST follow the [Table Schema specification][schema].

Table schemas are provided at `rs.tdwg.org` for each DwC-DP table. See [section 4](#4-dwc-dp-tables-non-normative) for an overview. These include all possible fields, primary keys and foreign key relationships a table can have. Use these to select the fields and keys that are applicable to your data.

1. A DwC-DP table schema MUST have a `fields` property, with an array of **field descriptors** describing the fields/columns in the data file. It must follow the [Table Scheme specification][schema.fields], but the order and number of elements in `fields` MUST be the order and number of fields in the CSV file. See [section 3.5](#3.5-field-descriptors) for details.

2. Each field in a DwC-DP table schema MUST be described with the field descriptor of the table schema provided at `rs.tdwg.org` for that table. E.g. if you want to describe an `"eventID"` field in an `"event"` table, you MUST use the field descriptor for `"eventID"` in the table schema for `"event"` provided at `rs.tdwg.org`. Fields MUST NOT be misrepresented. Custom fields SHOULD NOT be added.

3. A DwC-DP table schema MAY have a `primaryKey` property, indicating the field(s) that act as primary keys. It MUST follow the [Table Schema specification][schema.primaryKey]. This property is REQUIRED if the field is referenced by another table. `primaryKey` values MUST be one or more `primaryKey` values of the table schema provided at `rs.tdwg.org` for that table. See [section 3.6](#36-relationships-and-keys) for details.

4. A DwC-DP table schema MAY have a `foreignKeys` property, with an array of relationships the table has with other tables. It MUST follow the [Table Schema specification][schema.foreignKeys]. This property is REQUIRED if the table has a foreign key relationship with another table. `foreignKeys` values MUST be one or more `foreignKeys` values of the table schema provided at `rs.tdwg.org` for that table. See [section 3.6](#36-relationships-and-keys) for details.

5. A DwC-DP table schema MAY have a `missingValues` property, indicating what values should be interpreted as `null`. It MUST follow the [Table Schema specification][schema.missingValues].

6. A DwC-DP table schema MAY have custom properties.


**DwC-DP field-level linking metadata, optional but recommended**

- `namespace`: abbreviation for the term’s namespace (`"dwc"`, `"dcterms"`, `"rdfs"`, `"rdf"`, and so on).
- `dcterms:isVersionOf`: IRI for the unversioned source term (for example, `http://rs.tdwg.org/dwc/terms/eventID`).
- `dcterms:references`: IRI for the versioned source term (for example, `http://rs.tdwg.org/dwc/terms/version/eventID-2023-06-28`).

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

### 2.8 Conformance checklist (normative)

- Package MUST have `name`, at least one `resource`, and declare DwC-DP conformance via `profile` or `$schema`.
- Every resource MUST have `profile: "tabular-data-resource"` and a `schema` (inline or URL).
- Each table schema SHOULD define `fields`, use sensible `type` and `constraints`, and set `missingValues` if needed.
- Tables that are referenced by other tables MUST define a `primaryKey`.
- Foreign keys MUST declare both local `fields` and `reference` to target `resource` and `fields`. Note: In Data Package version 1.0, self-referential foreign keys MUST leave the reference property blank ("").
- Links to terms in standard vocabularies, when used, SHOULD include `namespace`, `dcterms:isVersionOf`, `dcterms:references`, and `rdfs:comment`.

## 4. DwC-DP tables (non-normative)

table name | table schema
--- | ---
`"agent"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/agent.json>
`"agent-agent-role"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/agent-agent-role.json>
`"agent-identifier"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/agent-identifier.json>
`"agent-media"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/agent-media.json>
`"chronometric-age"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/chronometric-age.json>
`"chronometric-age-agent-role"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/chronometric-age-agent-role.json>
`"chronometric-age-assertion"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/chronometric-age-assertion.json>
`"chronometric-age-media"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/chronometric-age-media.json>
`"chronometric-age-protocol"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/chronometric-age-protocol.json>
`"chronometric-age-reference"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/chronometric-age-reference.json>
`"event"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/event.json>
`"event-agent-role"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/event-agent-role.json>
`"event-assertion"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/event-assertion.json>
`"event-identifier"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/event-identifier.json>
`"event-media"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/event-media.json>
`"event-protocol"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/event-protocol.json>
`"event-provenance"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/event-provenance.json>
`"event-reference"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/event-reference.json>
`"geological-context"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/geological-context.json>
`"geological-context-media"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/geological-context-media.json>
`"identification"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/identification.json>
`"identification-agent-role"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/identification-agent-role.json>
`"identification-taxon"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/identification-taxon.json>
`"material"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/material.json>
`"material-agent-role"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/material-agent-role.json>
`"material-assertion"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/material-assertion.json>
`"material-identifier"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/material-identifier.json>
`"material-media"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/material-media.json>
`"material-protocol"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/material-protocol.json>
`"material-provenance"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/material-provenance.json>
`"material-reference"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/material-reference.json>
`"material-rights"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/material-rights.json> <span class="badge bg-danger">MISSING</span>
`"media"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/media.json>
`"media-agent-role"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/media-agent-role.json>
`"media-assertion"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/media-assertion.json>
`"media-identifier"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/media-identifier.json>
`"molecular-protocol"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/molecular-protocol.json>
`"media-provenance"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/media-provenance.json>
`"media-rights"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/media-rights.json> <span class="badge bg-danger">MISSING</span>
`"molecular-protocol-agent-role"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/molecular-protocol-agent-role.json>
`"molecular-protocol-assertion"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/molecular-protocol-assertion.json>
`"molecular-protocol-reference"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/molecular-protocol-reference.json>
`"nucleotide-analysis"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/nucleotide-analysis.json>
`"nucleotide-analysis-assertion"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/nucleotide-analysis-assertion.json>
`"nucleotide-sequence"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/nucleotide-sequence.json>
`"occurrence"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/occurrence.json>
`"occurrence-agent-role"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/occurrence-agent-role.json>
`"occurrence-assertion"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/occurrence-assertion.json>
`"occurrence-identifier"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/occurrence-identifier.json>
`"occurrence-media"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/occurrence-media.json>
`"occurrence-protocol"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/occurrence-protocol.json>
`"organism"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/organism.json>
`"organism-assertion"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/organism-assertion.json>
`"organism-identifier"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/organism-identifier.json>
`"organism-interaction"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/organism-interaction.json>
`"organism-interaction-agent-role"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/organism-interaction-agent-role.json>
`"organism-interaction-assertion"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/organism-interaction-assertion.json>
`"organism-interaction-media"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/organism-interaction-media.json>
`"organism-interaction-reference"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/organism-interaction-reference.json>
`"organism-reference"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/organism-reference.json>
`"organism-relationship"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/organism-relationship.json>
`"protocol"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/protocol.json>
`"provenance"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/provenance.json>
`"reference"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/reference.json>
`"rights"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/rights.json> <span class="badge bg-danger">MISSING</span>
`"resource-relationship"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/resource-relationship.json>
`"survey"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/survey.json>
`"survey-agent-role"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/survey-agent-role.json>
`"survey-assertion"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/survey-assertion.json>
`"survey-identifier"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/survey-identifier.json>
`"survey-protocol"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/survey-protocol.json>
`"survey-reference"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/survey-reference.json>
`"survey-target"` | <https://raw.githubusercontent.com/gbif/dwc-dp/refs/heads/master/dwc-dp/0.1/table-schemas/survey-target.json>
