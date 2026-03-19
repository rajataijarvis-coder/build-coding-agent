# 🎓 Build Your Own Coding Agent - Course Tracker

**Status:** Active (Day 1, Tutorial 1/288 complete)  
**Mode:** Hybrid + GitHub Workflow
- I publish tutorials to blog (self-paced)
- GitHub PRs for code review (collaborative)
- You track progress (Option B)  
**Last Updated:** 2026-03-18  
**Next Tutorial:** Day 1, Tutorial 2 (System Architecture Deep Dive)

---

## 🔄 GITHUB WORKFLOW (New!)

**Format:** Async collaboration via GitHub PRs
**Response Time:** Within same day (usually)
**Mode:** You code → Push → I review → Comment fixes

### How It Works

**Your Flow:**
```bash
# 1. Clone repo
git clone https://github.com/rajataijarvis-coder/build-coding-agent.git

# 2. Create your branch
git checkout -b ratewar-session-1

# 3. Work on tutorials
# Edit files in your-work/

# 4. Push your progress
git add .
git commit -m "Completed tutorials 1-3, stuck on exercise 2"
git push origin ratewar-session-1

# 5. Create PR for review
gh pr create --title "Session 1: Tutorials 1-3" --body "Ready for review"
```

**My Flow:**
```bash
# 1. See your PR
gh pr list

# 2. Review your code
gh pr view 1

# 3. Comment with feedback
gh pr comment 1 --body "Line 42: Try using composition instead of inheritance"

# 4. Or checkout and fix
gh pr checkout 1
# Edit files...
git commit -am "Fix: handle edge case in error handling"
git push
```

### PR Review Process

**When you push code:**
1. I get notification
2. Review within hours (same day)
3. Comment with:
   - ✅ What looks good
   - ❌ What needs fixing
   - 💡 Suggestions for improvement
   - 📚 Links to relevant docs

**When you have questions:**
- Comment on PR: "Stuck on X, getting Y error"
- Or WhatsApp me: "Check PR #3, need help with Z"
- I respond with fix or explanation

### Communication

**GitHub (Primary):**
- PR comments for code-specific feedback
- Issues for general questions
- Commit messages show progress

**WhatsApp (Secondary):**
- "Pushed PR #5, stuck on exercise 3"
- "Ready for next batch of tutorials"
- Quick questions that don't need code context

---

## 📊 Progress Dashboard

### Overall Progress
| Phase | Status | Tutorials | Completed |
|-------|--------|-----------|-----------|
| Phase 1: Foundations | 🟡 In Progress | 72 (Days 1-3) | 6/72 |
| Phase 2: Core Agent | ⚪ Not Started | 72 (Days 4-6) | 0/72 |
| Phase 3: Intelligence | ⚪ Not Started | 72 (Days 7-9) | 0/72 |
| Phase 4: Production | ⚪ Not Started | 72 (Days 10-12) | 0/72 |
| Phase 5: Agent-Native Web | ⚪ Not Started | 36 (Days 13-14) | 0/36 |
| **TOTAL** | | **324** | **6/324** |

### Daily Tutorial Tracker

#### Day 1: Architecture & Design Principles
| # | Tutorial | Status | Blog URL | Notes |
|---|----------|--------|----------|-------|
| 1 | What is a Coding Agent? | ✅ Published | jarvis-blog-murex.vercel.app | Intro complete |
| 2 | System Architecture Deep Dive | 🟡 Next Up | - | - |
| 3 | Component Communication | ⚪ Not Started | - | - |
| 4 | Data Flow Patterns | ⚪ Not Started | - | - |
| 5 | OOP Refresher | ⚪ Not Started | - | - |
| 6 | SOLID Principles | ⚪ Not Started | - | - |
| 7 | Design Patterns | ⚪ Not Started | - | - |
| 8 | Project Structure | ⚪ Not Started | - | - |
| 9 | Setup Environment | ⚪ Not Started | - | - |
| 10 | Agent Class Skeleton | ⚪ Not Started | - | - |
| 11 | Interface Design | ⚪ Not Started | - | - |
| 12 | Dependency Injection | ⚪ Not Started | - | - |
| 13-24 | Hands-on: Skeleton | ⚪ Not Started | - | - |

[Days 2-12 to be added as we progress]

---

## 🎯 Rajat's Progress Tracker

**Your Status:**
- [ ] Read Tutorial 1
- [ ] Set up environment (Python 3.10+, Git)
- [ ] Write down 3 agent tasks (exercise)
- [ ] Read Tutorial 2
- [ ] [To be filled as you progress]

**Your Questions/Blockers:**
- [None yet - add here]

**Your Wins:**
- [To be filled as you complete tutorials]

---

## 🔄 Delivery Cadence

### My Responsibilities (Hourly Learning Cycles)
**During each learning cycle, I will:**
1. Check this tracker
2. Write next tutorial (if not done)
3. Update tracker status
4. Deploy to blog
5. Send you a brief update

**Daily Target:** 1-3 tutorials per day (realistic pace)
**Weekly Target:** ~20-30 tutorials
**Full Course:** ~10-12 weeks at this pace

### Your Responsibilities
**When convenient for you:**
1. Read published tutorials
2. Complete exercises
3. Ask questions via WhatsApp
4. Mark your progress in this tracker

**Suggested:** 1 tutorial per day, or batch on weekends

---

## 💾 Memory & Persistence Strategy

### How I Remember (Multiple Layers)

**Layer 1: This Tracker File**
- Location: `jarvis-learning/courses/build-coding-agent/TRACKER.md`
- Updated: After every tutorial
- Purpose: Single source of truth

**Layer 2: MEMORY.md**
- Location: `~/.openclaw/workspace/MEMORY.md`
- Section: "Active Courses"
- Updated: Weekly or on major milestones

**Layer 3: Daily Memory Files**
- Location: `memory/YYYY-MM-DD.md`
- Content: What I worked on today
- Purpose: Session continuity

**Layer 4: Learning Board**
- Location: `jarvis-learning/LEARNING_BOARD.md`
- Section: "Build Your Own Coding Agent - COURSE"
- Updated: When course status changes

**Layer 5: QMD (Semantic Search)**
- All files auto-indexed every 5 minutes
- Can search: "coding agent tutorial 5" to find content

### How You Track (Options)

**Option A: Simple (Recommended)**
- I update this tracker file
- You read tutorials from blog
- You tell me via WhatsApp when you complete something
- I mark your progress here

**Option B: Self-Service**
- You clone the repo: `~/.openclaw/workspace/jarvis-learning/`
- You edit this tracker file directly
- Push your updates (I'll give you access)

**Option C: External Tool**
- Notion, Trello, GitHub Projects
- I can sync status there too

---

## 📢 Communication Protocol

### When I Reach Out
- **New tutorial published:** "Tutorial X is live: [URL]"
- **Phase complete:** "Phase 1 done! Ready for Phase 2?"
- **Question needed:** "Quick question: [specific]"

### When You Reach Out
- **Questions:** Any time, any topic
- **Progress updates:** "Finished tutorial 5, moving to 6"
- **Blockers:** "Stuck on [specific thing]"

### When We Sync Live
- **Weekly check-in:** Optional, your call
- **Milestone reviews:** End of each phase
- **Debug sessions:** When you're stuck

---

## 🛠️ Infrastructure Setup

### What I've Already Done
✅ Course curriculum designed (288 tutorials)  
✅ Tutorial 1 written and published  
✅ Blog integration working  
✅ This tracker file created  
✅ MEMORY.md updated with course info  

### What I'll Do Next
🔄 Tutorial 2 (System Architecture Deep Dive)  
🔄 Set up automated blog deployment  
🔄 Create exercise templates  

### What You Need to Do
⏳ Set up Python 3.10+ environment (Tutorial 1 exercise)  
⏳ Optional: Clone the course repo for direct access  

---

## 🎓 Course Artifacts Location

| Artifact | Location | Access |
|----------|----------|--------|
| Curriculum | `jarvis-learning/courses/build-coding-agent/CURRICULUM.md` | Local |
| Tracker (this file) | `jarvis-learning/courses/build-coding-agent/TRACKER.md` | Local |
| Tutorials | `jarvis-learning/courses/build-coding-agent/tutorials/` | Local |
| Blog Posts | `jarvis-blog/content/posts/` | Deployed |
| Live Blog | https://jarvis-blog-murex.vercel.app/ | Web |
| Your Notes | `[Suggest location]` | Your choice |

---

## 🔍 How to Find Things

**Me (searching my memory):**
```bash
qmd search "coding agent tutorial 3" -c jarvis-memory -n 5
```

**You (finding latest tutorial):**
1. Go to: https://jarvis-blog-murex.vercel.app/
2. Look for "Build Your Own Coding Agent" posts
3. Or ask me: "What's the latest tutorial?"

---

## ✅ Success Metrics

**For Me:**
- Consistent publishing (1+ tutorials per day)
- Tracker always up to date
- Your questions answered within reasonable time

**For You:**
- Understanding each concept before moving on
- Completing hands-on exercises
- Building working components
- Having a production-ready agent at the end

**For Both:**
- Open-source course that helps other junior devs
- Real working tool you can use
- Deep understanding of agent architecture

---

## 🚨 Contingency Plans

**If I forget where we are:**
- This tracker file exists
- MEMORY.md has course section
- You can ask: "What tutorial are we on?"

**If you fall behind:**
- No problem! Self-paced
- Tutorials stay published
- Pick up whenever ready

**If you get ahead:**
- Let me know!
- I'll accelerate writing
- Or you can read source code directly

**If we need to pause:**
- Tracker freezes at current state
- Resume anytime
- No pressure

---

## 📝 Next Actions

**Me (next learning cycle):**
- [ ] Write Tutorial 2: System Architecture Deep Dive
- [ ] Publish to blog
- [ ] Update this tracker

**You (when ready):**
- [ ] Set up Python environment
- [ ] Read Tutorial 1 fully
- [ ] Do the exercise (write 3 agent tasks)
- [ ] Tell me when ready for Tutorial 2

---

*This tracker is living document - updated after every interaction.*
