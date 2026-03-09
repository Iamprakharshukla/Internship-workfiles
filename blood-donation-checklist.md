**CRITICAL Priority (Core Focus / Phase 1)**

*Features categorized as "Must-Have" for immediate implementation.*

- [ ]  **Emergency Request Handling**: Includes an emergency flag, auto-prioritization, and instant alerts.
    - *Django Feasibility: High. Easily implemented using Boolean fields for flags and Django Signals/Celery for triggering instant alerts.*
- [ ]  **Donor Management**: Features donor profiles, eligibility cooldown tracking, and an availability toggle. - admin.
    - *Django Feasibility: High. Standard Django user models combined with DateTime fields can natively handle cooldown logic and availability states.*
- [ ]  **DIN (Donation Identification Number)**: Requires auto-generation, search & verification, and an audit trail.
    - Django Feasibility: High. A `UUIDField` or a custom `save()` method can auto-generate the DIN, while packages like `django-simple-history` can maintain the immutable audit logs.
- [ ]  **Location-Based Matching**: Utilizes radius search, OpenStreetMap + Leaflet integration, and city/PIN filters. - admin
    - *Django Feasibility: High. Leaflet JS integrates perfectly into Django templates. GeoDjango (using PostGIS) makes radius queries highly efficient.*
- [ ]  **Trust, Safety & Compliance**: Implements consent and privacy controls with role-based access. -transparency
    - *Django Feasibility: High. Handled flawlessly by Django's built-in Authentication system and Group permissions.*

---

**HIGH Priority (Highly Feasible & High Impact / Phase 1 & 2)**

*Features categorized as "Should-Have" or core admin features that drastically improve the UX.*

- [ ]  **Admin Dashboard & Status Tracking**: Displays live requests, pending/completed counts, and overdue alerts. Tracks statuses linearly (Pending → In Progress → Fulfilled).
    - *Django Feasibility: High. Standard Django views passing aggregate ORM queries (e.g., `Count()`) to the template.*
- [ ]  **Quick Search & Filters**: Allows filtering by blood group, city, and urgency.
    - *Django Feasibility: High. The `django-filter` package combined with HTML forms in templates handles this out-of-the-box.*
- [ ]  **Notifications**: Sends Email/SMS alerts, confirmations, reminders, and status updates.
    - *Django Feasibility: High. Use Django's native Email backend; integrate a 3rd-party SMS API (like Twilio) via Celery for asynchronous processing.*
- [ ]  **Auto Task Creation & Priority Scoring**: Creates tasks automatically from new requests and scores priority based on urgency, time, distance, and availability.
    - *Django Feasibility: Medium-High. Django Signals can intercept new requests to auto-create tasks, while a custom model property can calculate the priority score on the fly.*
- [ ]  **Adverse Reaction Triage**: Includes triage workflows with escalation scripts.
    - *Django Feasibility: Medium. Can be built efficiently as a step-by-step form wizard using Django's FormTools.*

---

**MEDIUM Priority (Build the Core 20% / Phase 2 & 3)**

*Features categorized as "Nice-to-Have" or advanced automations better suited for later iterations.*

- [ ]  **Post-Donation Care**: Sends automated tips and follow-up check-ins.
    - *Django Feasibility: Medium. Requires setting up Celery Beat to run scheduled tasks that check donation dates and trigger emails.*
- [ ]  **Analytics, Export & No-Show Tracking**: Features an Impact Dashboard (time-to-match, donor participation) , no-show tracking , and CSV/Sheets export with calendar sync.
    - *Django Feasibility: Medium. Django handles CSV generation natively via the `csv` module. Dashboards can be rendered using a library like Chart.js embedded in the templates.*
- [ ]  **AI Summaries & Volunteer Assignment**: Generates a Weekly AI Summary of performance/delays and handles volunteer assignment with skill/location matching.
    - *Django Feasibility: Low-Medium. Requires integrating an external LLM API for the summaries and writing complex assignment algorithms, making it heavier to implement.*

---

# UI for blood donation checklist

**1. Global Navigation & Header**

- [ ]  **DIN Tracker Bar**: A simple search input in the header where users can paste their Donation Identification Number to check the status of a request or donation.
- [ ]  **Call-to-Action Buttons**: Sticky buttons for "Request Blood" and "Register as Donor" to ensure they are always accessible.

**2. "Request Blood" Form (Public View)**

- [ ]  **Urgency Toggle/Checkbox**: A highly visible switch to mark the request as an "Emergency". Backend tie-in: Sets the boolean flag to trigger auto-prioritization and instant alerts.
- [ ]  **Patient & Hospital Details**: Standard text inputs for Patient Name, Hospital Name, and required Units.
- [ ]  **Blood Group Dropdown**: Select menu for A+, B-, O+, etc.
- [ ]  **Location Inputs**: Fields for City and PIN code to enable location-based matching.
- [ ]  **Consent Checkbox**: Mandatory checkbox for data privacy and consent.
- [ ]  **Success Modal (Post-Submit)**: A pop-up that prominently displays the auto-generated DIN (Donation Identification Number) so the user can save it for tracking.

**3. "Register as Donor" Form (Public View)**

- [ ]  **Basic Info**: Inputs for Name, Phone Number, and Email.
- [ ]  **Blood Group Dropdown**: Select menu for their blood type.
- [ ]  **Location Details**: City and PIN code fields.
- [ ]  **Availability Toggle**: A switch allowing the donor to mark themselves as "Available to Donate Now".
- [ ]  **Consent & Privacy Checkbox**: Mandatory opt-in for receiving SMS/Email notifications and agreeing to privacy controls.

**4. Live Requests Board / Feed (The Core Interactive Area)**

- [ ]  **Quick Filters Bar**: A row of dropdowns above the feed allowing users to filter the visible cards by Blood Group, City, and Urgency.
- [ ]  **View Toggle (List vs. Map)**: A button to switch between a standard card list and an OpenStreetMap + Leaflet map view.
- [ ]  **Request Cards**: Individual cards for each active request featuring:
    - Blood Group (Large, bold text).
    - Location (City/Hospital).
    - **Urgency Badge**: Red for Emergency, Yellow for Standard.
    - **Status Badge**: Color-coded labels showing *Pending* or *In Progress*.
    - "I Can Donate" Button: Triggers a quick form or WhatsApp redirect for registered donors to claim the task.

**5. Trust & Footer Elements**

- [ ]  **Impact Counters (Static or Dynamic)**: Simple text or counter UI showing "Lives Saved" or "Active Donors" to build trust, feeding from your Analytics/Impact Dashboard data.
- [ ]  **PWA Prompt**: A small, unobtrusive banner or button prompting mobile users to "Add to Home Screen" for low-bandwidth access.

### 🩸 Educational & Support UI Checklist

**6. "How It Works" / Tutorial Guide (Visual Stepper)**

*Instead of a wall of text, use a visually appealing horizontal timeline or vertical stepper.*

- [ ]  **Step 1: Check Eligibility UI**: A quick graphic showing age/weight requirements.
- [ ]  **Step 2: Find a Match UI**: An icon representing the location-based matching.
- [ ]  **Step 3: Donate UI**: A brief note on what happens at the clinic.
- [ ]  **Step 4: Save a Life UI**: A celebratory graphic.
- *Django Tie-in*: This is strictly static frontend HTML/CSS, making it incredibly lightweight to render in your Django templates.

**7. Pre-Donation Eligibility Questionnaire (Interactive)**
Instead of just letting anyone fill out the "Register as Donor" form, guide them through a quick self-check. This directly supports your "Donor Management: eligibility" requirement.

- [ ]  **Interactive Yes/No Quiz**: A simple card-based UI asking:
    - *Are you between 18-65 years old?*
    - *Do you weigh more than 50kg?*
    - *Have you gotten a tattoo in the last 6 months?*
    - Have you donated blood in the last 3 months? (Cooldown tracking)
- [ ]  **Dynamic Result UI**: If they click a disqualifying answer (like "Yes" to recent tattoos), the UI gently disables the registration form and explains why, saving backend validation load.

**8. Health & Wellness "Rant" (Prep & Post-Donation Care)**
This section covers what to eat, how to stay healthy, and what to do after donating. This perfectly sets up your "Post-Donation Care: Automated tips" feature.

- [ ]  **"Before You Donate" Info Cards**:
    - 💧 *Hydration icon*: "Drink plenty of water."
    - 🥦 *Diet icon*: "Eat iron-rich foods (spinach, beans, red meat)."
    - 🛌 *Sleep icon*: "Get at least 8 hours of sleep."
- [ ]  **"After You Donate" Info Cards**:
    - 🛑 *Warning icon*: "Avoid heavy lifting for 24 hours."
    - 🧃 *Snack icon*: "Keep the bandage on and eat sugary snacks if feeling dizzy."
- *Django Tie-in*: You can store these tips in a Django `ContentBlock` model so your NGO admins can easily update the advice via the Django Admin Dashboard without touching the HTML.

**9. Comprehensive FAQ Section (Accordion UI)**

*Collapsible panels to keep the page clean while offering deep information.*

- [ ]  **Pain & Safety**: "Does it hurt?", "Is the equipment safe?" (Reinforcing Trust, Safety & Compliance ).
- [ ]  **Time Commitment**: "How long does the process take?"
- [ ]  **Blood Group Compatibility**: A simple visual matrix or table showing who can donate to whom (e.g., O- is universal).
- [ ]  **Emergency Requests**: "What does the Emergency tag mean on a request?" (Explaining the Emergency flag feature ).

**10. Trust & Compliance Badges (Footer/Sidebar)**

*Visual reassurance for donors and requesters.*

- [ ]  **Data Privacy Badge**: A small shield icon stating "Your data is encrypted and private," tying into your "Consent & Privacy Controls".
- [ ]  **NGO / Hospital Partner Logos**: A banner showing verified partner hospitals to build legitimacy.
