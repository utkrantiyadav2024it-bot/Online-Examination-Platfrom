Yes. For the **Faculty portal**, I would go deeper than simply adding a few buttons to the current screens. The Faculty portal is the **academic-control layer** of the system:

> **Faculty creates academic content → builds exam → schedules it → students register/attempt → faculty monitors submissions → evaluates → finalizes/publishes results → analyzes performance.**

The screenshots you showed already cover some of this, but there are several important gaps and a few things that are currently misleading.

---

# **1\. First: What the Faculty portal should actually be responsible for**

The Faculty should own these areas:

FACULTY PORTAL

├── Dashboard  
├── Question Bank  
├── Exam Management  
├── Evaluations  
├── Subjects  
├── Analytics  
├── Notifications  
└── Profile

But the **logical workflow** is:

Subject  
   ↓  
Question Bank  
   ↓  
Create Questions  
   ↓  
Create Exam  
   ↓  
Attach Questions  
   ↓  
Configure Rules  
   ↓  
Schedule Exam  
   ↓  
Publish / Open Registration  
   ↓  
Students Register  
   ↓  
Students Attempt  
   ↓  
Submissions  
   ↓  
Auto Evaluation  
   ↓  
Faculty Evaluation  
   ↓  
Finalize Result  
   ↓  
Publish Result  
   ↓  
Analytics

Your current UI does not make this lifecycle sufficiently obvious.

That is the biggest Faculty-side issue.

---

# **2\. Recommended Faculty sidebar**

Your current sidebar is:

Dashboard  
Question Bank  
Exam Management  
Evaluations  
Subjects  
Analytics

That is actually a good foundation.

I would keep it, but change the order slightly:

┌─────────────────────────┐  
│ 🎓 MMCOE Exam           │  
├─────────────────────────┤  
│ FACULTY PORTAL          │  
│                         │  
│ ▣ Dashboard             │  
│ 📚 Question Bank        │  
│ 📝 Exam Management      │  
│ ✓ Evaluations           │  
│ 📖 Subjects             │  
│ 📊 Analytics            │  
│                         │  
│                         │  
│ 👤 Profile              │  
│ 🚪 Logout               │  
└─────────────────────────┘

Notifications stay in the top header.

---

# **3\. Faculty Dashboard — what it should actually answer**

The current dashboard is visually decent, but it is too much of a **static summary**.

A Faculty member should immediately know:

1\. What exams are active/upcoming?  
2\. Which exams need attention?  
3\. How many students are registered?  
4\. Are there submissions waiting for evaluation?  
5\. Are there integrity issues?  
6\. What exams/results were recently published?  
7\. What questions/exams need completion?

So the dashboard should be reorganized around **actions and alerts**, not just numbers.

---

# **4\. Recommended Faculty dashboard layout**

I would make it:

┌──────────────────────────────────────────────────────────────┐  
│ Welcome, Dr. Rajesh Sharma                                  │  
│ Department of Computer Engineering                           │  
│                                                              │  
│ \[+ Create Exam\] \[+ Add Question\]                            │  
├──────────────────────────────────────────────────────────────┤  
│                                                              │  
│ \[ Active Exams \] \[ Upcoming Exams \] \[ Pending Evaluation \]  │  
│ \[ Registered Students \]                                      │  
│                                                              │  
├────────────────────────────────┬─────────────────────────────┤  
│ Upcoming / Active Exams        │ Attention Required          │  
│                                │                             │  
│ DBMS Mid-Term                  │ ⚠ 2 submissions pending    │  
│ Today 2:00 PM                  │ ⚠ 1 integrity review       │  
│ 2 candidates                   │                             │  
│ \[Manage Exam\] \[Monitor\]        │ \[Review Now\]                │  
│                                │                             │  
│ Full Stack Internal            │                             │  
│ Sept 10 • 10 AM                │                             │  
│ \[Manage Exam\]                  │                             │  
├────────────────────────────────┴─────────────────────────────┤  
│                                                              │  
│ Recent Submissions                                           │  
│ Student | Exam | Submitted | Score | Integrity | Action     │  
│                                                              │  
├──────────────────────────────────────────────────────────────┤  
│ Recent Activity                                              │  
│ Question created                                             │  
│ Exam scheduled                                               │  
│ Result published                                             │  
└──────────────────────────────────────────────────────────────┘  
---

# **5\. Fix the current dashboard cards**

Currently you have:

2 Assigned Subjects  
2 Questions Created  
2 Pending Evaluations  
2 Enrolled Candidates

The problem is that these are not equally useful.

I'd change them to:

### **Card 1**

Active / Upcoming Exams  
2

### **Card 2**

Questions in Bank  
24

### **Card 3**

Pending Evaluations  
2

### **Card 4**

Registered Candidates  
42

Clicking each card should take the Faculty directly to the relevant filtered page.

For example:

Pending Evaluations: 2  
        ↓  
Evaluations  
        ↓  
status \= PENDING  
---

# **6\. Add "Attention Required"**

This is currently missing.

A Faculty dashboard should not make faculty search through six modules to find problems.

Add:

Attention Required

with things like:

🔴 2 evaluations pending  
🟠 Exam starts in 30 minutes  
🟠 3 integrity events require review  
🟡 DBMS exam has only 8/20 questions  
🟡 Result awaiting publication

This is much more useful than a generic activity feed.

---

# **7\. Upcoming Exams widget**

This should be directly below the summary cards.

Example:

Upcoming & Active Exams

┌──────────────────────────────────────────────────────────────┐  
│ DBMS Mid-Term Assessment                                    │  
│ CS101 • Today, 2:00 PM – 3:00 PM                            │  
│ 2 registered • 20 questions                                 │  
│                                                              │  
│ Status: ACTIVE                                               │  
│                                                              │  
│ \[Monitor Exam\] \[View Details\]                               │  
└──────────────────────────────────────────────────────────────┘

For upcoming:

Status: Scheduled

\[Manage\] \[View Registrations\]  
---

# **8\. Add an exam status lifecycle**

This is essential.

Faculty should see:

DRAFT  
SCHEDULED  
REGISTRATION\_OPEN  
REGISTRATION\_CLOSED  
LIVE  
COMPLETED  
EVALUATION\_PENDING  
EVALUATED  
PUBLISHED  
CANCELLED

You don't necessarily have to expose every technical status in the UI, but the system needs a clear lifecycle.

---

# **9\. Exam Management is currently incomplete**

Your current screenshots show:

> Design & Schedule Examination

with:

Step 1 Basic Details  
Step 2 Scoring & Rules  
Step 3 Schedule & Entry

That's good, but **the workflow is incomplete**.

You need at least:

Step 1 → Basic Details  
Step 2 → Scoring & Rules  
Step 3 → Schedule & Entry  
Step 4 → Question Selection  
Step 5 → Review & Publish

This is one of the biggest changes I would make.

---

# **10\. Step 1 — Basic Details**

Current fields:

Subject  
Exam Code  
Exam Title  
Assessment Type  
Duration  
Initial Status  
Instructions

Good foundation.

But I would change:

### **Remove editable "Initial Status"**

Faculty shouldn't casually select:

SCHEDULED

before actually completing scheduling.

Instead:

Status: Draft

is automatically assigned.

The system determines status based on actions.

---

# **11\. Step 1 should add exam description**

Add:

Exam Description

Optional, but useful.

Example:

Mid-semester assessment covering SQL queries,  
normalization and transaction management.  
---

# **12\. Step 1 should show academic ownership**

Display:

Subject  
Faculty  
Department  
Academic Year / Semester

Faculty shouldn't manually select themselves.

Backend derives:

authenticated faculty → faculty\_id  
---

# **13\. Step 2 — Scoring & Rules**

Your current screen has:

Total Marks  
Passing Marks  
Maximum Attempts

Shuffle Questions  
Shuffle Options  
Negative Marking  
Negative Marks

Good.

But there is a serious issue:

### **Total marks should not be independently inconsistent with questions.**

Suppose:

20 questions × 5 marks \= 100

but Faculty enters:

Total Marks \= 80

What happens?

You need validation.

I'd display:

Question Marks  
────────────────────  
Selected Questions: 20  
Calculated Marks: 100  
Exam Total: 100

or allow section/question-specific marks if your database supports it.

---

# **14\. Add pass percentage/marks validation**

For:

Passing Marks

enforce:

0 \< passing\_marks \<= total\_marks

The UI should immediately show:

Passing marks cannot exceed total marks.  
---

# **15\. Negative marking needs better UI**

Current:

Enable Negative Marking  
Negative Marks Per Wrong Question

If disabled, the negative marks field should become disabled.

If enabled:

Negative Marking  
☑ Enabled

Deduction:  
\[ 0.25 \]

Preview:  
Wrong answer → \-0.25 marks

And prevent:

negative marks \> question marks

unless your policy explicitly permits it.

---

# **16\. Maximum Attempts**

Current:

Maximum Attempts: 1

Keep it.

But Faculty should see:

Maximum Attempts  
\[ 1 \]

Students can attempt this exam up to 1 time.

If greater than 1:

2 attempts allowed

Then your Student portal's history needs to support multiple attempts.

---

# **17\. Step 3 — Schedule & Entry**

This screen has one obvious UI problem.

You currently show:

dd-mm-yyyy \--:-- \--

while the browser's native datetime input is displaying a different format/interaction.

That needs to be standardized.

Use a proper:

datetime-local

input or a consistent date-time picker.

The user should never have to figure out what:

dd-mm-yyyy \--:-- \--

means.

---

# **18\. Add timezone**

For an examination system, show:

Timezone  
Asia/Kolkata (IST)

Preferably derived from institution configuration.

This prevents ambiguity.

---

# **19\. Scheduling validation**

The system must enforce:

registration\_start \< registration\_end  
registration\_end \<= exam\_start  
exam\_start \< exam\_end

And:

exam duration ≈ end\_time \- start\_time

You need to decide whether duration is:

### **Option A**

Automatically calculated:

Exam Start: 10:00  
Exam End: 11:00

Duration: 60 minutes

I prefer this.

Or:

### **Option B**

Duration remains the master and end time is calculated.

Either can work.

But allowing all three to be independently editable creates inconsistency.

---

# **20\. Late entry allowance**

Current:

10 minutes

Good feature.

But explain it:

Late Entry Allowance  
\[ 10 \] minutes

Students may enter the examination up to  
10 minutes after the scheduled start time.

Then backend must enforce it.

---

# **21\. Auto-submit**

Current:

Auto-Submit Answers Upon Timer Expiry

Keep it.

But the description should make it clear:

At timer expiry, the attempt will automatically  
be submitted and no further answers can be modified.  
---

# **22\. Add "Exam Availability"**

You need to distinguish:

Registration window

from:

Examination window

These are not the same thing.

Faculty needs to see:

Registration:  
01 Sept 10:00 → 08 Sept 23:59

Exam:  
10 Sept 10:00 → 11:00  
---

# **23\. Step 4 — Question Selection**

This is the **largest missing Faculty feature** in your current create-exam flow.

After scheduling:

Next: Select Questions

Faculty should see:

Question Bank

Search questions...  
Filter:  
\[Subject\]  
\[Category\]  
\[Difficulty\]  
\[Type\]  
\[Marks\]

☐ Q1 Which SQL clause...  
☐ Q2 Which are ACID properties...  
☐ Q3 ...

Then:

Selected Questions: 10  
Total Marks: 50  
---

# **24\. Question selection must show question preview**

Faculty should be able to click:

Preview

and see:

Question  
Options  
Correct answer  
Explanation  
Difficulty  
Marks  
Question type

This is faculty-only information.

---

# **25\. Add question distribution**

This would significantly improve your project.

For example:

Difficulty Distribution

Easy      4  
Medium    4  
Hard      2

And:

Question Type

MCQ       8  
MSQ       2

This helps Faculty build balanced examinations.

---

# **26\. Question selection should prevent duplicates**

The same question should not accidentally be selected twice.

Backend must enforce this through the exam-question relationship.

---

# **27\. Add "Remove Question"**

Selected list:

Q1  
Q2  
Q3  
Q4

\[Remove\]

And optionally:

↑ ↓

for manual ordering when shuffle is disabled.

---

# **28\. Step 5 — Review & Publish**

This is missing completely.

Before final creation:

Review Examination

show:

Basic Details  
────────────────  
DBMS Mid-Term  
CS101  
60 minutes

Scoring  
────────────────  
Total: 100  
Passing: 40  
Negative marking: 0.25  
Attempts: 1

Schedule  
────────────────  
Registration: 01 Sept → 08 Sept  
Exam: 10 Sept, 10:00 → 11:00

Questions  
────────────────  
20 Questions  
10 Easy  
8 Medium  
2 Hard

Then:

\[ Save Draft \]  
\[ Publish / Schedule Exam \]  
---

# **29\. Don't directly publish without review**

Your current:

Finalize & Schedule Exam

is too aggressive.

A Faculty member should get one final confirmation:

Are you sure?

Once published:  
• Students may see the exam.  
• Question selection may become locked.  
• Schedule changes may notify students.  
---

# **30\. Exam Management list page**

This is another major missing page.

Click:

Exam Management

and you should **not immediately go to Create Exam**.

You need:

Exam Management

\[ \+ Create Exam \]

Search exams...

Filters:  
Subject | Status | Date

Table:

Exam Code  
Exam Title  
Subject  
Schedule  
Candidates  
Questions  
Status  
Actions

Example:

EXAM-DBMS-MID  
DBMS Mid-Term  
CS101  
10 Sept, 10 AM  
42 candidates  
20 questions  
SCHEDULED

\[ View \] \[ Manage \] \[ Monitor \]  
---

# **31\. Exam actions should depend on status**

For Draft:

Edit  
Delete  
Continue Setup

For Scheduled:

View  
Edit  
View Candidates  
Cancel

For Live:

Monitor  
View Candidates

For Completed:

Results  
Evaluate  
Analytics

For Published:

View  
Analytics

This prevents inappropriate actions.

---

# **32\. Add candidate management**

Your dashboard says:

> Enrolled Candidates

But where does Faculty actually see them?

You need:

Exam → Candidates

Page:

Registered Candidates

Student ID  
Name  
Email  
Registration Status  
Attempt Status  
Score  
Integrity Flags

Example:

STU001  
Rutuja Ghodekar  
Registered  
Submitted  
90/100  
2 Flags

\[View Attempt\]  
---

# **33\. Registration management**

Faculty should be able to see:

Registered  
Not Registered  
Attempted  
Submitted  
Absent

But don't necessarily give Faculty arbitrary ability to register students unless that is an explicit institutional requirement.

The system should primarily derive registration from the student process.

---

# **34\. Question Bank — current screen**

Your current Question Bank is:

Question Text  
Type  
Category  
Difficulty  
Default Marks  
Actions

Good foundation.

But it is missing important management functionality.

---

# **35\. Add filters**

At the top:

Search questions...

Add:

Subject  
Category  
Question Type  
Difficulty  
Status  
Created By

And:

\[ Apply Filters \] \[ Clear \]  
---

# **36\. Add question status**

Questions need something like:

ACTIVE  
ARCHIVED

Don't permanently delete questions that have already been used in examinations.

Why?

Because an old exam depends on its historical question.

So:

Question used in exam  
       ↓  
Archive

is safer than:

DELETE  
---

# **37\. Fix the disabled edit icons**

Your screenshot shows pale/disabled-looking edit buttons.

That is a usability problem.

If editing is unavailable, don't show an apparently clickable pencil.

If editing is allowed:

✏ Edit

If it isn't:

🔒 Locked

with a tooltip:

Question is locked because it is used in a published examination.

That's much clearer.

---

# **38\. Question creation screen**

Current screen is pretty good structurally:

Category  
Difficulty  
Question Type  
Marks  
Estimated Time  
Question  
Options  
Explanation  
Save

But I'd change several things.

---

# **39\. Don't expose database table names to Faculty**

You currently have labels such as:

> Question Category (QuestionCategory Table)

> QuestionOption Junction Table

This is useful for developers but **not for the Faculty user**.

Remove all:

(Table)  
Junction Table  
Schema names

from the actual UI.

Use:

Question Category  
Question Type  
Options  
Explanation

Your project documentation can mention the database mapping.

The production UI should not.

---

# **40\. Default marks should not be 50**

Your screenshot shows:

Default Marks: 50.00

for a simple MCQ.

That is almost certainly inappropriate.

For example:

MCQ \= 1 or 2 marks  
MSQ \= 2–5 marks

depending on your exam design.

More importantly, the value should be intentionally configured rather than accidentally defaulting to `50`.

---

# **41\. Estimated time**

Keep:

Estimated Time

but use:

seconds/minutes

and explain:

Estimated time: 2 minutes

Faculty can later use this for analytics.

---

# **42\. Add question preview**

Before saving:

Preview Question

should show exactly what the Student will see.

This is extremely useful for preventing malformed questions.

---

# **43\. Question validation**

For MCQ:

Exactly one correct option

For MSQ:

At least two?

Whether MSQ requires at least two correct options depends on your rules, but you must define it.

Also:

At least 2 options  
No empty options  
Question text required  
Marks \> 0  
Difficulty required  
Type required  
---

# **44\. Question categories should come from backend**

Don't hardcode:

SQL Queries  
Database Concepts

in JavaScript.

They should come from the relevant database configuration/reference data.

Same with:

Easy  
Medium  
Hard

and question types.

---

# **45\. Evaluations — current screen**

Your current Evaluation page is:

Attempt ID  
Student  
Exam  
Submitted Time  
Auto Score  
Evaluation Status  
Action

That's a good queue, but it's not enough.

The faculty needs a **real evaluation workspace**.

---

# **46\. Evaluation details page**

Click:

Review & Finalize

and show:

┌──────────────────────────────────────────────────────────┐  
│ Rutuja Ghodekar                                          │  
│ DBMS Mid-Term Assessment                                 │  
│ Attempt \#1                                               │  
│                                                          │  
│ Auto Score: 90/100                                       │  
│ Integrity Events: 2                                     │  
├──────────────────────────────────────────────────────────┤  
│ Question Review                                          │  
│                                                          │  
│ Q1                                                       │  
│ Which SQL clause...?                                     │  
│ Student Answer: WHERE                                    │  
│ Correct: WHERE                                           │  
│ Score: 5/5                                              │  
│                                                          │  
│ Q2                                                       │  
│ ...                                                      │  
├──────────────────────────────────────────────────────────┤  
│                                                          │  
│ Final Score: \[ 90 \]                                     │  
│ Faculty Remarks:                                        │  
│ \[.................................................\]      │  
│                                                          │  
│ \[ Save Draft \] \[ Finalize Evaluation \]                   │  
└──────────────────────────────────────────────────────────┘  
---

# **47\. Faculty must see the student's answers**

The Evaluation screen should allow:

Question  
Student answer  
Correct answer  
Marks

for objective questions.

For descriptive/coding questions later:

Student submission  
Faculty score  
Faculty comments  
---

# **48\. Auto evaluation vs faculty evaluation**

Your current dashboard shows:

Auto Score

This is good.

But distinguish:

Auto Score  
Final Score

because they are not necessarily identical.

Example:

Auto Score: 85  
Faculty Adjustment: \+5  
Final Score: 90

The final result should be based on the final evaluation.

---

# **49\. Evaluation status needs more states**

Instead of only:

AUTO\_EVALUATED  
PENDING

use:

PENDING  
AUTO\_EVALUATED  
UNDER\_REVIEW  
FINALIZED  
PUBLISHED

Potentially:

REOPENED

if your workflow permits it.

---

# **50\. Add integrity information to Evaluation**

This is currently missing.

For each attempt:

Integrity Summary

⚠ 2 events  
• Tab switch — 02:17 PM  
• Fullscreen exit — 02:24 PM

Then:

\[ Review Integrity Events \]

Faculty decides whether action is needed.

Again:

**do not automatically invalidate the attempt merely because an event occurred.**

---

# **51\. Add candidate attempt timeline**

This would be a very strong feature.

Example:

02:00 — Exam started  
02:12 — Answer saved  
02:17 — Tab switch detected  
02:24 — Fullscreen exited  
02:30 — Exam submitted

This is extremely useful during disputes.

---

# **52\. Faculty should be able to finalize results**

After reviewing:

\[ Finalize Evaluation \]

confirmation:

Finalize Evaluation?

Final Score: 90/100

Once finalized, the score will be locked unless  
the result is reopened by an authorized user.

\[ Cancel \] \[ Finalize \]  
---

# **53\. Result publication should be separate**

Don't automatically publish immediately after evaluation.

Workflow:

Evaluation  
   ↓  
Finalized  
   ↓  
Ready for Publication  
   ↓  
Publish Results  
   ↓  
Student can see result

This gives the institution control.

---

# **54\. Add result publication screen**

For example:

DBMS Mid-Term Assessment

Evaluation Summary  
42 Candidates  
40 Evaluated  
2 Pending

\[ Publish Results \]

If not all are evaluated:

⚠ 2 candidates are still pending evaluation.

Publish anyway?

Whether publishing is allowed should be a policy decision.

---

# **55\. Results should connect directly to Student**

Once Faculty clicks:

Publish Results

the Student gets:

🔔 Result Published

DBMS Mid-Term Assessment  
Score: 90/100

\[ View Result \]

And:

Student → Results

shows it.

---

# **56\. Faculty analytics — current page**

Your current Analytics screenshot is visually good but **far too limited**.

You currently have:

Total Candidates  
Pass Rate  
Average Percentage  
Avg Time Spent

and:

Grade Distribution  
Difficulty Accuracy

That's a good start.

But a real Faculty analytics module should answer:

> Was the exam well designed?

> Which questions were too easy/hard?

> Which topics are weak?

> Which students are struggling?

---

# **57\. Add exam selector**

At the top:

Analytics

Exam:  
\[ DBMS Mid-Term Assessment ▼ \]

Potentially:

Subject:  
\[ All ▼ \]

and:

Date range  
---

# **58\. Faculty analytics should include**

### **Performance**

Candidates  
Attempted  
Submitted  
Absent  
Average Score  
Median Score  
Highest Score  
Lowest Score  
Pass Rate  
---

# **59\. Score distribution**

Add a chart:

Score Distribution

0–20    ██  
21–40   ███  
41–60   █████  
61–80   ███████  
81–100  █████████

This tells faculty much more than:

A+ \= 2 students  
---

# **60\. Question analysis**

This is particularly valuable.

Table:

Question  
Correct %  
Incorrect %  
Skipped %  
Difficulty  
Average Time

Example:

Q1   100%   0%    0%    Easy     32 sec  
Q2    40%  50%   10%    Hard     95 sec

Then Faculty can identify problematic questions.

---

# **61\. Question discrimination**

If you want one genuinely impressive analytics feature:

Question Performance

show:

High-performing students correct: 95%  
Low-performing students correct: 30%

This can indicate whether a question effectively differentiates performance.

You don't need an advanced statistical implementation initially, but the architecture can leave room for it.

---

# **62\. Difficulty analysis**

Your existing:

Difficulty Level Accuracy Analysis

should be expanded.

Show:

Easy  
Average accuracy: 91%

Medium  
Average accuracy: 74%

Hard  
Average accuracy: 48%

This lets Faculty evaluate whether the exam is balanced.

---

# **63\. Topic/category performance**

Because your Question Bank has categories:

SQL Queries  
Database Concepts  
Normalization  
Transactions

analytics can show:

Category Performance

SQL Queries          88%  
Normalization        72%  
Transactions         61%  
ACID Properties      94%

This is very useful academically.

---

# **64\. Time analytics**

Since your ExamAttempt should record timing:

Average Time  
Median Time  
Fastest  
Slowest

Potentially:

Average time per question

This connects to the `estimatedTimeSeconds` you already have on questions.

---

# **65\. Export analytics**

Your screenshot already has:

Export Report PDF

Keep it.

But add:

Export PDF  
Export CSV

if feasible.

PDF:

Exam summary  
Grade distribution  
Question analysis  
Difficulty analysis

CSV:

Student  
Score  
Percentage  
Grade  
Attempt status  
---

# **66\. Subjects page — important correction**

Your Faculty portal currently has:

Academic Subject Directory  
\[+ Add New Subject\]

I would **remove or restrict "Add New Subject" from Faculty** unless your requirements explicitly say faculty can create institution-wide subjects.

This is an architectural issue.

Your Admin portal already has:

Subjects

Therefore subject master data should generally be controlled by Admin.

Faculty should see:

My Assigned Subjects

rather than:

Academic Subject Directory  
---

# **67\. Faculty Subjects should look like**

My Subjects

CS101  
Database Management Systems  
4 Credits

2 Active Exams  
24 Questions

\[ View Subject \]

and:

CS102  
Full Stack Web Development  
4 Credits

1 Active Exam  
18 Questions  
---

# **68\. Subject details page**

Faculty can see:

Subject  
Code  
Credits  
Description

Assigned Exams  
Question Bank  
Candidate statistics

But not:

Create Subject  
Delete Subject  
Change Credits  
Change Department

unless Admin permissions explicitly grant that.

---

# **69\. Why this matters**

The stakeholder boundary should be:

ADMIN  
  ↓  
Creates/maintains Subject  
  ↓  
Assigns Faculty  
  ↓  
FACULTY  
  ↓  
Uses assigned Subject  
  ↓  
Creates Questions  
  ↓  
Creates Exams  
  ↓  
STUDENT

Don't make both Admin and Faculty independently own the same master data.

That creates conflicts.

---

# **70\. Faculty ↔ Admin connection**

The Admin should control:

User accounts  
Roles  
Faculty assignment  
Subject master data  
System configuration  
Security/audit  
Feature flags

Faculty controls:

Questions  
Exams  
Schedules  
Evaluations  
Academic results

So:

Admin  
  │  
  ├── creates faculty  
  ├── assigns subjects  
  └── activates account  
          │  
          ↓  
       Faculty  
          │  
          ├── creates questions  
          ├── creates exam  
          ├── schedules exam  
          └── evaluates  
---

# **71\. Faculty ↔ Student connection**

This is the most important relationship.

FACULTY  
   │  
   │ creates  
   ↓  
EXAM  
   │  
   ├── Schedule  
   ├── Questions  
   ├── Rules  
   └── Registration  
          │  
          ↓  
       STUDENT  
          │  
          │ attempts  
          ↓  
     EXAM ATTEMPT  
          │  
          ├── Answers  
          ├── Timing  
          └── Integrity Events  
                  │  
                  ↓  
               FACULTY  
                  │  
                  ↓  
              Evaluation  
                  │  
                  ↓  
                Result  
                  │  
                  ↓  
               STUDENT

This should drive your backend APIs.

---

# **72\. Faculty ↔ Admin security connection**

During an exam:

Student  
  ↓  
Tab switch  
  ↓  
IntegrityEvent  
  ↓  
Faculty reviews  
  ↓  
Admin can audit

Admin should have broader visibility.

For example:

Admin  
System Health & Flags  
       ↓  
Integrity events  
       ↓  
ExamAttempt  
       ↓  
Student

But Admin shouldn't need to manually evaluate every student's academic answers.

---

# **73\. Notifications**

Faculty also needs notifications.

Examples:

🔔 Student submitted an exam  
🔔 2 evaluations are pending  
🔔 Exam starts in 30 minutes  
🔔 Result publication pending  
🔔 Integrity event detected

These should be generated from actual backend events.

Not hardcoded activity messages.

---

# **74\. Faculty activity feed**

Your current dashboard has:

Question Bank  
Added MCQ question...  
Exam Management  
Scheduled DBMS Mid-Term...

Keep it, but make it real.

Events could be:

Question created  
Exam created  
Exam scheduled  
Exam published  
Student submitted  
Evaluation completed  
Result published  
Exam schedule changed  
---

# **75\. Search should actually work**

You currently have search bars on almost every page:

Search questions...  
Search exams...  
Search evaluations...  
Search subjects...  
Search analytics...

If these are just visual elements, remove them until functional.

A fake search bar is worse than no search bar.

When implemented:

### **Question Bank**

Search:

question text  
category  
type  
difficulty

### **Exam Management**

Search:

exam title  
exam code  
subject

### **Evaluation**

Search:

student name  
attempt ID  
exam  
---

# **76\. Add loading states**

Every Faculty data page needs:

Loading...

or skeleton rows.

For example:

Fetching evaluations...

Don't render empty tables while the API is loading.

Otherwise Faculty may think:

> There are no submissions.

when the API simply hasn't returned yet.

---

# **77\. Add proper empty states**

### **Question Bank**

No questions found.

Create your first question.

\[ Create Question \]

### **Exams**

No examinations created yet.

\[ Create Exam \]

### **Evaluations**

No pending evaluations.  
You're all caught up.

### **Analytics**

No completed examinations available for analysis.  
---

# **78\. Add proper error states**

Example:

Unable to load evaluations.

\[ Retry \]

or:

Exam could not be scheduled.

Please correct the highlighted fields.

Never expose:

500  
SQLAlchemy error  
ForeignKeyViolation

to Faculty.

---

# **79\. Audit important Faculty actions**

Faculty actions that should generate audit records:

Question created  
Question edited  
Question archived  
Exam created  
Exam updated  
Exam scheduled  
Exam cancelled  
Question added to exam  
Question removed from exam  
Evaluation finalized  
Result published

This connects directly to your Admin:

System Health & Flags / Audit  
---

# **80\. Lock questions after publication**

This is very important.

Suppose:

Question \#1

is used in:

DBMS Mid-Term

and the exam has already been completed.

Faculty shouldn't edit the question and accidentally change historical meaning.

Instead:

Question used by published exam  
       ↓  
Edit restricted  
       ↓  
Archive / create new version

This protects historical exam integrity.

---

# **81\. Same principle for exams**

After:

Exam starts

don't allow Faculty to casually change:

Questions  
Marks  
Negative marking  
Duration

unless your policy specifically supports emergency changes.

If changes are allowed:

Change detected  
↓  
Audit event  
↓  
Affected students notified  
---

# **82\. Exam monitoring page — missing**

I would add:

Exam Management  
   ↓  
Monitor Exam

During an active exam:

DBMS Mid-Term

Status: LIVE  
Started: 02:00 PM  
Ends: 03:00 PM

42 Registered  
38 Started  
35 In Progress  
3 Submitted  
4 Not Started

Then:

Student  
Status  
Last Activity  
Integrity Events

Example:

Rutuja Ghodekar  
In Progress  
02:27 PM  
1 Warning

Shlok Powar  
Submitted  
02:25 PM  
0

This would be a very strong Faculty feature.

---

# **83\. But don't allow Faculty to see answers live**

During an active examination, Faculty should generally see:

attempt status  
connection/activity status  
integrity events

but not necessarily:

student's current answers

unless there is a legitimate administrative requirement.

This reduces unnecessary privacy/security exposure.

---

# **84\. Add exam cancellation**

Exam Management should support:

Cancel Exam

with confirmation:

Cancel DBMS Mid-Term?

42 students are registered.

Students will be notified.

Reason:  
\[...................................\]

\[ Cancel \] \[ Confirm Cancellation \]

Then Student sees:

Exam Cancelled

and Admin sees an audit event.

---

# **85\. Add schedule modification**

If an exam hasn't started:

Edit Schedule

If students are already registered:

⚠ Changing this schedule will notify 42 students.

That is important.

---

# **86\. Faculty dashboard should surface schedule conflicts**

Potentially:

⚠ Schedule Conflict

DBMS Mid-Term  
10:00–11:00

Another examination for the same student group:  
10:30–11:30

This may be more advanced, but it is valuable if your database contains enough enrollment information.

If not, don't implement this now.

---

# **87\. Role boundaries — final recommendation**

This is where I'd be strict.

| Feature | Student | Faculty | Admin |
| ----- | ----- | ----- | ----- |
| View own profile | ✅ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| Manage subjects | ❌ | ❌/limited | ✅ |
| View assigned subjects | ❌ | ✅ | ✅ |
| Create question | ❌ | ✅ | maybe |
| Edit question | ❌ | ✅ | maybe |
| Create exam | ❌ | ✅ | maybe |
| Schedule exam | ❌ | ✅ | oversight |
| Register for exam | ✅ | ❌ | ❌ |
| Attempt exam | ✅ | ❌ | ❌ |
| Submit exam | ✅ | ❌ | ❌ |
| Monitor exam | ❌ | ✅ | oversight |
| Evaluate | ❌ | ✅ | maybe oversight |
| Publish result | ❌ | ✅ | oversight |
| View own result | ✅ | ❌ | ❌ |
| View exam analytics | ❌ | ✅ | aggregated |
| View system analytics | ❌ | ❌ | ✅ |
| View integrity events | own | assigned exams | all/oversight |
| RBAC management | ❌ | ❌ | ✅ |
| Feature flags | ❌ | ❌ | ✅ |
| System configuration | ❌ | ❌ | ✅ |

This keeps the architecture clean.

---

# **88\. Final Faculty navigation**

So my final recommendation is:

FACULTY PORTAL

Dashboard

Question Bank  
 ├── All Questions  
 ├── Create Question  
 └── Categories/Filters

Exam Management  
 ├── All Exams  
 ├── Create Exam  
 ├── Upcoming  
 ├── Active / Monitor  
 └── Completed

Evaluations  
 ├── Pending  
 ├── In Review  
 ├── Finalized  
 └── Results / Publication

Subjects  
 └── My Assigned Subjects

Analytics  
 ├── Exam Performance  
 ├── Question Analysis  
 ├── Difficulty Analysis  
 └── Student Performance

Profile  
Help / Rules  
Logout  
---

# **89\. Final exam creation architecture**

I would change your current 3-step process to:

                   CREATE EXAM

                         ↓

              ┌─────────────────────┐  
              │ 1\. Basic Details     │  
              │ Subject              │  
              │ Title                │  
              │ Code                 │  
              │ Type                 │  
              │ Instructions         │  
              └──────────┬──────────┘  
                         ↓  
              ┌─────────────────────┐  
              │ 2\. Scoring & Rules  │  
              │ Marks               │  
              │ Passing Marks       │  
              │ Attempts            │  
              │ Negative Marking    │  
              │ Shuffle             │  
              └──────────┬──────────┘  
                         ↓  
              ┌─────────────────────┐  
              │ 3\. Schedule         │  
              │ Registration        │  
              │ Exam Start/End      │  
              │ Late Entry          │  
              │ Auto Submit         │  
              └──────────┬──────────┘  
                         ↓  
              ┌─────────────────────┐  
              │ 4\. Questions        │  
              │ Search              │  
              │ Filter              │  
              │ Select              │  
              │ Reorder             │  
              └──────────┬──────────┘  
                         ↓  
              ┌─────────────────────┐  
              │ 5\. Review & Publish │  
              │ Summary             │  
              │ Validation          │  
              │ Preview             │  
              │ Save Draft          │  
              │ Publish             │  
              └─────────────────────┘

This is much more complete than the current flow.

---

# **90\. Final Faculty → Student lifecycle**

The finished system should behave like this:

                ADMIN  
                   │  
             assigns Subject  
                   │  
                   ↓  
                FACULTY  
                   │  
          ┌────────┴─────────┐  
          ↓                  ↓  
   Question Bank         Create Exam  
          │                  │  
          └────────┬─────────┘  
                   ↓  
             Select Questions  
                   ↓  
                Schedule  
                   ↓  
              Publish/Open  
                   │  
                   ↓  
                STUDENT  
                   │  
              sees exam  
                   ↓  
              registers  
                   ↓  
             starts exam  
                   ↓  
             ExamAttempt  
              /    |    \\  
             /     |     \\  
        Answers  Timer  Integrity  
             \\     |     /  
              \\    |    /  
                   ↓  
                Submit  
                   ↓  
              FACULTY QUEUE  
                   ↓  
            Auto Evaluation  
                   ↓  
            Faculty Review  
                   ↓  
           Finalize Evaluation  
                   ↓  
            Publish Result  
                   ↓  
                STUDENT  
                   ↓  
                Result  
                   ↓  
             Personal History

And alongside this:

                  ALL IMPORTANT ACTIONS  
                           │  
                           ↓  
                      AUDIT LOG  
                           │  
                           ↓  
                         ADMIN  
---

# **91\. What I would actually change in your current Faculty frontend**

If we're working directly from the screenshots you gave me, here's the **concrete change list**.

### **Dashboard**

**Keep:**

* Welcome section  
* Summary cards  
* Pending evaluation table  
* Assigned subjects  
* Activity feed

**Change:**

* Replace weak metrics with actionable metrics  
* Add Upcoming/Active Exams  
* Add Attention Required  
* Add integrity alerts  
* Make cards clickable  
* Make activity feed dynamic  
* Add exam status  
* Add quick actions  
* Add candidate/submission counts  
* Add loading/empty/error states

---

### **Question Bank**

**Keep:**

* Table  
* Create Question  
* Filters/search concept

**Add:**

* Search functionality  
* Subject filter  
* Category filter  
* Difficulty filter  
* Type filter  
* Status filter  
* Pagination  
* Preview  
* Edit  
* Archive  
* Usage count  
* "Used in published exam" lock indicator

**Remove:**

* Database table names from UI

**Fix:**

* Disabled-looking action buttons

---

### **Create Question**

**Keep:**

* Category  
* Difficulty  
* Type  
* Marks  
* Estimated time  
* Question  
* Options  
* Explanation

**Add:**

* Validation  
* Preview  
* Save draft  
* MCQ/MSQ-specific validation  
* Question status

**Change:**

* Remove schema/table terminology  
* Fix default marks  
* Better option management  
* Clear required fields

---

### **Exam Management**

**Add completely:**

* Exam list  
* Search  
* Filters  
* Status  
* Candidate count  
* Question count  
* View  
* Edit  
* Monitor  
* Cancel  
* Duplicate exam if desired

---

### **Create Exam**

**Current:**

3 steps

**Change to:**

5 steps  
1\. Basic Details  
2\. Scoring & Rules  
3\. Schedule & Entry  
4\. Question Selection  
5\. Review & Publish  
---

### **Evaluations**

**Keep:**

* Queue table

**Add:**

* Filters  
* Search  
* Evaluation details  
* Student answers  
* Correct answers  
* Marks  
* Faculty comments  
* Auto score  
* Final score  
* Integrity events  
* Attempt timeline  
* Finalize  
* Reopen if authorized  
* Result publication

---

### **Subjects**

**Change:**

Academic Subject Directory

to:

My Assigned Subjects

**Remove/restrict:**

Add New Subject

because Admin should own subject master data.

---

### **Analytics**

**Keep:**

* Pass rate  
* Average  
* Grade distribution  
* Difficulty accuracy  
* PDF export

**Add:**

* Exam selector  
* Score distribution  
* Median  
* Highest/lowest  
* Attempted/absent  
* Question-level analysis  
* Category/topic analysis  
* Time analysis  
* Difficulty distribution  
* Student performance  
* CSV export

---

# **92\. One thing I would NOT add**

Don't turn the Faculty dashboard into another Admin dashboard.

For example, Faculty does **not** need:

System CPU  
Database latency  
Thread pool utilization  
Feature flags  
RBAC matrix  
Global user management

Those belong to Admin.

Similarly, don't make Faculty manage every student account.

The Faculty portal should stay focused on:

> **Teaching \+ examination administration \+ evaluation.**

---

# **93\. The three stakeholder dashboards should therefore fit together like this**

This is the architecture I'd use for the whole project:

                   ┌─────────────┐  
                    │    ADMIN    │  
                    │             │  
                    │ Users       │  
                    │ Subjects    │  
                    │ RBAC        │  
                    │ Audit       │  
                    │ System      │  
                    └──────┬──────┘  
                           │  
             assigns/controls/oversees  
                           │  
                           ↓  
                    ┌─────────────┐  
                    │   FACULTY   │  
                    │             │  
                    │ Questions   │  
                    │ Exams       │  
                    │ Schedule    │  
                    │ Evaluation  │  
                    │ Analytics   │  
                    └──────┬──────┘  
                           │  
                    creates/publishes  
                           │  
                           ↓  
                    ┌─────────────┐  
                    │   STUDENT   │  
                    │             │  
                    │ Exams       │  
                    │ Registration│  
                    │ Attempt     │  
                    │ Answers     │  
                    │ Submit      │  
                    │ Results     │  
                    └──────┬──────┘  
                           │  
                     attempt data  
                           │  
                           ↓  
                    ┌─────────────┐  
                    │   FACULTY   │  
                    │ Evaluation  │  
                    │ Results     │  
                    └──────┬──────┘  
                           │  
                        publish  
                           │  
                           ↓  
                    ┌─────────────┐  
                    │   STUDENT   │  
                    │   Result    │  
                    └─────────────┘

       All important actions ───────→ ADMIN AUDIT

### **The most important missing Faculty features, in priority order**

If you have limited development time, **do these first**:

1. **Exam Management list**  
2. **Question selection as part of exam creation**  
3. **Review & Publish step**  
4. **Real evaluation detail page**  
5. **Candidate/registration management**  
6. **Active exam monitoring**  
7. **Result finalization/publication**  
8. **Integrity-event visibility**  
9. **Better analytics**  
10. **Convert Subjects to "My Assigned Subjects"**  
11. **Real search/filtering**  
12. **Proper validation/error/loading/empty states**  
13. **Lock published exam/question data**  
14. **Notifications**  
15. **Audit integration with Admin**

The biggest conceptual change I would make is this: **don't think of the Faculty dashboard as six disconnected CRUD pages.** It should be a single academic workflow whose data moves from **Subject → Question → Exam → Schedule → Student Attempt → Evaluation → Result → Analytics**, while Admin provides the governance and audit layer around that workflow.

