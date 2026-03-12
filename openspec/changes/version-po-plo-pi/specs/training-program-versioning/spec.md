## MODIFIED Requirements

### Requirement: Academic Year Versioning for Training Programs

The system SHALL allow creation of discrete versions of a Training Program bound to a specific academic year.

#### Scenario: Admin creates a new program version from scratch

- **WHEN** an administrator creates a new Training Program Version for an existing Training Program without specifying a source version
- **THEN** an empty version is created in the Draft state with the specified academic year

#### Scenario: Admin clones an existing program version

- **WHEN** an administrator creates a new Training Program Version and selects a previous version to clone
- **THEN** the system creates a new version in the Draft state and deep-copies all KnowledgeBlocks, CourseGroups, ProgramCourses, ProgramObjectives, ProgramLearningOutcomes, PerformanceIndicators, PLOPOMappings, PLOAssessmentPlans, SemesterPlans, and CoursePLOContributions into the new version with correctly remapped foreign keys

### Requirement: Version-scoped Program Structure

The system SHALL scope all curriculum structures (KnowledgeBlocks, CourseGroups, ProgramCourses, ProgramObjectives, ProgramLearningOutcomes, PerformanceIndicators, PLOAssessmentPlans) strictly to a Training Program Version rather than the parent Training Program.

#### Scenario: Fetching knowledge blocks

- **WHEN** a user or API requests the knowledge blocks for a training program
- **THEN** the request must specify the version, or the system defaults to the most recent version, returning only blocks belonging to that specific version

#### Scenario: Fetching POs/PLOs/PIs for a version

- **WHEN** a user or API requests POs, PLOs, or PIs for a training program
- **THEN** the system returns only records belonging to the specified or default version

#### Scenario: Course code evolution

- **WHEN** the credit requirement for a globally shared Course changes
- **THEN** the administrator must create a new global Course record and assign it to the Draft version of the new academic year's Training Program Version, leaving the older version unaffected
