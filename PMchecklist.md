# Project Management & CRM Feature Checklist

This document tracks the implementation status of the Project Management (PM) and Customer Relationship Management (CRM) features within the UDAAN Society portal.

## 1. Project Management (PM) Suite

### Core Task Management
- [x] **Task Creation & Assignment**: Admins/Managers can assign tasks to staff via Django Admin. (Model: `Task`)
- [x] **Task Status Tracking**: Staff can update status (`To Do` -> `In Progress` -> `Done`) via Dashboard.
- [x] **Prioritization**: Tasks support `High`, `Medium`, `Low`, `Critical` priorities with visual badges.
- [x] **Sub-Tasks**: Database model supports task decomposition.
  - [x] *Pending*: UI validation to view/edit sub-tasks in the portal.
- [x] **Team View**: Managers can view all tasks across the organization.

### Dashboards & Views
- [x] **Staff Dashboard**: Personalized Kanban-style view of assigned tasks.
- [x] **Manager Dashboard**: High-level overview of organization-wide tasks.
- [x] **Announcements**: Digital bulletin board for staff alerts.
- [x] **Advanced Filtering**: Filtering tasks by project, date range, or specific assignee in the frontend.

### Field Operations (GPS)
- [x] **Data Structure**: `Task` model includes `completion_lat`, `completion_lng`, and timestamp fields.
- [x] **GPS Logic**: Frontend integration to capture geolocation when marking a task as "Done".

---

## 2. CRM (Constituent Relationship Management)

### Donor & Constituent Management
- [x] **Blood Donor Database**: Centralized storage of donor profiles (`BloodDonor` model).
- [x] **Donor Search API**: Basic API endpoint (`search_donors`) for filtering by blood group/city.
- [x] **Staff Profiles**: Linkage between User accounts and phone numbers for coordination.

### Interaction Tracking (Biziverse-Style)
- [x] **Interaction Model**: Database structure to log Calls, Meetings, Emails, and Visits (`Interaction` model).
- [x] **Outcome Tracking**: Support for outcomes like "Interested", "Follow-up", "Closed".
- [x] **Interaction Logging UI**: Frontend forms for staff to record calls/meetings.
- [x] **Auto-Task Generation**: Logic to automatically create follow-up tasks based on interaction outcomes.

### Scheduling
- [x] **Appointment Calendar**: Visual calendar for upcoming meetings/drives.
- [x] **Reminders**: Automated email/SMS reminders for scheduled interactions.

---

## 3. NGO Operations (Data & CMS)

### Dynamic Content
- [x] **Campaigns Management**: Create/Edit fundraising campaigns via Admin.
- [x] **Projects Management**: Create/Edit NGO projects via Admin (with Slug & Rich Text).
- [x] **Blood Requests**: Public form for blood requests and backend management.

### Reporting
- [x] **Basic Stats**: Dashboard counters for Active Tasks.
- [x] **Export**: Ability to export task lists or task reports to CSV/Excel.

---

## 4. Advanced Features (Biziverse & Zoho Style)

### Biziverse Interconnectedness (Unified Interactions)
- [x] **Interaction Logging**: Calls/Emails/Meetings tracking (partially done in CRM).
- [x] **Timeline View**: A single view showing history of a any task or log  (donations, calls, tasks).

### Zoho Workflow Rules (Automated Workflows)
- [X] **Data Model**: Configurable "Rules" model (Trigger -> Condition -> Action).
- [X] **Execution Engine**: Celery task to process rules (e.g., "If Last Donation > 90 days, Email Donor").

### Zoho Blueprint (Process Enforcement)
- [X] **Finite State Machine**: Strict process states (Screening -> Donation -> Rest).
- [X] **Transition Guards**: Logic to prevent skipping steps (e.g., cannot Donate without Screening).

### Zoho Zia (Intelligence Layer)
- [x] **Donor Scoring**: Script to calculate engagement score (Recency/Frequency).
- [x] **Heuristic Suggestions**: "Best time to call" based on donor history.

### Zoho Canvas (Visual Design)
- [ ] **Card UI**: Visual representation of records (already using Tailwind, can be enhanced).
- [ ] **htmx Integration**: Real-time state updates on cards without reloading.

### Omnichannel Alerts
- [ ] **Notification Center**: Centralized module for routing alerts.
- [ ] **Multi-Channel**: SMS (Twilio), WhatsApp, and Email support.


Phase 25: The Notion-Style Workspace (Collaboration & Docs)
 Slash Commands (/) in Notes
 Integrate custom block editor or extend CKEditor
 Implement UI popover for / command
 Action: Insert Task, Insert Table, Insert File
 Team Wikis & Knowledge Bases
 Add parent/child hierarchy to SharedNote
 UI for Wiki navigation sidebar
 Database Multi-Views
 Implement List/Calendar/Gallery views alongside Kanban
Phase 26: The Zoho-Style CRM (Relationships)
 Donor Pipelines / Funnels
 Design pipeline stages (New, Nurture, Retain)
 Interactive Drag-and-Drop Pipeline View
 Automated Communication (Drip)
 Rule engine for time-delayed emails/WhatsApp
 Omnichannel Inbox
 Integrate Email/SMS sending from Donor profile
 Donor Health Scoring (Zoho Zia)
 Predictive script for retention likelihood
Phase 27: The Biziverse-Style MIS (Analytics)
 Custom Dashboard Builder
 Draggable/Resizable widget grid for Managers
 Advanced Audit Trails
 Install/Configure django-simple-history
 Audit log UI view
 Expense Tracking
 Create Expense model linked to Campaigns
Phase 28: Immediate Wins (High Value / Low Effort)
 Mentions (@username)
 Parse @ in notes/comments
 Trigger Portal Notification
 Global Keyboard Shortcuts
 Hotkey 'C' to open Quick Add Task modal
 Recurring Tasks
 Add recurrence logic/cron job for Ops workloads
