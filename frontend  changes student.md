Absolutely. Let's treat the **Student Dashboard as a complete product**, not just a page that displays a few cards.

The key is to design it around the actual student journey:

> **Login → see available exams → register/eligible → enter exam → attempt → autosave → integrity monitoring → submit → evaluation → result → analytics/history**

And every one of those stages needs to connect to the **Faculty** and **Admin** sides.

I would make the Student portal the most carefully designed part of Phase 4 because this is where the actual examination happens.

---

# **1\. First: What the Student Portal should contain**

I recommend this navigation:

STUDENT PORTAL

├── Dashboard  
├── My Exams  
├── Available Exams  
├── Exam History  
├── Results  
├── Profile  
└── Help / Exam Rules

During an active exam, the navigation should **disappear or become inaccessible**.

The student should enter a dedicated examination environment:

EXAM MODE

├── Exam Header  
├── Timer  
├── Question Area  
├── Question Navigator  
├── Answer Controls  
├── Save Status  
├── Integrity Status  
└── Submit Exam

Do **not** treat the exam page as another normal dashboard page.

It is a special runtime environment.

---

# **2\. Student Dashboard — redesign completely**

The current dashboard should answer six questions immediately:

1\. What exams do I have?  
2\. Which exam is next?  
3\. Can I take an exam right now?  
4\. What have I already completed?  
5\. What are my recent results?  
6\. Is there anything I need to do?

The dashboard should therefore look roughly like:

┌─────────────────────────────────────────────────────────────┐  
│ Welcome, Rutuja\!                                           │  
│ Computer Engineering                                       │  
│                                                             │  
│ \[ Available Exams \] \[ Upcoming \] \[ Completed \] \[ Results \] │  
├─────────────────────────────────────────────────────────────┤  
│                                                             │  
│ NEXT / ACTIVE EXAM                                         │  
│ ┌─────────────────────────────────────────────────────────┐ │  
│ │ DBMS Mid-Term Assessment                                │ │  
│ │ Database Management Systems                             │ │  
│ │ Today • 2:00 PM – 3:00 PM                              │ │  
│ │                                                         │ │  
│ │ Status: AVAILABLE / ACTIVE                             │ │  
│ │                                                         │ │  
│ │                 \[ Start Exam \]                          │ │  
│ └─────────────────────────────────────────────────────────┘ │  
│                                                             │  
├──────────────────────────────┬──────────────────────────────┤  
│ Upcoming Exams               │ Recent Results               │  
│                              │                              │  
│ DBMS Final                   │ DBMS Mid-Term                │  
│ Sept 10 • 10:00 AM           │ 90 / 100                     │  
│ \[View Details\]               │ Passed                       │  
│                              │ \[View Result\]                │  
├──────────────────────────────┴──────────────────────────────┤  
│                                                             │  
│ Recent Activity                                             │  
│ • Exam submitted                                            │  
│ • Result published                                          │  
│ • Registration opened                                       │  
│                                                             │  
└─────────────────────────────────────────────────────────────┘  
---

# **3\. Top navigation/header**

Keep the same visual language as Faculty/Admin.

At the top:

MMCOE Exam

Then:

Search...

Then:

🔔 Notifications  
👤 Rutuja Ghodekar  
   Student  
   ↓

Clicking the profile should provide:

Profile  
Account Settings  
Logout

### **Don't put too many things in the header.**

The student's core functions belong in the sidebar.

---

# **4\. Student sidebar**

Recommended:

STUDENT PORTAL

🏠 Dashboard

📝 Available Exams

📚 My Exams

📊 Results

🕘 Exam History

👤 Profile

❓ Help & Exam Rules

Potentially combine:

Available Exams  
My Exams

into one:

Exams

with tabs:

Available | Upcoming | Active | Completed

I actually prefer this because it reduces navigation.

So my final recommendation is:

Dashboard  
Exams  
Results  
Exam History  
Profile  
Help & Rules  
---

# **5\. Dashboard summary cards**

The four cards should be:

### **Card 1**

Available Exams  
2

Meaning exams the student is eligible to take/register for.

### **Card 2**

Upcoming Exams  
1

### **Card 3**

Completed Exams  
4

### **Card 4**

Pending Results  
1

Don't use meaningless metrics such as:

Total Questions  
Average Login Time  
System Status

The dashboard should represent the student's academic state.

---

# **6\. Very important — distinguish exam states**

This is one of the most important things to implement.

Every exam shown to a student should have a clear state.

Use:

UPCOMING  
REGISTRATION\_OPEN  
REGISTRATION\_CLOSED  
AVAILABLE  
IN\_PROGRESS  
COMPLETED  
SUBMITTED  
EVALUATION\_PENDING  
RESULT\_PUBLISHED  
MISSED

But don't expose all of those as technical database values.

The UI can translate them.

For example:

Registration Open

instead of:

REGISTRATION\_OPEN  
---

# **7\. Exam lifecycle**

The complete lifecycle should be:

Faculty creates exam  
        ↓  
Faculty adds questions  
        ↓  
Faculty schedules exam  
        ↓  
Registration opens  
        ↓  
Student sees exam  
        ↓  
Student becomes eligible / registers  
        ↓  
Registration closes  
        ↓  
Exam starts  
        ↓  
Student enters exam  
        ↓  
ExamAttempt created  
        ↓  
Questions loaded  
        ↓  
Answers saved  
        ↓  
Integrity events recorded  
        ↓  
Student submits  
        ↓  
ExamAttempt submitted  
        ↓  
Objective evaluation  
        ↓  
Faculty review if necessary  
        ↓  
Result finalized  
        ↓  
Faculty/Admin publishes result  
        ↓  
Student sees result

This is the backbone of the entire application.

---

# **8\. Available Exams page**

This is one of the most important missing student features.

Student should see something like:

Available Examinations

┌────────────────────────────────────────────┐  
│ Database Management Systems                │  
│ DBMS Mid-Term Assessment                   │  
│                                            │  
│ Exam Date: Sept 10, 2026                   │  
│ Time: 10:00 AM – 11:00 AM                 │  
│ Duration: 60 minutes                       │  
│ Total Marks: 100                           │  
│                                            │  
│ Registration: OPEN                         │  
│                                            │  
│ \[ View Details \] \[ Register \]              │  
└────────────────────────────────────────────┘  
---

# **9\. Exam Details page**

Before starting an exam, student should be able to see:

Exam Title  
Subject  
Faculty  
Exam Code  
Date  
Start Time  
End Time  
Duration  
Total Marks  
Passing Marks  
Maximum Attempts  
Question Count  
Question Types  
Negative Marking  
Shuffle Questions  
Shuffle Options  
Late Entry Allowance

But don't expose internal implementation names like:

examStatus  
negativeMarking  
QuestionOption Junction Table

The Faculty/Admin screens can be technical.

The Student screen should be understandable.

---

# **10\. Exam instructions**

This deserves a dedicated section.

Example:

Before You Begin

• Ensure a stable internet connection.  
• Do not refresh the page during the examination.  
• Do not close the examination window.  
• Your answers are automatically saved.  
• The examination will automatically submit when the timer expires.  
• Leaving the examination window may be recorded as an integrity event.  
• Once submitted, you cannot change your answers.

Then:

☐ I have read and understood the examination rules.

\[ Proceed to Exam \]

This checkbox should be mandatory.

---

# **11\. Registration**

If your requirements include exam registration, this needs to be properly connected.

Flow:

Available Exam  
      ↓  
View Details  
      ↓  
Register  
      ↓  
Registration record created  
      ↓  
Exam appears under My Exams

The student should then see:

Registered ✓

instead of:

Register  
---

# **12\. But don't add registration if your institution doesn't need it**

This is an important design decision.

Your Faculty screenshots already show:

> Open Registration

and:

> Enrolled Candidates

So your current system clearly assumes registration.

Therefore, yes — I would keep it.

---

# **13\. My Exams page**

This should be the student's central examination management page.

Tabs:

All  
Upcoming  
Available  
In Progress  
Completed

Each exam card:

DBMS Mid-Term Assessment

Subject: Database Management Systems  
Date: 02 Sept 2026  
Time: 02:00 PM – 03:00 PM

Status: Registered

\[ View Details \]

For an active exam:

Status: LIVE

\[ ENTER EXAM \]

For completed:

Status: SUBMITTED

Score: 90/100

\[ View Result \]  
---

# **14\. Prevent invalid exam entry**

The frontend should **never decide eligibility by itself**.

For example, don't simply do:

if currentTime \>= startTime:  
    show Start Exam

The backend should verify:

Student authenticated  
        ↓  
Student eligible  
        ↓  
Exam exists  
        ↓  
Registration valid  
        ↓  
Exam currently active  
        ↓  
Attempts remaining  
        ↓  
Student hasn't already submitted  
        ↓  
Allow entry

The frontend merely displays the backend's decision.

This is critical.

---

# **15\. The actual Exam Page**

This is the most important Phase 4 feature.

I would structure it like this:

┌─────────────────────────────────────────────────────────────┐  
│ DBMS Mid-Term Assessment                   ⏱ 48:32 remaining │  
│ Question 3 of 20                          ● Saved            │  
├─────────────────────────────────────────────────────────────┤  
│                                                             │  
│ Question 3                                                 │  
│                                                             │  
│ Which SQL clause is used to filter records...?             │  
│                                                             │  
│ ○ GROUP BY                                                 │  
│ ● WHERE                                                    │  
│ ○ ORDER BY                                                 │  
│ ○ HAVING                                                   │  
│                                                             │  
│                                                             │  
│ \[ ← Previous \]                         \[ Next → \]           │  
│                                                             │  
├─────────────────────────────────────────────────────────────┤  
│ Question Navigator                                          │  
│                                                             │  
│ \[1\] \[2\] \[3\] \[4\] \[5\] \[6\] \[7\] \[8\] \[9\] \[10\]                 │  
│ \[11\]\[12\]\[13\]\[14\]\[15\]\[16\]\[17\]\[18\]\[19\]\[20\]                  │  
│                                                             │  
│ Legend:                                                     │  
│ ● Answered  ○ Unanswered  ⚑ Marked for Review              │  
│                                                             │  
│                              \[ Submit Exam \]                │  
└─────────────────────────────────────────────────────────────┘  
---

# **16\. Timer**

Timer is not optional.

It should be based on the **server-authoritative exam timing**, not merely:

60 \* 60

in JavaScript.

When the student enters:

serverStart  
serverEnd

should determine the remaining time.

Frontend:

remaining \= serverEnd \- serverCurrentTime

approximately.

This protects against:

refresh  
computer clock manipulation  
tab switching  
delayed page loading  
---

# **17\. Timer states**

Normal:

48:32

Warning:

05:00

Critical:

01:00

At:

00:00

the frontend should trigger submission, **but backend expiration must independently enforce it**.

Never trust only JavaScript.

---

# **18\. Question navigation**

Need:

Previous  
Next  
Question number navigation

And preferably:

Mark for Review

Student can mark:

Question 8 → Review later

This state belongs to the current attempt.

---

# **19\. Answer autosave**

This is one of your responsibilities and should be implemented carefully.

When student selects:

B

the frontend sends:

POST/PUT answer

to backend.

Conceptually:

Student  
   ↓  
ExamAttempt  
   ↓  
AttemptAnswer  
   ↓  
Question  
   ↓  
Selected Option

For MCQ:

selected\_option\_id

For MSQ:

selected\_option\_ids

depending on your actual schema.

---

# **20\. Don't save only when Next is clicked**

That is dangerous.

Suppose:

Student selects B  
↓  
Internet drops  
↓  
Student refreshes

They shouldn't lose their answer.

Autosave should happen immediately or through a very short debounce.

Example:

select answer  
      ↓  
local state updated immediately  
      ↓  
autosave request  
      ↓  
server confirms  
      ↓  
"Saved"  
---

# **21\. Show save status**

Near timer:

✓ Saved

or:

Saving...

or:

⚠ Not saved

This is extremely useful.

Don't make the student wonder whether their answer was recorded.

---

# **22\. Local backup**

You can additionally store the current answer state temporarily in:

sessionStorage

or another browser-local mechanism.

But this should only be a **recovery aid**.

The server remains authoritative.

Don't treat local storage as the actual answer database.

---

# **23\. Full-screen mode**

Because this is an examination platform, I recommend:

Enter Full Screen

before starting.

Then:

Exam begins only after full-screen is entered

if your requirements demand it.

But don't claim this makes cheating impossible.

Full-screen can be exited.

It is an integrity control, not a security boundary.

---

# **24\. Browser/tab switching monitoring**

This is another major Phase 4 requirement.

Detect:

visibilitychange  
blur  
fullscreenchange

Potentially:

tab switched  
window lost focus  
fullscreen exited

Then create an integrity event.

For example:

TAB\_SWITCH  
FULLSCREEN\_EXIT  
WINDOW\_BLUR  
---

# **25\. Integrity event architecture**

The connection should be:

Student Exam Page  
       │  
       ├── Timer  
       ├── Fullscreen monitor  
       ├── Visibility monitor  
       └── Focus monitor  
                │  
                ↓  
        Integrity Event API  
                │  
                ↓  
       IntegrityEvent table  
                │  
        ┌───────┴────────┐  
        ↓                ↓  
     Faculty            Admin  
     Review            Oversight

This is one of the most important cross-stakeholder connections in your system.

---

# **26\. Don't automatically punish the student for one tab switch**

This is important.

A browser event does not necessarily mean cheating.

For example:

student receives OS notification  
student accidentally clicks outside  
browser crashes

So:

1 TAB\_SWITCH

should not automatically mean:

EXAM\_INVALID

Instead record:

event\_type  
timestamp  
attempt\_id  
severity

Then faculty/admin can review according to policy.

---

# **27\. Integrity warning to student**

When something happens:

⚠ Warning

You have left the examination window.

This event has been recorded.  
Please return to the examination.

Don't immediately terminate the exam unless that is an explicit institutional rule.

---

# **28\. Submit Exam flow**

Never make the submit button instantly submit.

Click:

Submit Exam

Then modal:

Submit Examination?

You have answered 18 of 20 questions.

2 questions are unanswered.

Once submitted, you cannot modify your answers.

\[ Cancel \] \[ Submit Final Answer \]

This is essential.

---

# **29\. Submission states**

You need:

IN\_PROGRESS  
SUBMITTING  
SUBMITTED  
AUTO\_SUBMITTED

If network fails during submission:

Submission failed.

Your answers are still saved.  
Please retry.

But backend must ensure idempotency.

Repeated clicks should not create:

Attempt 1  
Attempt 2  
Attempt 3

for the same exam.

---

# **30\. Auto-submit**

When timer reaches zero:

Timer expired  
     ↓  
Frontend submits  
     ↓  
Backend validates expiry  
     ↓  
Attempt \= AUTO\_SUBMITTED

Even if the frontend fails, the backend should be capable of determining:

end\_time \<= current\_time

and prevent further answer modification.

---

# **31\. Exam completion page**

After submission:

✓ Examination Submitted

DBMS Mid-Term Assessment

Submitted at:  
02:58 PM

Submission:  
Successful

Your answers have been recorded.

Result:  
Pending Evaluation

\[ Return to Dashboard \]

Don't immediately show the score if evaluation isn't finalized.

---

# **32\. Results page**

This should be a separate student module.

Example:

My Results

┌──────────────────────────────────────────────┐  
│ DBMS Mid-Term Assessment                    │  
│ Database Management Systems                 │  
│                                             │  
│ Score: 90 / 100                            │  
│ Percentage: 90%                             │  
│ Grade: A+                                   │  
│ Status: Passed                              │  
│                                             │  
│ Published: 02 Sept 2026                     │  
│                                             │  
│ \[ View Detailed Result \]                    │  
└──────────────────────────────────────────────┘  
---

# **33\. Result must have a publication state**

The student shouldn't see a result merely because the faculty has evaluated it.

Use:

EVALUATION\_PENDING  
EVALUATED  
PUBLISHED

Student sees the result only when:

PUBLISHED

This connects directly to Faculty/Admin.

---

# **34\. Detailed result**

Student should be able to see:

Total Marks  
Obtained Marks  
Percentage  
Grade  
Pass/Fail  
Correct Answers  
Incorrect Answers  
Unanswered  
Negative Marks

If institutional rules allow it, also:

Question-wise breakdown

For example:

Q1   Correct      \+5  
Q2   Incorrect    \-1  
Q3   Correct      \+5  
Q4   Unanswered    0  
---

# **35\. Don't expose correct answers if policy doesn't allow it**

This is important.

There should be a configurable distinction between:

Score visible

and:

Correct answers/explanations visible

Faculty may want to publish:

90/100

without exposing:

correct option  
solution explanation

until later.

---

# **36\. Exam History**

This should show every exam attempt.

Example:

Exam History

DBMS Mid-Term  
Attempt \#1  
Submitted  
90/100

Full Stack Internal  
Attempt \#1  
Submitted  
85/100

DBMS Final  
Attempt \#1  
Missed  
—

This is important for academic history.

---

# **37\. Attempt history matters if maximum attempts \> 1**

Your Faculty exam screen already has:

> Maximum Attempts: 1

Therefore the architecture should support:

Exam  
  ↓  
Student  
  ↓  
Attempt 1  
Attempt 2  
Attempt 3

even if your current implementation allows only one.

That gives you future flexibility.

---

# **38\. Profile**

Student profile should contain:

Full Name  
Email  
Phone  
Student ID  
Department  
Enrollment information

Potentially:

Profile photo

but not necessary for your current project.

Student should **not** be able to modify authoritative academic information like:

Student ID  
Department  
Enrollment

unless your requirements explicitly allow it.

---

# **39\. Password management**

Profile should have:

Change Password

requiring:

Current Password  
New Password  
Confirm Password

This should call backend authentication logic.

---

# **40\. Help & Exam Rules**

This is a small page but worth having.

Include:

How to enter an exam  
How the timer works  
How autosave works  
What happens if internet disconnects  
What happens if I switch tabs  
How submission works  
When results are published

This will reduce confusion during the actual exam.

---

# **41\. Notifications**

You already have a bell in Faculty/Admin.

Student should have the same.

Notifications could include:

Exam registration opened  
Exam starts in 1 hour  
Exam starts in 15 minutes  
Result published  
Exam schedule changed  
Exam cancelled

The flow:

Faculty creates/schedules exam  
          ↓  
Notification generated  
          ↓  
Eligible students  
          ↓  
Student notification bell

This is another important stakeholder connection.

---

# **42\. Exam schedule changes**

Suppose Faculty changes:

Exam:  
10:00 AM

to:

11:00 AM

Student must not continue seeing the old value.

Backend:

ExamSchedule updated  
        ↓  
Student query  
        ↓  
Dashboard updates  
        ↓  
Notification generated

This is why you should never hardcode exam information in the frontend.

---

# **43\. Student dashboard ↔ Faculty dashboard**

This connection is extremely important.

### **Faculty creates exam**

Faculty  
   ↓  
Exam  
   ↓  
ExamSchedule  
   ↓  
Student Dashboard

Student sees:

Upcoming Exam  
---

### **Faculty adds questions**

Faculty  
   ↓  
Question  
   ↓  
ExamQuestion  
   ↓  
Student Exam Page

The student should never see questions until the exam runtime authorizes them.

---

### **Student submits**

Student  
   ↓  
ExamAttempt  
   ↓  
Faculty Evaluation Queue

Faculty then sees:

Rutuja Ghodekar  
DBMS Mid-Term  
90/100  
Pending/Auto Evaluated  
---

### **Faculty finalizes result**

Faculty  
   ↓  
Evaluation  
   ↓  
Result  
   ↓  
Publish  
   ↓  
Student Results

That's your complete result pipeline.

---

# **44\. Student dashboard ↔ Admin dashboard**

Admin shouldn't directly control the student's exam UI.

Instead:

Admin  
 ↓  
Users  
 ↓  
Student account  
 ↓  
Student can login

and:

Admin  
 ↓  
Subject  
 ↓  
Faculty assignment  
 ↓  
Faculty creates exam  
 ↓  
Student sees exam

And:

Student  
 ↓  
ExamAttempt  
 ↓  
AuditLog / IntegrityEvent  
 ↓  
Admin Security/Audit

So Admin is primarily **oversight**, not part of the student's actual examination flow.

---

# **45\. Complete cross-stakeholder architecture**

This is the structure I recommend:

                        ADMIN  
                           │  
            ┌──────────────┼───────────────┐  
            ↓              ↓               ↓  
          Users         Subjects        Audit/Security  
            │              │               ↑  
            ↓              ↓               │  
        Students        Faculty             │  
            │              │                │  
            │              ↓                │  
            │          Create Exam           │  
            │              │                │  
            │              ↓                │  
            │        Exam \+ Schedule         │  
            │              │                │  
            ↓              ↓                │  
       ┌─────────────────────────┐          │  
       │      STUDENT PORTAL     │          │  
       │                         │          │  
       │ Dashboard               │          │  
       │     ↓                   │          │  
       │ Available Exams         │          │  
       │     ↓                   │          │  
       │ Registration            │          │  
       │     ↓                   │          │  
       │ Exam Runtime            │──────────┤  
       │     ↓                   │          │  
       │ ExamAttempt             │          │  
       │     ↓                   │          │  
       │ Answers / Autosave      │          │  
       │     ↓                   │          │  
       │ Integrity Events        │──────────┤  
       │     ↓                   │          │  
       │ Submit                  │          │  
       └──────────┬──────────────┘          │  
                  ↓                         │  
             Evaluation                     │  
                  ↓                         │  
               FACULTY                      │  
                  ↓                         │  
            Finalized Result                │  
                  ↓                         │  
              Publish                       │  
                  ↓                         │  
             STUDENT RESULT ←───────────────┘  
---

# **46\. Backend entity relationships**

Based on the database architecture you've been working toward, the student side should conceptually work around:

User  
 │  
 └── Student  
       │  
       ├── Exam Registration  
       │       │  
       │       └── Exam  
       │             │  
       │             ├── Subject  
       │             ├── ExamSchedule  
       │             └── ExamQuestion  
       │                    │  
       │                    └── Question  
       │                           │  
       │                           └── QuestionOption  
       │  
       └── ExamAttempt  
               │  
               ├── AttemptAnswer  
               │      │  
               │      └── Question / Option  
               │  
               ├── IntegrityEvent  
               │  
               └── Result

This is the actual data flow your frontend should reflect.

---

# **47\. Don't create frontend-only relationships**

For example, don't do:

Student dashboard  
    ↓  
hardcoded exam card

Instead:

GET /exams/my

or whatever endpoint your backend design uses.

Then:

Exam  
 \+ Schedule  
 \+ Subject  
 \+ Registration status  
 \+ Attempt status

gets rendered.

---

# **48\. API flow you should implement**

Your exact endpoint names can follow your backend conventions, but conceptually you need:

### **Student**

GET    /student/dashboard  
GET    /student/exams  
GET    /student/exams/{id}  
POST   /student/exams/{id}/register  
GET    /student/exams/{id}/eligibility  
POST   /student/exams/{id}/attempt  
GET    /attempts/{id}  
GET    /attempts/{id}/questions  
PUT    /attempts/{id}/answers  
POST   /attempts/{id}/integrity-events  
POST   /attempts/{id}/submit  
GET    /student/results  
GET    /student/results/{id}  
GET    /student/history  
GET    /student/profile  
PUT    /student/profile

Don't blindly create every one of these if your backend already has equivalent endpoints; the point is the **capabilities**, not the literal URL names.

---

# **49\. One important security rule**

The frontend must never receive the correct answer before submission/evaluation.

Bad:

{  
  "question": "...",  
  "options": \[...\],  
  "correct\_option": 2  
}

during an exam.

It should receive only:

{  
  "question\_id": 1,  
  "question\_text": "...",  
  "options": \[...\]  
}

Correctness belongs on the backend.

---

# **50\. Student should never be able to request another student's attempt**

For example:

GET /attempts/25

must not simply return Attempt \#25 because the student knows the ID.

Backend should verify:

attempt.student\_id \== authenticated\_student.id

Likewise:

GET /results/25

must verify ownership.

This is especially important for an examination platform.

---

# **51\. Exam questions should be server-controlled**

The student should not be able to manipulate:

marks  
question IDs  
correct answers  
exam ID  
attempt ID  
submission status  
timer

through frontend JavaScript.

The frontend can send:

selected\_option\_id

but the backend determines:

question belongs to exam  
question belongs to attempt  
option belongs to question  
attempt belongs to student  
attempt is still active  
---

# **52\. Question shuffling**

Your Faculty page already has:

> Shuffle Question Order for Each Student

and:

> Shuffle Option Choice Order

Therefore Student runtime needs to support that.

Important:

Student A:  
Q1 Q5 Q3 Q2 Q4

Student B:  
Q3 Q1 Q4 Q2 Q5

But the student's ordering must remain stable during that attempt.

Don't reshuffle every time the student refreshes.

---

# **53\. Question numbering**

If shuffled:

Question 1  
Question 2  
Question 3

should refer to the student's generated order.

The underlying `question_id` remains stable.

This means you need an attempt-specific question order or deterministic shuffle strategy.

---

# **54\. Negative marking**

Faculty can configure:

Enable Negative Marking  
Negative Marks Per Wrong Question

Student should see this **before starting**:

Negative marking:  
0.25 marks deducted for each incorrect answer.

But don't expose it repeatedly during the exam unless useful.

---

# **55\. MSQ support**

Your Faculty Question Bank already contains:

MCQ  
MSQ

So the Student Exam UI must support both.

### **MCQ**

○ A  
○ B  
○ C  
○ D

Only one selection.

### **MSQ**

☐ A  
☐ B  
☐ C  
☐ D

Multiple selections.

Don't implement the frontend as MCQ-only and assume MSQ can be added later.

---

# **56\. Exam analytics for Student**

Student doesn't need the Faculty analytics dashboard.

But after results are published, you can give a lightweight:

My Performance

Average Score  
Highest Score  
Exams Passed  
Exams Attempted

Potentially:

Subject-wise performance

But don't overdo this.

Faculty/Admin need institutional analytics.

Student needs **personal analytics**.

---

# **57\. Student dashboard notifications**

I'd put a small section:

Upcoming

DBMS Mid-Term  
Starts tomorrow at 10:00 AM

\[View Exam\]

And:

Recent Results

DBMS Mid-Term  
90/100  
Published today

\[View Result\]

This is more valuable than a generic activity feed.

---

# **58\. Empty states**

This is something developers frequently forget.

You need screens for:

### **No exams**

No examinations available.

There are currently no examinations available for you.

### **No results**

No results published yet.

### **No history**

You haven't completed any examinations yet.

### **No notifications**

You're all caught up.

These are necessary for a real application.

---

# **59\. Error states**

Also design:

Unable to load exams.  
\[ Retry \]  
Unable to save answer.  
Retrying...  
Connection lost.  
Your answers will be synchronized when connection is restored.  
Exam unavailable.  
Please contact your faculty/institution.

Don't show raw backend errors.

Never:

500 Internal Server Error  
SQLAlchemy IntegrityError

to students.

---

# **60\. Network interruption during exam**

This is particularly important.

Scenario:

Student answers Q5  
↓  
internet disconnects  
↓  
frontend detects offline

Show:

⚠ Connection lost

Your local answers are being preserved.  
Reconnect to continue synchronization.

When connection returns:

Connection restored  
Synchronizing answers...  
✓ All answers saved

But again, local storage is recovery support—not the authoritative source.

---

# **61\. Browser refresh during exam**

You should decide your policy.

I recommend:

Refresh  
 ↓  
session/token still valid  
 ↓  
attempt exists  
 ↓  
attempt still active  
 ↓  
reload attempt  
 ↓  
restore question position  
 ↓  
restore answers from backend

Don't automatically destroy the attempt.

Otherwise a normal accidental refresh could ruin a student's exam.

---

# **62\. Back button**

During exam:

Browser Back

should ideally be handled carefully.

Don't rely entirely on preventing browser navigation—browsers don't guarantee that.

Instead:

If attempt active:  
    leaving page → warning

and when returning:

restore active attempt  
---

# **63\. Logout during exam**

Student should get:

You are currently taking an examination.

Logging out will leave the examination session.

Are you sure?

But don't destroy the attempt.

They should be able to resume if institutional policy allows.

---

# **64\. Session expiration**

This needs coordination with Admin's session configuration.

If session expires during exam, you don't want:

Student loses exam

without explanation.

Ideally:

Session expired  
↓  
re-authenticate  
↓  
resume existing attempt

subject to your security requirements.

---

# **65\. Mobile responsiveness**

For normal dashboard:

✅ Fully responsive.

For actual exam:

I'd support tablet/laptop, but **desktop/laptop should be the primary target**.

Exam UI on a 360px phone is a bad experience.

You could show:

This examination is optimized for desktop/tablet.  
Please use a larger screen.

if your institutional requirements allow you to restrict devices.

---

# **66\. Accessibility**

At minimum:

Keyboard navigation  
Visible focus  
Proper labels  
ARIA where needed  
Readable contrast  
No icon-only critical actions

For example, don't make Submit just:

\[ ✓ \]

Use:

\[ Submit Exam \]  
---

# **67\. Security: don't trust the student UI**

This deserves repeating because it is an online exam.

The frontend is **untrusted**.

A malicious student can modify JavaScript.

Therefore:

Frontend  
    ↓  
UX \+ convenience

Backend  
    ↓  
Security \+ authority

Backend must enforce:

student ownership  
exam availability  
attempt count  
exam timing  
question membership  
answer validity  
submission state  
result visibility  
---

# **68\. How Faculty sees the student's activity**

Faculty Dashboard should eventually show:

Pending Evaluations

Student  
Exam  
Submitted  
Score  
Integrity Flags  
Action

For example:

Rutuja Ghodekar  
DBMS Mid-Term  
02:30 PM  
90/100  
2 integrity events  
\[ Review \]

That connects the Student runtime directly to Faculty.

---

# **69\. How Admin sees it**

Admin should see aggregated oversight:

Audit Trail

Rutuja Ghodekar  
ExamAttempt  
CREATE  
SUCCESS

and:

Security / Integrity

Student: Rutuja Ghodekar  
Exam: DBMS Mid-Term  
Event: TAB\_SWITCH  
Time: 02:17 PM  
Severity: Warning

Admin does **not** need to see every answer.

That's Faculty/student exam data, not administrative data.

---

# **70\. What the Student should NOT have**

I'd deliberately remove/avoid:

❌ RBAC Matrix  
❌ System Metrics  
❌ Feature Flags  
❌ Faculty Question Bank  
❌ Subject creation  
❌ Exam creation  
❌ Global analytics  
❌ Other students' results  
❌ Other students' attempts  
❌ Admin audit controls

Student should see only information relevant to themselves.

---

# **71\. Final Student sidebar**

If I were implementing your frontend now, I'd settle on:

┌────────────────────────────┐  
│ 🎓 MMCOE Exam              │  
├────────────────────────────┤  
│ STUDENT PORTAL             │  
│                            │  
│ ▣ Dashboard                │  
│ 📝 Exams                   │  
│ 📊 Results                 │  
│ 🕘 Exam History            │  
│ 👤 Profile                 │  
│ ❓ Help & Rules             │  
│                            │  
│                            │  
│                            │  
│                            │  
│ Logout                     │  
└────────────────────────────┘

Then `Exams` has:

All  
Available  
Upcoming  
Active  
Completed

rather than creating five sidebar items.

---

# **72\. Final Student page structure**

You should ultimately have:

/student/  
│  
├── dashboard.html  
│  
├── exams/  
│   ├── exams.html  
│   ├── exam-details.html  
│   ├── instructions.html  
│   └── register.html  
│  
├── attempt/  
│   ├── exam.html  
│   └── submission.html  
│  
├── results/  
│   ├── results.html  
│   └── result-details.html  
│  
├── history/  
│   └── history.html  
│  
├── profile/  
│   └── profile.html  
│  
└── help/  
    └── rules.html

You don't necessarily need separate HTML files for every state if your existing architecture uses JS-driven views, but the **logical page separation** should exist.

---

# **73\. The most important data flow**

If you remember only one thing from this entire design, remember this:

                   FACULTY  
                       │  
                       │ creates  
                       ↓  
                     EXAM  
                       │  
                       │ schedules  
                       ↓  
                  EXAM SCHEDULE  
                       │  
                       ↓  
              ┌─────────────────┐  
              │     STUDENT     │  
              └────────┬────────┘  
                       │  
                  registers  
                       ↓  
                 REGISTRATION  
                       │  
                    starts  
                       ↓  
                 EXAM ATTEMPT  
                       │  
             ┌─────────┼─────────┐  
             ↓         ↓         ↓  
          Answers   Timer    Integrity  
             │         │         │  
             └─────────┼─────────┘  
                       ↓  
                    SUBMIT  
                       │  
                       ↓  
                  EVALUATION  
                       │  
                       ↓  
                    RESULT  
                       │  
                   publishes  
                       ↓  
                    STUDENT  
                       │  
                       ↓  
                  RESULT VIEW

And Admin sits **above the ecosystem for oversight**, rather than being inserted into every transaction.

---

# **74\. Priority order for implementation**

Don't build these randomly.

### **Phase A — Student shell**

1\. Student sidebar  
2\. Header  
3\. Dashboard  
4\. Profile  
5\. Logout

### **Phase B — Examination discovery**

6\. Exams page  
7\. Available exams  
8\. Upcoming exams  
9\. Exam details  
10\. Registration  
11\. Instructions

### **Phase C — Actual examination**

12\. Exam runtime  
13\. Timer  
14\. Question navigation  
15\. MCQ  
16\. MSQ  
17\. Autosave  
18\. Save status  
19\. Question review  
20\. Fullscreen

### **Phase D — Integrity**

21\. Tab switching  
22\. Window blur  
23\. Fullscreen exit  
24\. Integrity warning  
25\. Integrity API  
26\. Faculty/Admin visibility

### **Phase E — Submission**

27\. Submit confirmation  
28\. Manual submission  
29\. Auto submission  
30\. Submission result  
31\. Resume/reconnect handling

### **Phase F — Results**

32\. Results page  
33\. Result details  
34\. Grade  
35\. Score breakdown  
36\. Publication state  
37\. Exam history

### **Phase G — Polish**

38\. Notifications  
39\. Empty states  
40\. Error states  
41\. Responsive design  
42\. Accessibility  
43\. Loading states  
44\. Security hardening  
---

# **75\. And one architectural rule for the entire project**

I strongly recommend your team establish this now:

### **Faculty owns exam creation and academic evaluation**

Questions  
Exams  
Schedules  
Evaluation  
Results  
Academic analytics

### **Student owns exam participation**

Registration  
Attempt  
Answers  
Submission  
Personal results  
Personal history

### **Admin owns platform governance**

Users  
Subjects  
Faculty assignment  
Security  
Audit  
System-level oversight

That separation will prevent the exact problems we just found in the Admin/Faculty screenshots.

Most importantly, **Student → Faculty → Admin should be a data flow, not three independent dashboards**. The Student dashboard is the consumer of Faculty-created exams; the Student attempt generates the data Faculty evaluates; and those same actions generate the audit/security information Admin oversees.

That should be the foundation before you start changing individual Student HTML pages.

