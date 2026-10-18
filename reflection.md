# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Core user actions**

Based on the PawPal+ scenario, the three core actions a user should be able to perform are:

1. **Enter owner and pet information** – The user sets up a profile with basic owner details (name, how much time they have available each day, preferences) and their pet's info (name, species/breed). This gives the scheduler the context it needs.
2. **Add and edit care tasks** – The user creates pet care tasks such as walks, feeding, medication, enrichment, or grooming. Each task needs at least a duration and a priority, and the user can update them later as needs change.
3. **Generate and view today's plan** – The user asks the app to build a daily schedule that fits their available time and puts higher-priority tasks first. The plan is displayed clearly, along with an explanation of why tasks were chosen, ordered, or skipped.

**Initial UML design**

My design is pretty simple. An owner has pets, each pet has tasks, and a scheduler looks at the tasks and the owner's free time to make a daily plan. I kept all the scheduling logic in one class so it's easier to test.

**Classes and responsibilities**

- **Owner** – keeps the owner's name, how much time they have today, and their pets.
- **Pet** – keeps the pet's name and species, and its list of tasks.
- **Task** – one care activity (walk, feeding, meds, etc.) with a duration and priority.
- **Scheduler** – sorts tasks by priority and fits them into the available time.
- **DailyPlan** – the final schedule, plus which tasks got skipped and why.

**b. Design changes**

Yes. AI generated the class skeleton from my UML, and then I asked it to review its own skeleton for missing pieces. Based on that feedback I changed a few things:

- `DailyPlan` now saves the reason a task was skipped, because before it accepted a reason but had nowhere to store it.
- `DailyPlan` now saves a start time for each scheduled task, so the plan can say when things happen.
- A task's priority can only be low, medium, or high, so a typo doesn't break the sorting.

I made these changes so the plan can explain itself, and I updated `uml.mmd` to match.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
