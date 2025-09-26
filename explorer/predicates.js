let predicates = [
  {
    "subject_table": "event",
    "subject_field": "parentEventID",
    "predicate": "happened during",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "event",
    "subject_field": "eventConductedByID",
    "predicate": "conducted by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "event",
    "subject_field": "georeferencedByID",
    "predicate": "georeferenced by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "event",
    "subject_field": "georeferenceProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "event",
    "subject_field": "geologicalContextID",
    "predicate": "within",
    "related_table": "geological-context",
    "related_field": "geologicalContextID"
  },
  {
    "subject_table": "chronometric-age",
    "subject_field": "eventID",
    "predicate": "for",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "chronometric-age",
    "subject_field": "chronometricAgeProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "chronometric-age",
    "subject_field": "chronometricAgeConversionProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "chronometric-age",
    "subject_field": "materialDatedID",
    "predicate": "dated",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "chronometric-age",
    "subject_field": "chronometricAgeDeterminedByID",
    "predicate": "determined by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "occurrence",
    "subject_field": "eventID",
    "predicate": "happened during",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "occurrence",
    "subject_field": "isPartOfOccurrenceID",
    "predicate": "part of",
    "related_table": "occurrence",
    "related_field": "occurrenceID"
  },
  {
    "subject_table": "occurrence",
    "subject_field": "surveyTargetID",
    "predicate": "satisfied",
    "related_table": "survey-target",
    "related_field": "surveyTargetID"
  },
  {
    "subject_table": "occurrence",
    "subject_field": "recordedByID",
    "predicate": "recorded by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "occurrence",
    "subject_field": "organismID",
    "predicate": "of an",
    "related_table": "organism",
    "related_field": "organismID"
  },
  {
    "subject_table": "occurrence",
    "subject_field": "identifiedByID",
    "predicate": "identified by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "organism-interaction",
    "subject_field": "eventID",
    "predicate": "happened during",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "organism-interaction",
    "subject_field": "subjectOccurrenceID",
    "predicate": "by",
    "related_table": "occurrence",
    "related_field": "occurrenceID"
  },
  {
    "subject_table": "organism-interaction",
    "subject_field": "relatedOccurrenceID",
    "predicate": "with",
    "related_table": "occurrence",
    "related_field": "occurrenceID"
  },
  {
    "subject_table": "survey",
    "subject_field": "eventID",
    "predicate": "happened during",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "survey",
    "subject_field": "identifiedByID",
    "predicate": "identifications by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "survey",
    "subject_field": "samplingPerformedByID",
    "predicate": "sampling performed by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "survey",
    "subject_field": "samplingEffortProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "survey-target",
    "subject_field": "surveyID",
    "predicate": "for",
    "related_table": "survey",
    "related_field": "surveyID"
  },
  {
    "subject_table": "identification",
    "subject_field": "materialEntityID",
    "predicate": "based on",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "identification",
    "subject_field": "mediaID",
    "predicate": "based on",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "identification",
    "subject_field": "nucleotideAnalysisID",
    "predicate": "based on",
    "related_table": "nucleotide-analysis",
    "related_field": "nucleotideAnalysisID"
  },
  {
    "subject_table": "identification",
    "subject_field": "nucleotideSequenceID",
    "predicate": "based on",
    "related_table": "nucleotide-sequence",
    "related_field": "nucleotideSequenceID"
  },
  {
    "subject_table": "identification",
    "subject_field": "occurrenceID",
    "predicate": "based on",
    "related_table": "occurrence",
    "related_field": "occurrenceID"
  },
  {
    "subject_table": "identification",
    "subject_field": "organismID",
    "predicate": "targeted / inferred",
    "related_table": "organism",
    "related_field": "organismID"
  },
  {
    "subject_table": "identification",
    "subject_field": "identifiedByID",
    "predicate": "identified by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "identification-taxon",
    "subject_field": "identificationID",
    "predicate": "for",
    "related_table": "identification",
    "related_field": "identificationID"
  },
  {
    "subject_table": "material",
    "subject_field": "eventID",
    "predicate": "collected during",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "material",
    "subject_field": "institutionID",
    "predicate": "stored in",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "material",
    "subject_field": "ownerInstitutionID",
    "predicate": "owned by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "material",
    "subject_field": "collectedByID",
    "predicate": "collected by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "material",
    "subject_field": "evidenceForOccurrenceID",
    "predicate": "evidence for",
    "related_table": "occurrence",
    "related_field": "occurrenceID"
  },
  {
    "subject_table": "material",
    "subject_field": "derivedFromMaterialEntityID",
    "predicate": "derived from",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "material",
    "subject_field": "derivationEventID",
    "predicate": "derived during",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "material",
    "subject_field": "isPartOfMaterialEntityID",
    "predicate": "part of",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "material",
    "subject_field": "identifiedByID",
    "predicate": "identified by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "material-geological-context",
    "subject_field": "materialEntityID",
    "predicate": "for",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "material-geological-context",
    "subject_field": "geologicalContextID",
    "predicate": "within",
    "related_table": "geological-context",
    "related_field": "geologicalContextID"
  },
  {
    "subject_table": "nucleotide-analysis",
    "subject_field": "eventID",
    "predicate": "material collected during",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "nucleotide-analysis",
    "subject_field": "molecularProtocolID",
    "predicate": "followed",
    "related_table": "molecular-protocol",
    "related_field": "molecularProtocolID"
  },
  {
    "subject_table": "nucleotide-analysis",
    "subject_field": "nucleotideSequenceID",
    "predicate": "produced",
    "related_table": "nucleotide-sequence",
    "related_field": "nucleotideSequenceID"
  },
  {
    "subject_table": "nucleotide-analysis",
    "subject_field": "materialEntityID",
    "predicate": "of",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "molecular-protocol",
    "subject_field": "source_mat_id",
    "predicate": "has source",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "agent-agent-role",
    "subject_field": "agentID",
    "predicate": "role holder",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "agent-agent-role",
    "subject_field": "relatedAgentID",
    "predicate": "role for",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "chronometric-age-agent-role",
    "subject_field": "agentID",
    "predicate": "role holder",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "chronometric-age-agent-role",
    "subject_field": "chronometricAgeID",
    "predicate": "role for",
    "related_table": "chronometric-age",
    "related_field": "chronometricAgeID"
  },
  {
    "subject_table": "event-agent-role",
    "subject_field": "agentID",
    "predicate": "role holder",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "event-agent-role",
    "subject_field": "eventID",
    "predicate": "role for",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "identification-agent-role",
    "subject_field": "agentID",
    "predicate": "role holder",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "identification-agent-role",
    "subject_field": "identificationID",
    "predicate": "role for",
    "related_table": "identification",
    "related_field": "identificationID"
  },
  {
    "subject_table": "material-agent-role",
    "subject_field": "agentID",
    "predicate": "role holder",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "material-agent-role",
    "subject_field": "materialEntityID",
    "predicate": "role for",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "media-agent-role",
    "subject_field": "agentID",
    "predicate": "role holder",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "media-agent-role",
    "subject_field": "mediaID",
    "predicate": "role for",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "molecular-protocol-agent-role",
    "subject_field": "agentID",
    "predicate": "role holder",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "molecular-protocol-agent-role",
    "subject_field": "molecularProtocolID",
    "predicate": "role for",
    "related_table": "molecular-protocol",
    "related_field": "molecularProtocolID"
  },
  {
    "subject_table": "occurrence-agent-role",
    "subject_field": "agentID",
    "predicate": "role holder",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "occurrence-agent-role",
    "subject_field": "occurrenceID",
    "predicate": "role for",
    "related_table": "occurrence",
    "related_field": "occurrenceID"
  },
  {
    "subject_table": "organism-interaction-agent-role",
    "subject_field": "agentID",
    "predicate": "role holder",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "organism-interaction-agent-role",
    "subject_field": "organismInteractionID",
    "predicate": "role for",
    "related_table": "organism-interaction",
    "related_field": "organismInteractionID"
  },
  {
    "subject_table": "survey-agent-role",
    "subject_field": "agentID",
    "predicate": "role holder",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "survey-agent-role",
    "subject_field": "surveyID",
    "predicate": "role for",
    "related_table": "survey",
    "related_field": "surveyID"
  },
  {
    "subject_table": "media",
    "subject_field": "derivedFromMediaID",
    "predicate": "derived from",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "media",
    "subject_field": "isPartOfMediaID",
    "predicate": "part of",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "media",
    "subject_field": "commenterID",
    "predicate": "comment by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "media",
    "subject_field": "reviewerID",
    "predicate": "reviewed by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "agent-media",
    "subject_field": "mediaID",
    "predicate": "this media instance",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "agent-media",
    "subject_field": "agentID",
    "predicate": "about",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "chronometric-age-media",
    "subject_field": "mediaID",
    "predicate": "this media instance",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "chronometric-age-media",
    "subject_field": "chronometricAgeID",
    "predicate": "about",
    "related_table": "chronometric-age",
    "related_field": "chronometricAgeID"
  },
  {
    "subject_table": "event-media",
    "subject_field": "mediaID",
    "predicate": "this media instance",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "event-media",
    "subject_field": "eventID",
    "predicate": "about",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "geological-context-media",
    "subject_field": "mediaID",
    "predicate": "this media instance",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "geological-context-media",
    "subject_field": "geologicalContextID",
    "predicate": "about",
    "related_table": "geological-context",
    "related_field": "geologicalContextID"
  },
  {
    "subject_table": "material-media",
    "subject_field": "mediaID",
    "predicate": "this media instance",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "material-media",
    "subject_field": "materialEntityID",
    "predicate": "about",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "occurrence-media",
    "subject_field": "mediaID",
    "predicate": "this media instance",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "occurrence-media",
    "subject_field": "occurrenceID",
    "predicate": "about",
    "related_table": "occurrence",
    "related_field": "occurrenceID"
  },
  {
    "subject_table": "organism-interaction-media",
    "subject_field": "mediaID",
    "predicate": "this media instance",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "organism-interaction-media",
    "subject_field": "organismInteractionID",
    "predicate": "about",
    "related_table": "organism-interaction",
    "related_field": "organismInteractionID"
  },
  {
    "subject_table": "chronometric-age-protocol",
    "subject_field": "chronometricAgeID",
    "predicate": "used for",
    "related_table": "chronometric-age",
    "related_field": "chronometricAgeID"
  },
  {
    "subject_table": "chronometric-age-protocol",
    "subject_field": "protocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "event-protocol",
    "subject_field": "eventID",
    "predicate": "used during",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "event-protocol",
    "subject_field": "protocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "material-protocol",
    "subject_field": "materialEntityID",
    "predicate": "used for",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "material-protocol",
    "subject_field": "protocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "occurrence-protocol",
    "subject_field": "occurrenceID",
    "predicate": "used during",
    "related_table": "occurrence",
    "related_field": "occurrenceID"
  },
  {
    "subject_table": "occurrence-protocol",
    "subject_field": "protocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "survey-protocol",
    "subject_field": "protocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "survey-protocol",
    "subject_field": "surveyID",
    "predicate": "used during",
    "related_table": "survey",
    "related_field": "surveyID"
  },
  {
    "subject_table": "bibliographic-resource",
    "subject_field": "parentReferenceID",
    "predicate": "part of",
    "related_table": "bibliographic-resource",
    "related_field": "referenceID"
  },
  {
    "subject_table": "bibliographic-resource",
    "subject_field": "authorID",
    "predicate": "authored by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "bibliographic-resource",
    "subject_field": "editorID",
    "predicate": "edited by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "bibliographic-resource",
    "subject_field": "publisherID",
    "predicate": "published by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "chronometric-age-reference",
    "subject_field": "chronometricAgeID",
    "predicate": "mentioned",
    "related_table": "chronometric-age",
    "related_field": "chronometricAgeID"
  },
  {
    "subject_table": "chronometric-age-reference",
    "subject_field": "referenceID",
    "predicate": "mentioned in",
    "related_table": "bibliographic-resource",
    "related_field": "referenceID"
  },
  {
    "subject_table": "event-reference",
    "subject_field": "eventID",
    "predicate": "mentioned",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "event-reference",
    "subject_field": "referenceID",
    "predicate": "mentioned in",
    "related_table": "bibliographic-resource",
    "related_field": "referenceID"
  },
  {
    "subject_table": "identification-reference",
    "subject_field": "identificationID",
    "predicate": "used for",
    "related_table": "identification",
    "related_field": "identificationID"
  },
  {
    "subject_table": "identification-reference",
    "subject_field": "referenceID",
    "predicate": "used",
    "related_table": "bibliographic-resource",
    "related_field": "referenceID"
  },
  {
    "subject_table": "material-reference",
    "subject_field": "referenceID",
    "predicate": "mentioned in",
    "related_table": "bibliographic-resource",
    "related_field": "referenceID"
  },
  {
    "subject_table": "material-reference",
    "subject_field": "materialEntityID",
    "predicate": "mentioned",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "molecular-protocol-reference",
    "subject_field": "referenceID",
    "predicate": "mentioned in",
    "related_table": "bibliographic-resource",
    "related_field": "referenceID"
  },
  {
    "subject_table": "molecular-protocol-reference",
    "subject_field": "molecularProtocolID",
    "predicate": "mentioned",
    "related_table": "molecular-protocol",
    "related_field": "molecularProtocolID"
  },
  {
    "subject_table": "occurrence-reference",
    "subject_field": "occurrenceID",
    "predicate": "mentioned",
    "related_table": "occurrence",
    "related_field": "occurrenceID"
  },
  {
    "subject_table": "occurrence-reference",
    "subject_field": "referenceID",
    "predicate": "mentioned in",
    "related_table": "bibliographic-resource",
    "related_field": "referenceID"
  },
  {
    "subject_table": "organism-reference",
    "subject_field": "organismID",
    "predicate": "mentioned in",
    "related_table": "organism",
    "related_field": "organismID"
  },
  {
    "subject_table": "organism-reference",
    "subject_field": "referenceID",
    "predicate": "mentioned",
    "related_table": "bibliographic-resource",
    "related_field": "referenceID"
  },
  {
    "subject_table": "organism-interaction-reference",
    "subject_field": "organismInteractionID",
    "predicate": "mentioned",
    "related_table": "organism-interaction",
    "related_field": "organismInteractionID"
  },
  {
    "subject_table": "organism-interaction-reference",
    "subject_field": "referenceID",
    "predicate": "mentioned in",
    "related_table": "bibliographic-resource",
    "related_field": "referenceID"
  },
  {
    "subject_table": "protocol-reference",
    "subject_field": "protocolID",
    "predicate": "mentioned",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "protocol-reference",
    "subject_field": "referenceID",
    "predicate": "mentioned in",
    "related_table": "bibliographic-resource",
    "related_field": "referenceID"
  },
  {
    "subject_table": "survey-reference",
    "subject_field": "referenceID",
    "predicate": "mentioned in",
    "related_table": "bibliographic-resource",
    "related_field": "referenceID"
  },
  {
    "subject_table": "survey-reference",
    "subject_field": "surveyID",
    "predicate": "mentioned",
    "related_table": "survey",
    "related_field": "surveyID"
  },
  {
    "subject_table": "chronometric-age-assertion",
    "subject_field": "chronometricAgeID",
    "predicate": "about",
    "related_table": "chronometric-age",
    "related_field": "chronometricAgeID"
  },
  {
    "subject_table": "chronometric-age-assertion",
    "subject_field": "assertionByID",
    "predicate": "asserted by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "chronometric-age-assertion",
    "subject_field": "assertionProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "event-assertion",
    "subject_field": "eventID",
    "predicate": "about",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "event-assertion",
    "subject_field": "assertionByID",
    "predicate": "asserted by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "event-assertion",
    "subject_field": "assertionProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "material-assertion",
    "subject_field": "materialEntityID",
    "predicate": "about",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "material-assertion",
    "subject_field": "assertionByID",
    "predicate": "asserted by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "material-assertion",
    "subject_field": "assertionProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "media-assertion",
    "subject_field": "mediaID",
    "predicate": "about",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "media-assertion",
    "subject_field": "assertionByID",
    "predicate": "asserted by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "media-assertion",
    "subject_field": "assertionProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "molecular-protocol-assertion",
    "subject_field": "molecularProtocolID",
    "predicate": "about",
    "related_table": "molecular-protocol",
    "related_field": "molecularProtocolID"
  },
  {
    "subject_table": "molecular-protocol-assertion",
    "subject_field": "assertionByID",
    "predicate": "asserted by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "molecular-protocol-assertion",
    "subject_field": "assertionProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "nucleotide-analysis-assertion",
    "subject_field": "nucleotideAnalysisID",
    "predicate": "about",
    "related_table": "nucleotide-analysis",
    "related_field": "nucleotideAnalysisID"
  },
  {
    "subject_table": "nucleotide-analysis-assertion",
    "subject_field": "assertionByID",
    "predicate": "asserted by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "nucleotide-analysis-assertion",
    "subject_field": "assertionProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "occurrence-assertion",
    "subject_field": "occurrenceID",
    "predicate": "about",
    "related_table": "occurrence",
    "related_field": "occurrenceID"
  },
  {
    "subject_table": "occurrence-assertion",
    "subject_field": "assertionByID",
    "predicate": "asserted by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "occurrence-assertion",
    "subject_field": "assertionProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "organism-assertion",
    "subject_field": "organismID",
    "predicate": "about",
    "related_table": "organism",
    "related_field": "organismID"
  },
  {
    "subject_table": "organism-assertion",
    "subject_field": "assertionByID",
    "predicate": "asserted by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "organism-assertion",
    "subject_field": "assertionProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "organism-interaction-assertion",
    "subject_field": "organismInteractionID",
    "predicate": "about",
    "related_table": "organism-interaction",
    "related_field": "organismInteractionID"
  },
  {
    "subject_table": "organism-interaction-assertion",
    "subject_field": "assertionByID",
    "predicate": "asserted by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "organism-interaction-assertion",
    "subject_field": "assertionProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "survey-assertion",
    "subject_field": "surveyID",
    "predicate": "about",
    "related_table": "survey",
    "related_field": "surveyID"
  },
  {
    "subject_table": "survey-assertion",
    "subject_field": "assertionByID",
    "predicate": "asserted by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "survey-assertion",
    "subject_field": "assertionProtocolID",
    "predicate": "followed",
    "related_table": "protocol",
    "related_field": "protocolID"
  },
  {
    "subject_table": "agent-identifier",
    "subject_field": "agentID",
    "predicate": "for",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "event-identifier",
    "subject_field": "eventID",
    "predicate": "for",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "material-identifier",
    "subject_field": "materialEntityID",
    "predicate": "for",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "media-identifier",
    "subject_field": "mediaID",
    "predicate": "for",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "occurrence-identifier",
    "subject_field": "occurrenceID",
    "predicate": "for",
    "related_table": "occurrence",
    "related_field": "occurrenceID"
  },
  {
    "subject_table": "organism-identifier",
    "subject_field": "organismID",
    "predicate": "for",
    "related_table": "organism",
    "related_field": "organismID"
  },
  {
    "subject_table": "survey-identifier",
    "subject_field": "surveyID",
    "predicate": "for",
    "related_table": "survey",
    "related_field": "surveyID"
  },
  {
    "subject_table": "provenance",
    "subject_field": "fundingAttributionID",
    "predicate": "funded by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "provenance",
    "subject_field": "creatorID",
    "predicate": "created by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "provenance",
    "subject_field": "providerID",
    "predicate": "provided by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "provenance",
    "subject_field": "metadataCreatorID",
    "predicate": "metadata created by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "provenance",
    "subject_field": "metadataProviderID",
    "predicate": "metadata provided by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "event-provenance",
    "subject_field": "provenanceID",
    "predicate": "has",
    "related_table": "provenance",
    "related_field": "provenanceID"
  },
  {
    "subject_table": "event-provenance",
    "subject_field": "eventID",
    "predicate": "for",
    "related_table": "event",
    "related_field": "eventID"
  },
  {
    "subject_table": "material-provenance",
    "subject_field": "provenanceID",
    "predicate": "has",
    "related_table": "provenance",
    "related_field": "provenanceID"
  },
  {
    "subject_table": "material-provenance",
    "subject_field": "materialEntityID",
    "predicate": "for",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "media-provenance",
    "subject_field": "provenanceID",
    "predicate": "has",
    "related_table": "provenance",
    "related_field": "provenanceID"
  },
  {
    "subject_table": "media-provenance",
    "subject_field": "mediaID",
    "predicate": "for",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "usage-policy",
    "subject_field": "rightsHolderID",
    "predicate": "rights held by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "usage-policy",
    "subject_field": "ownerID",
    "predicate": "owned by",
    "related_table": "agent",
    "related_field": "agentID"
  },
  {
    "subject_table": "material-usage-policy",
    "subject_field": "usagePolicyID",
    "predicate": "has",
    "related_table": "usage-policy",
    "related_field": "usagePolicyID"
  },
  {
    "subject_table": "material-usage-policy",
    "subject_field": "materialEntityID",
    "predicate": "for",
    "related_table": "material",
    "related_field": "materialEntityID"
  },
  {
    "subject_table": "media-usage-policy",
    "subject_field": "usagePolicyID",
    "predicate": "has",
    "related_table": "usage-policy",
    "related_field": "usagePolicyID"
  },
  {
    "subject_table": "media-usage-policy",
    "subject_field": "mediaID",
    "predicate": "for",
    "related_table": "media",
    "related_field": "mediaID"
  },
  {
    "subject_table": "organism-relationship",
    "subject_field": "subjectOrganismID",
    "predicate": "of",
    "related_table": "organism",
    "related_field": "organismID"
  },
  {
    "subject_table": "organism-relationship",
    "subject_field": "relatedOrganismID",
    "predicate": "to",
    "related_table": "organism",
    "related_field": "organismID"
  },
  {
    "subject_table": "organism-relationship",
    "subject_field": "relationshipAccordingToID",
    "predicate": "according to",
    "related_table": "agent",
    "related_field": "agentID"
  }
];
