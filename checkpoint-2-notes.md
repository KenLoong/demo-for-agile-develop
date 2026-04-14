# 1. App Pitch

## Project Title
**UWA Skill-Swap**

## Problem
UWA students often want to learn practical skills from peers, but there is no simple platform dedicated to skill exchange within the university community.

## Target Users
The main users are UWA students who want to either teach a skill, learn a skill, or connect with other students who share similar interests.

## Scope
UWA Skill-Swap is a web application where students can create posts offering skills, browse posts created by others, search and filter available skills, comment on posts, and express interest in learning from another student. The project is designed to satisfy the course requirements of client-server architecture, authentication, persistent user data, and user interaction.

---

# 2. User Stories

## Authentication User Stories
1. As a UWA student, I want to register with my UWA email address so that I can create a secure account on the platform.
2. As a registered user, I want to log in to my account so that I can access protected features such as creating posts and managing my dashboard.
3. As a logged-in user, I want to log out of my account so that my session remains secure on shared devices.

## Posting User Stories
4. As a user, I want to create a skill post so that I can offer my skills to other students.
5. As a user, I want to edit my own skill post so that I can keep the information accurate and up to date.
6. As a user, I want to delete my own skill post so that I can remove listings that are no longer relevant.

## Discovery, Search, and Filter User Stories
7. As a user, I want to browse all available skill posts so that I can discover useful learning opportunities.
8. As a user, I want to search posts by keyword so that I can quickly find skills related to my interests.
9. As a user, I want to filter posts by category so that I can narrow down results and browse more efficiently.

## Comment and Interaction User Stories
10. As a user, I want to comment on a post so that I can ask questions or request more details before expressing interest.
11. As a user, I want to express interest in another user’s skill post so that I can connect with them for a possible skill exchange.

## Dashboard User Stories
12. As a user, I want to view my dashboard so that I can manage my own posts, view incoming requests, and track requests I have sent.

## Edge Case User Stories
13. As a user, I want the system to prevent me from expressing interest in my own post so that the feature is used appropriately.
14. As a user, I want the system to prevent duplicate interest requests on the same post so that the dashboard remains clear and accurate.
15. As a user, I want protected pages to require login so that unauthorised users cannot access private features.

---

# 3. Main Pages and Purpose

1. **Home / Discovery Page** – Displays all available skill posts with search and category filtering.
2. **Login Page** – Allows existing users to sign in to their account.
3. **Register Page** – Allows new users to create an account using their details.
4. **Create Post Page** – Allows a logged-in user to create a new skill listing.
5. **Edit Post Page** – Allows a logged-in user to update one of their existing posts.
6. **Post Detail Page** – Shows the full post description, creator information, comments, and interest action.
7. **Dashboard Page** – Lets users manage their posts, incoming requests, and sent requests.
8. **Profile Page** – Shows basic public information about a user and their posted skills.
9. **Error Page** – Informs users when a page cannot be found or accessed properly.

---

# 4. CSS Framework Choice

## Selected Framework
**Bootstrap 5**

## Reason for Choice
We have chosen Bootstrap 5 because it provides a consistent set of responsive layout tools and reusable UI components such as navbars, forms, buttons, cards, and grids. This helps the team maintain a professional and uniform design while developing pages efficiently. Bootstrap also reduces styling inconsistencies across members’ work and makes it easier to support both desktop and mobile screens.

---

# 5. Team Organisation

## Meeting Rhythm
Our team meets regularly each week to review progress, assign tasks, and prepare for upcoming checkpoints.

## Roles
We divide work across frontend, backend, and database responsibilities so that each member has a clear contribution area while still collaborating on integration.

## Communication Channel
We use Microsoft Teams for communication, including chat messages and calls.

## Task Tracking
We use GitHub to manage the project, including commits, branches, pull requests, and issue tracking. This supports the course expectation that GitHub activity is part of the agile development process assessment.

---

# 6. Must-Have Checklist from the Information and FAQs


- **Client-server architecture**  
  **Status:** Planned  
  **Notes:** Flask backend with HTML/CSS/JS frontend

- **Login and logout**  
  **Status:** Planned  
  **Notes:** Authentication module included

- **Persistent user data**  
  **Status:** Planned  
  **Notes:** SQLite + SQLAlchemy

- **Users can view data from other users**  
  **Status:** Covered  
  **Notes:** Users can browse posts, comments, and requests

- **Engaging design**  
  **Status:** In progress  
  **Notes:** Bootstrap-based responsive UI

- **Effective value for users**  
  **Status:** Covered  
  **Notes:** Supports student learning and community

- **Intuitive navigation**  
  **Status:** In progress  
  **Notes:** Main pages and clear layout planned

- **Public GitHub repository**  
  **Status:** In progress  
  **Notes:** Repository used for collaboration

- **README with app purpose**  
  **Status:** To do  
  **Notes:** Will be included before submission

- **README with member table**  
  **Status:** To do  
  **Notes:** Will include UWA ID, name, GitHub username

- **README with launch instructions**  
  **Status:** To do  
  **Notes:** Needed before final submission

- **README with test instructions**  
  **Status:** To do  
  **Notes:** Needed before final submission


---

# 7. Gaps and Action Items

## Current Gaps
Some required items are planned but not yet fully implemented at the checkpoint stage, especially backend functionality, full persistence, and final README/testing content. The brief also makes clear that the project will be assessed across checkpoints, with frontend planning in Checkpoint 2 and backend implementation later.

## Action Items with Owners

- **Finalise 10+ formal user stories in project document** — Whole team
- **Complete frontend mock-up pages for checkpoint demo** — Frontend lead
- **Confirm Bootstrap styling consistency across pages** — Frontend lead
- **Define SQLAlchemy models for User, Post, Category, Comment, Interest** — Backend/Database lead
- **Prepare login/logout and protected route plan** — Backend lead
- **Create GitHub Issues for each feature group** — Project coordinator
- **Add README draft with project purpose and setup outline** — Documentation owner
- **Prepare screenshots or live demo setup for checkpoint** — Whole team
- **Confirm roles and speaking order for the meeting** — Whole team
