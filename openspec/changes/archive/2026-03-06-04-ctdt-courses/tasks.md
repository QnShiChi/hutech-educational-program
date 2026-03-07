# Tasks: 04 - Course Management

## 1. Models

- [x] 1.1 Create Course model
- [x] 1.2 Create CourseGroup model
- [x] 1.3 Create ProgramCourse model
- [x] 1.4 Create CoursePrerequisite model
- [x] 1.5 Create SemesterPlan model
- [x] 1.6 Migrations + Admin registration

## 2. APIs

- [x] 2.1 CourseViewSet (CRUD, filter by department/group, search by code/name)
- [x] 2.2 CourseGroupViewSet (CRUD)
- [x] 2.3 ProgramCourseViewSet (nested under program, bulk add)
- [x] 2.4 PrerequisiteView (GET/PUT all prerequisites for a CTDT)
- [x] 2.5 SemesterPlanView (GET/PUT full 8-semester plan)
- [x] 2.6 Course usage endpoint: /courses/{id}/programs/

## 3. Business Logic

- [x] 3.1 Validate credit sum: total = theory + practice + project + internship
- [x] 3.2 Validate prerequisite semester ordering
- [x] 3.3 Notification trigger when Course changes (signal)
- [x] 3.4 Prevent delete if Course used in non-DRAFT CTDT

## 4. Tests

- [x] 4.1 Course CRUD + unique code validation
- [x] 4.2 ProgramCourse bulk add
- [x] 4.3 Prerequisite validation
- [x] 4.4 Semester plan update
- [x] 4.5 Course change notification trigger
