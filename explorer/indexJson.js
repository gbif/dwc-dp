const indexJson = {
  "tableSchemas": [
    {
      "name": "agent",
      "title": "Agent",
      "description": "A person, group, organization, machine, software or other entity that can act.",
      "comments": "",
      "examples": "`Carl Linnaeus`; `The Terra Nova Expedition`; `The National Science Foundation`; `The El Yunque National Forest ARBIMON System`; `ChatGPT`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#Agent"
    },
    {
      "name": "agent-agent-role",
      "title": "AgentAgentRole",
      "description": "A role filled by an Agent with respect to another Agent.",
      "comments": "test",
      "examples": "`an instance of an Agent that is a person is the director of another instance of an Agent that is an organization`; `an instance of an Agent that is a person is a member of another instance of an Agent that is a group`; `an instance of an Agent that is a person is the author of another instance of an Agent that is software`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#AgentAgentRole"
    },
    {
      "name": "agent-identifier",
      "title": "AgentIdentifier",
      "description": "An identifier for an Agent.",
      "comments": "",
      "examples": "`an ORCID`; `a Wikidata Q-number`; `an Index Herbariorum Institution Code`; `an International Standard Name Identifier`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#AgentIdentifier"
    },
    {
      "name": "agent-media",
      "title": "AgentMedia",
      "description": "A link establishing an Agent as content in a Media entity.",
      "comments": "",
      "examples": "`a person shown in a photograph`; `a group of people in a video`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#AgentMedia"
    },
    {
      "name": "chronometric-age",
      "title": "ChronometricAge",
      "description": "An approximation of temporal position (in the sense conveyed by https://www.w3.org/TR/owl-time/#time:TemporalPosition) that is supported by evidence.",
      "comments": "The age of a specimen and how this age is known, whether by a dating assay, a relative association with dated material, or legacy collections information.",
      "examples": "`an age range associated with a specimen derived from an AMS dating assay applied to an oyster shell in the same stratum`; `an age range associated with a specimen derived from a ceramics analysis based on other materials found in the same stratum`; `a maximum age associated with a specimen derived from K-Ar dating applied to a proximal volcanic tuff found stratigraphically below the specimen`; `an age range of a specimen based on its biostratigraphic context`; `an age of a specimen based on what is reported in legacy collections data`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#ChronometricAge"
    },
    {
      "name": "chronometric-age-agent-role",
      "title": "ChronometricAgeAgentRole",
      "description": "A role filled by an Agent with respect to a chrono:ChronometricAge.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#ChronometricAgeAgentRole"
    },
    {
      "name": "chronometric-age-assertion",
      "title": "ChronometricAgeAssertion",
      "description": "An Assertion made by an Agent about a chrono:ChronometricAge.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#ChronometricAgeAssertion"
    },
    {
      "name": "chronometric-age-reference",
      "title": "ChronometricAgeReference",
      "description": "A bibliographic reference in which a chrono:ChronometricAge is mentioned.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#ChronometricAgeReference"
    },
    {
      "name": "chronometric-age-media",
      "title": "ChronometricAgeMedia",
      "description": "A link establishing a chrono:ChronometricAge as content of a Media entity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#ChronometricAgeMedia"
    },
    {
      "name": "chronometric-age-protocol",
      "title": "ChronometricAgeProtocol",
      "description": "A link establishing a Protocol used in the determination of a chrono:ChronometricAge.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#ChronometricAgeProtocol"
    },
    {
      "name": "event",
      "title": "Event",
      "description": "An action, process, or set of circumstances occurring at a dcterms:Location during a period of time.",
      "comments": "",
      "examples": "`a material collecting event`; `a bird observation`; `a camera trap image capture`; `an organism occurrence`; `a biotic survey`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#Event"
    },
    {
      "name": "event-agent-role",
      "title": "EventAgentRole",
      "description": "A role filled by an Agent with respect to a dwc:Event.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#EventAgentRole"
    },
    {
      "name": "event-assertion",
      "title": "EventAssertion",
      "description": "An Assertion made by an Agent about a dwc:Event.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#EventAssertion"
    },
    {
      "name": "event-reference",
      "title": "EventReference",
      "description": "A bibliographic reference in which a dwc:Event is mentioned.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#EventReference"
    },
    {
      "name": "event-identifier",
      "title": "EventIdentifier",
      "description": "An identifier for a dwc:Event.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#EventIdentifier"
    },
    {
      "name": "event-media",
      "title": "EventMedia",
      "description": "A link establishing a dwc:Event as content of a Media entity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#EventMedia"
    },
    {
      "name": "event-protocol",
      "title": "EventProtocol",
      "description": "A link establishing a Protocol used in a dwc:Event.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#EventProtocol"
    },
    {
      "name": "geological-context",
      "title": "GeologicalContext",
      "description": "A set of geological designations, such as stratigraphy, that qualifies a region or place.",
      "comments": "",
      "examples": "`a particular lithostratigraphic layer`; `a specific chronostratigraphic unit`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#GeologicalContext"
    },
    {
      "name": "geological-context-media",
      "title": "GeologicalContextMedia",
      "description": "A link establishing a dwc:GeologicalContext as content of a Media entity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#GeologicalContextMedia"
    },
    {
      "name": "identification",
      "title": "Identification",
      "description": "A taxonomic determination (i.e., the assignment of dwc:Taxa to dwc:Organisms).",
      "comments": "",
      "examples": "`a subspecies determination of an organism`; `a nomenclatural act designating a specimen as a holotype`; `the determination of species of the furs of animals in a parka`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#Identification"
    },
    {
      "name": "identification-agent-role",
      "title": "IdentificationAgentRole",
      "description": "A role filled by an Agent with respect to a dwc:Identification.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#IdentificationAgentRole"
    },
    {
      "name": "identification-taxon",
      "title": "IdentificationTaxon",
      "description": "A construct of components and positions of dwc:scientificNames in a dwc:Identification.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#IdentificationTaxon"
    },
    {
      "name": "material",
      "title": "Material",
      "description": "An entity that can be identified, exist for some period of time, and consist in whole or in part of physical matter while it exists.",
      "comments": "The term is defined at the most general level to admit descriptions of any subtype of material entity within the scope of Darwin Core. In particular, any kind of material sample, preserved specimen, fossil, or exemplar from living collections is intended to be subsumed under this term.",
      "examples": "`the entire contents of a trawl`; `a subset of the contents of a trawl`; `the body of a fish`; `the stomach contents of a fish`; `a rock containing fossils`; `a fossil within a rock`; `an herbarium sheet with its attached plant specimen`; `a flower on a plant specimen`; `a pollen grain`; `a specific water sample`; `an isolated molecule of DNA`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#Material"
    },
    {
      "name": "material-agent-role",
      "title": "MaterialAgentRole",
      "description": "A role filled by an Agent with respect to a dwc:MaterialEntity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MaterialAgentRole"
    },
    {
      "name": "material-assertion",
      "title": "MaterialAssertion",
      "description": "An Assertion made by an Agent about a dwc:MaterialEntity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MaterialAssertion"
    },
    {
      "name": "material-reference",
      "title": "MaterialReference",
      "description": "A bibliographic reference in which a dwc:MaterialEntity is mentioned.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MaterialReference"
    },
    {
      "name": "material-identifier",
      "title": "MaterialIdentifier",
      "description": "An identifier for a dwc:MaterialEntity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MaterialIdentifier"
    },
    {
      "name": "material-media",
      "title": "MaterialMedia",
      "description": "A link establishing a dwc:MaterialEntity as content of a Media entity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MaterialMedia"
    },
    {
      "name": "material-protocol",
      "title": "MaterialProtocol",
      "description": "A link establishing a Protocol used in the treatment of a dwc:MaterialEntity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MaterialProtocol"
    },
    {
      "name": "media",
      "title": "Media",
      "description": "A dcmi:MediaType (dcmi:Sounds, dcmi:StillImages, dcmi:MovingImages or dcmi:Text) with other entities as content.",
      "comments": "An instance of digital textual media may be better represented as a Reference.",
      "examples": "`a digital image`; `a camera trap image series`; `a video`; `a clip from a sound recording`; `a digital 3D mesh representing a specimen`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#Media"
    },
    {
      "name": "media-agent-role",
      "title": "MediaAgentRole",
      "description": "A role filled by an Agent with respect to a Media entity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MediaAgentRole"
    },
    {
      "name": "media-assertion",
      "title": "MediaAssertion",
      "description": "An Assertion made by an Agent about a Media entity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MediaAssertion"
    },
    {
      "name": "media-identifier",
      "title": "MediaIdentifier",
      "description": "An identifier for a Media entity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MediaIdentifier"
    },
    {
      "name": "molecular-protocol",
      "title": "MolecularProtocol",
      "description": "A protocol used to derive and identify a nucleotide sequence from a dwc:MaterialEntity.",
      "comments": "",
      "examples": "`a standard DNA barcoding workflow using Sanger sequencing`; `a shotgun metagenomics pipeline for microbial community profiling`; `a high-throughput amplicon sequencing protocol targeting 16S rRNA`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MolecularProtocol"
    },
    {
      "name": "molecular-protocol-agent-role",
      "title": "MolecularProtocolAgentRole",
      "description": "A role filled by an Agent with respect to a MolecularProtocol.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MolecularProtocolAgentRole"
    },
    {
      "name": "molecular-protocol-assertion",
      "title": "MolecularProtocolAssertion",
      "description": "An Assertion made by an Agent about a MolecularProtocol.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MolecularProtocolAssertion"
    },
    {
      "name": "molecular-protocol-reference",
      "title": "MolecularProtocolReference",
      "description": "A bibliographic reference in which a MolecularProtocol is mentioned.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#MolecularProtocolReference"
    },
    {
      "name": "nucleotide-analysis",
      "title": "NucleotideAnalysis",
      "description": "A link between a NucleotideSequence and a dwc:Event and a dwc:MaterialEntity from which it was derived, using a specified Protocol.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#NucleotideAnalysis"
    },
    {
      "name": "nucleotide-analysis-assertion",
      "title": "NucleotideAnalysisAssertion",
      "description": "An Assertion made by an Agent about a NucleotideAnalysis.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#NucleotideAnalysisAssertion"
    },
    {
      "name": "nucleotide-sequence",
      "title": "NucleotideSequence",
      "description": "A digital representation of a nucleotide sequence.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#NucleotideSequence"
    },
    {
      "name": "occurrence",
      "title": "Occurrence",
      "description": "A state of a dwc:Organism in a dwc:Event.",
      "comments": "",
      "examples": "`a wolf pack on the shore of Kluane Lake in 1988`; `a virus in a plant leaf in the New York Botanical Garden at 15:29 on 2014-10-23`; `a fungus in Central Park in the summer of 1929`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#Occurrence"
    },
    {
      "name": "occurrence-agent-role",
      "title": "OccurrenceAgentRole",
      "description": "A role filled by an Agent with respect to a dwc:Occurrence.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#OccurrenceAgentRole"
    },
    {
      "name": "occurrence-assertion",
      "title": "OccurrenceAssertion",
      "description": "An Assertion made by an Agent about a dwc:Occurrence.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#OccurrenceAssertion"
    },
    {
      "name": "occurrence-reference",
      "title": "OccurrenceReference",
      "description": "A bibliographic reference in which a dwc:Occurrence is mentioned.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#OccurrenceReference"
    },
    {
      "name": "occurrence-identifier",
      "title": "OccurrenceIdentifier",
      "description": "An identifier for a dwc:Occurrence.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#OccurrenceIdentifier"
    },
    {
      "name": "occurrence-media",
      "title": "OccurrenceMedia",
      "description": "A link establishing a dwc:Occurrence as content of a Media entity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#OccurrenceMedia"
    },
    {
      "name": "occurrence-protocol",
      "title": "OccurrenceProtocol",
      "description": "A link establishing a Protocol used in the determination of a dwc:Occurrence.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#OccurrenceProtocol"
    },
    {
      "name": "organism-interaction",
      "title": "OrganismInteraction",
      "description": "An interaction between two dwc:Organisms during a dwc:Event.",
      "comments": "Supports only primary observed interactions, not habitual or derived taxon-level interactions. Pairwise interactions must be used to represent multi-organism interactions. When possible, typify the action rather than the state from which an action is inferred, with the actor as the subject dwc:Occurrence and the acted-upon as the related dwc:Occurrence. Only one direction of a two-way interaction is necessary, though both are premissible as distint OrganismInteractions with distint subject dwc:Occurrences.",
      "examples": "`a bee visiting a flower`; `a Mallophora ruficauda hunting an Apis mellifera in flight`; `a viral infection in a plant`; `a female spider mating with a male spider`; `a lion cub nursing from its mother`; `a mosquito sucking blood from a chimpanzee's arm`; `a slug eating a fungus growing on decomposing stump (2 interactions)`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#OrganismInteraction"
    },
    {
      "name": "organism-interaction-agent-role",
      "title": "OrganismInteractionAgentRole",
      "description": "A role filled by an Agent with respect to an OrganismInteraction.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#OrganismInteractionAgentRole"
    },
    {
      "name": "organism-interaction-assertion",
      "title": "OrganismInteractionAssertion",
      "description": "An Assertion made by an Agent about an OrganismInteraction.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#OrganismInteractionAssertion"
    },
    {
      "name": "organism-interaction-reference",
      "title": "OrganismInteractionReference",
      "description": "A bibliographic reference in which an OrganismInteraction is mentioned.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#OrganismInteractionReference"
    },
    {
      "name": "organism-interaction-media",
      "title": "OrganismInteractionMedia",
      "description": "A link establishing an OrganismInteraction as content of a Media entity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#OrganismInteractionMedia"
    },
    {
      "name": "phylogenetic-tree",
      "title": "PhylogeneticTree",
      "description": "A branching diagram that shows the evolutionary relationships between dwc:Organisms.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#PhylogeneticTree"
    },
    {
      "name": "phylogenetic-tree-assertion",
      "title": "PhylogeneticTreeAssertion",
      "description": "An Assertion made by an Agent about a PhylogeneticTree.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#PhylogeneticTreeAssertion"
    },
    {
      "name": "phylogenetic-tree-reference",
      "title": "PhylogeneticTreeReference",
      "description": "A bibliographic reference in which a PhylogeneticTree is mentioned.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#PhylogeneticTreeReference"
    },
    {
      "name": "phylogenetic-tree-identifier",
      "title": "PhylogeneticTreeIdentifier",
      "description": "An identifier for a PhylogeneticTree.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#PhylogeneticTreeIdentifier"
    },
    {
      "name": "phylogenetic-tree-media",
      "title": "PhylogeneticTreeMedia",
      "description": "A link establishing a PhylogeneticTree as content of a Media entity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#PhylogeneticTreeMedia"
    },
    {
      "name": "phylogenetic-tree-protocol",
      "title": "PhylogeneticTreeProtocol",
      "description": "A link establishing a Protocol used in the determination of a PhylogeneticTree.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#PhylogeneticTreeProtocol"
    },
    {
      "name": "phylogenetic-tree-tip",
      "title": "PhylogeneticTreeTip",
      "description": "A group of Taxa at the end of a branch of a PhylogeneticTree as determined from relationships between dwc:Organisms.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#PhylogeneticTreeTip"
    },
    {
      "name": "phylogenetic-tree-tip-assertion",
      "title": "PhylogeneticTreeTipAssertion",
      "description": "An Assertion made by an Agent about a PhylogeneticTreeTip.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#PhylogeneticTreeTipAssertion"
    },
    {
      "name": "protocol",
      "title": "Protocol",
      "description": "A method used during an action.",
      "comments": "",
      "examples": "`a pitfall trap method for sampling ground-dwelling arthropods`; `a point-radius georeferencing method`; `a linear regression model to estimate body mass from skeletal measurements`; `a Bayesian phylogenetic inference method`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#Protocol"
    },
    {
      "name": "protocol-reference",
      "title": "ProtocolReference",
      "description": "A bibliographic reference in which a Protocol is mentioned.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#ProtocolReference"
    },
    {
      "name": "reference",
      "title": "Reference",
      "description": "A bibliographic reference in which an entity is mentioned.",
      "comments": "",
      "examples": "`a peer-reviewed journal article describing a taxonomic revision`; `a page in a field notebook containing an original drawing of a fossil in context`; `a nucleotide sequence database entry for a barcoded specimen`; `an online dataset documenting organism occurrences in a region`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#Reference"
    },
    {
      "name": "relationship",
      "title": "Relationship",
      "description": "A specification for a relationship of a subject entity to a related entity.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#Relationship"
    },
    {
      "name": "survey",
      "title": "Survey",
      "description": "A biotic survey.",
      "comments": "This class consists of the information you might find in the Humboldt Extension to Darwin Core, except for the target scope terms, which are here accommodated in SurveyTarget.",
      "examples": "`a botanical survey of a protected area to assess native and invasive plant species`; `a wetland vegetation mapping`; `a camera trap deployment in a rainforest to monitor large mammals`; `a frog call survey in wetlands across breeding seasons`; `a coverboard survey for reptiles in forested environments`; `a pollinator survey in an agricultural landscape`; `a macroinvertebrate sampling in a freshwater stream to assess water quality`; `a habitat- or ecosystem-level survey (e.g., coral reef health assessment, forest biodiversity assessment)`; `an environmental impact assessment (e.g., pre-construction biological baseline survey for a wind farm project)`",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#Survey"
    },
    {
      "name": "survey-agent-role",
      "title": "SurveyAgentRole",
      "description": "A role filled by an Agent with respect to a Survey.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#SurveyAgentRole"
    },
    {
      "name": "survey-assertion",
      "title": "SurveyAssertion",
      "description": "An Assertion made by an Agent about a Survey.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#SurveyAssertion"
    },
    {
      "name": "survey-reference",
      "title": "SurveyReference",
      "description": "A bibliographic reference in which a Survey is mentioned.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#SurveyReference"
    },
    {
      "name": "survey-identifier",
      "title": "SurveyIdentifier",
      "description": "An identifier for a Survey.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#SurveyIdentifier"
    },
    {
      "name": "survey-protocol",
      "title": "SurveyProtocol",
      "description": "A link establishing a Protocol used in a Survey.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#SurveyProtocol"
    },
    {
      "name": "survey-target",
      "title": "SurveyTarget",
      "description": "A specification of a characteristic of dwc:Occurrence that was included or excluded in a Survey.",
      "comments": "",
      "examples": "",
      "url": "https://gbif.github.io/dwc-dp/qrg/index.html#SurveyTarget"
    }
  ]
};