# TaskFlow -- SaaS Project Blueprint

## Overview

TaskFlow is a **Project Management SaaS** inspired by Jira, Trello, and
Notion. It enables organizations to manage projects, collaborate through
tasks, comments, notifications, and dashboards.

------------------------------------------------------------------------

# Goal

Build a production-style backend using:

-   Python
-   Django
-   Django REST Framework
-   PostgreSQL
-   JWT Authentication

Later versions:

-   Redis
-   Celery
-   Docker
-   Cloudinary
-   Gemini/OpenAI API

------------------------------------------------------------------------

# Release Plan (at ~3 hrs/day, 5-6 days/week)

Phases are grouped by release so the project is demoable and job-application-ready
long before every phase is finished. Do not wait for v3 to start applying.

## MVP -- Phases 1-7 (~3-4 weeks)
Auth, Profile, Workspace, Members & Roles, Projects, Boards, Tasks, Comments.
This is the "I can demo this in an interview" milestone. RBAC + core task
management working end-to-end.

## v2 -- Phases 8-12 (~2 weeks)
Attachments, Notifications, Activity Log, Dashboard, Search & Filters.
Adds the "product" feel and the ORM aggregation skills recruiters probe for.

## v3 -- Phases 13-16 (~2 weeks)
AI Features, Redis + Celery, Docker, CI/CD + Deployment.
Build this in parallel with interviewing, not before it.

**Full project estimate: ~7-9 weeks.** Ship MVP, start applying, keep building.

------------------------------------------------------------------------

# AI Usage Boundary

Explicit rule so this doesn't drift under deadline pressure.

**Code it myself (no AI-generated logic):**
-   RBAC / permission classes (Phase 3)
-   Task status & board-move business rules (Phase 6)
-   Dashboard aggregation queries (Phase 11)
-   Any ownership/duplicate-prevention validation

**AI help is fine for:**
-   Standard serializers / viewsets for simple CRUD models
-   URL routing, admin.py registration, migrations boilerplate
-   Syntax lookups when I know *what* I want, not *how*
-   Debugging a specific traceback I've already tried to diagnose

------------------------------------------------------------------------

# Open Decisions (resolve before starting the relevant phase)

These are gaps the original blueprint doesn't specify. Each has real
architectural consequences, so decide deliberately, don't default silently.

1. **Attachments (Phase 8):** local disk storage vs. S3/Cloudinary?
   Affects how the upload logic and `file` field are written.
2. **Notifications (Phase 9):** in-app only, or in-app + email?
   If email, Celery is needed earlier than Phase 14.
3. **Task assignment:** single assignee (`ForeignKey`) or multiple
   (`ManyToMany`)? Affects the model field and the permission logic
   around "who can edit this task."

------------------------------------------------------------------------

# Development Roadmap

## Phase 1 -- Authentication

### Features

-   User Registration
-   Login
-   Logout
-   JWT Authentication
-   User Profile
-   Password Hashing
-   Forgot Password (optional)

### Models

-   User
-   Profile

### Definition of Done
User can register, login, logout, and receive/refresh a JWT. Profile is
auto-created on registration. Password reset is deferred to v2 unless
explicitly pulled forward.

------------------------------------------------------------------------

## Phase 2 -- Workspace

A workspace represents a company/team.

Example:

-   OpenAI
-   Microsoft
-   Startup XYZ

### Models

Workspace - name - description - owner - created_at

### Definition of Done
Authenticated user can create a workspace and is automatically set as
owner. Only the owner (for now) can view/edit/delete it.

------------------------------------------------------------------------

## Phase 3 -- Workspace Members

Invite users into a workspace.

### Roles

-   Owner
-   Admin
-   Manager
-   Developer
-   Viewer

### Business Rules

-   One owner
-   Multiple admins
-   Role-based permissions

### Definition of Done
Owner can invite a user to a workspace with a role. Permission classes
enforce role-based access on at least one protected endpoint (proof the
RBAC actually works, not just modeled).

------------------------------------------------------------------------

## Phase 4 -- Projects

A workspace contains multiple projects.

Examples

-   Backend API
-   Mobile App
-   Admin Panel

### Model

Project - workspace - name - description - created_by

### Definition of Done
Workspace member with sufficient role can create/list/edit/delete
projects scoped to their workspace only (no cross-workspace leakage).

------------------------------------------------------------------------

## Phase 5 -- Boards

Each project has boards.

Examples

-   Backlog
-   Sprint 1
-   Sprint 2
-   Completed

### Definition of Done
Boards CRUD scoped to a project. A project can have multiple boards.

------------------------------------------------------------------------

## Phase 6 -- Tasks

### Model

Task

-   title
-   description
-   project
-   board
-   assigned_to
-   reporter
-   priority
-   status
-   deadline
-   created_at
-   updated_at

### Status

-   Todo
-   In Progress
-   Review
-   Done

### Priority

-   Low
-   Medium
-   High
-   Critical

### Business Rules

-   Assign task
-   Move between boards
-   Change status
-   Edit/Delete only by authorized users

### Definition of Done
Task CRUD with status/priority working. Assignment and board-move logic
enforce permissions (not just any workspace member can move any task).
Assignee cardinality decided per Open Decisions above.

------------------------------------------------------------------------

## Phase 7 -- Comments

Every task supports discussion.

Model

Comment

-   task
-   user
-   message
-   created_at

### Definition of Done
Users can comment on a task they have access to. **This completes the
MVP -- stop here, deploy, and consider applying to jobs before continuing.**

------------------------------------------------------------------------

## Phase 8 -- Attachments

Upload

-   Images
-   PDF
-   Documents
-   ZIP

Model

Attachment

-   task
-   uploaded_by
-   file
-   uploaded_at

### Definition of Done
Files upload to the storage backend decided in Open Decisions, with
type/size validation. Files are only visible to users with task access.

------------------------------------------------------------------------

## Phase 9 -- Notifications

Examples

-   Task Assigned
-   Comment Added
-   Status Changed
-   Deadline Reminder

Model

Notification

-   user
-   message
-   is_read
-   created_at

### Definition of Done
Notification created on the four listed trigger events, deliverable
channel per Open Decisions, and markable as read.
------------------------------------------------------------------------

## Phase 10 -- Activity Log

Track every important action.

Examples

-   Task Created
-   Task Updated
-   Status Changed
-   File Uploaded

Model

ActivityLog

-   user
-   action
-   task
-   timestamp

### Definition of Done
Every listed action type writes an ActivityLog entry, queryable per task
and per workspace.

------------------------------------------------------------------------

## Phase 11 -- Dashboard

Display

-   Total Projects
-   Total Tasks
-   Completed Tasks
-   Pending Tasks
-   Overdue Tasks
-   Tasks Per Member

Use

-   Aggregate
-   Annotate
-   Count
-   Avg

### Definition of Done
Dashboard endpoint returns all six listed metrics for a workspace using
`select_related`/`prefetch_related` and `annotate` -- not N+1 loops in
Python. This is the phase to be able to explain query-count reasoning in
an interview.

------------------------------------------------------------------------

## Phase 12 -- Search & Filters

Search

-   Projects
-   Tasks
-   Members

Filters

-   Status
-   Priority
-   Deadline
-   Assigned User

Pagination

Ordering

### Definition of Done
Task/project list endpoints support search, the four listed filters,
pagination, and ordering together in a single query param combination.
**This completes v2.**

------------------------------------------------------------------------

## REST APIs

Authentication API

Workspace API

Project API

Board API

Task API

Comment API

Attachment API

Notification API

Dashboard API

Search API

------------------------------------------------------------------------

## Permissions

Workspace Owner

-   Full access

Admin

-   Manage members
-   Manage projects

Developer

-   Manage assigned tasks

Viewer

-   Read only

------------------------------------------------------------------------

## Database Relationships

User └── Profile

Workspace └── WorkspaceMember

Workspace └── Project

Project └── Board

Board └── Task

Task ├── Comment ├── Attachment ├── Notification └── ActivityLog

------------------------------------------------------------------------

## Backend Concepts Covered

-   Django Models
-   ForeignKey
-   OneToOne
-   ManyToMany
-   Related Names
-   Custom Permissions
-   Business Logic
-   JWT
-   REST APIs
-   Pagination
-   Search
-   Filtering
-   PostgreSQL
-   File Uploads
-   Activity Logs
-   Notifications

------------------------------------------------------------------------

## Future Enhancements

### AI

-   Generate task descriptions
-   Break features into subtasks
-   Summarize project progress
-   Generate sprint reports

### Infrastructure

-   Redis
-   Celery
-   Docker
-   Cloudinary
-   Email Notifications

------------------------------------------------------------------------

## Suggested Build Order

1.  Authentication
2.  Profile
3.  Workspace
4.  Members & Roles
5.  Projects
6.  Boards
7.  Tasks
8.  Comments
9.  Attachments
10. Notifications
11. Activity Logs
12. Dashboard
13. Search & Filters
14. REST APIs
15. AI Features
16. Deployment

------------------------------------------------------------------------

## End Goal

A production-style SaaS backend demonstrating:

-   Authentication
-   Authorization
-   Role-Based Access Control
-   Complex ORM Relationships
-   REST APIs
-   PostgreSQL
-   Business Logic
-   Search
-   Analytics
-   Scalable Architecture

Suitable as a flagship Python Backend portfolio project.
