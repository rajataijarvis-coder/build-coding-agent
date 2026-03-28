# 🎓 Build Your Own Coding Agent - Course Tracker

**Status:** Day 3 In Progress (T25-T36) - Tool Use Loop  
**Mode:** Hybrid + GitHub Workflow
- I publish tutorials to GitHub (canonical source)
- You follow along, run code, ask questions
- Day 3 (Tool Use Loop) is now live!  
**Last Updated:** 2026-03-28  
**Next:** T26 - JSON Schema for Tool Definitions

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
| Phase 1: Foundations | ✅ Complete | 13 (Days 1) | 13/13 |
| Phase 2: File Operations | ✅ Complete | 11 (Days 2) | 11/11 |
| Phase 3: Tool Use Loop | 🟡 In Progress | 12 (Day 3) | 1/12 |
| Phase 4: Shell & Context | ⚪ Not Started | 12 (Day 4) | 0/12 |
| Phase 5: Polish & Testing | ⚪ Not Started | 12 (Day 5) | 0/12 |
| **TOTAL** | 🟡 In Progress | **Streamlined** | **25/60** |

**Note:** Course streamlined from 324 to 60 tutorials (5 days). Focus on working agent by end.

### Daily Tutorial Tracker

#### Day 1: Architecture & Design Principles
| # | Tutorial | Status | Blog URL | Notes |
|---|----------|--------|----------|-------|
| 1 | What is a Coding Agent? | ✅ Published | jarvis-blog-murex.vercel.app | Intro complete |
| 2 | System Architecture Deep Dive | ✅ Published | jarvis-blog-murex.vercel.app | Architecture diagram |
| 3 | Component Communication | ✅ Published | jarvis-blog-murex.vercel.app | Detailed breakdown |
| 4 | Data Flow Patterns | ✅ Published | jarvis-blog-murex.vercel.app | agent_v0.py created |
| 5 | OOP Refresher | ✅ Published | jarvis-blog-murex.vercel.app | agent_v1.py created |
| 6 | SOLID Principles | ✅ Published | jarvis-blog-murex.vercel.app | agent_v2.py created |
| 7 | Design Patterns | ✅ Published | jarvis-blog-murex.vercel.app | agent_v3.py created |
| 8 | Project Structure | ✅ Published | jarvis-blog-murex.vercel.app | Package structure |
| 9 | Setup Environment | ✅ Published | jarvis-blog-murex.vercel.app | Poetry, Git, API keys |
| 10 | Agent Class Skeleton | ✅ Published | jarvis-blog-murex.vercel.app | Agent class created |
| 11 | Interface Design | ✅ Published | jarvis-blog-murex.vercel.app | Contracts defined |
| 12 | Dependency Injection | ✅ Published | jarvis-blog-murex.vercel.app | DI container wired |
| 13 | Day 1 Capstone: Summary & Complete Code | ✅ Published | GitHub | Working code consolidating T1-T12 |

#### Day 2: File Operations
| # | Tutorial | Status | Blog URL | Notes |
|---|----------|--------|----------|-------|
| 14 | File Operations: Read and Write | ✅ Published | jarvis-blog-murex.vercel.app | read_file, write_file |
| 15 | Path Validation and Safety | ✅ Published | jarvis-blog-murex.vercel.app | No ../ escapes |
| 16 | Directory Listing: list_dir | ✅ Published | jarvis-blog-murex.vercel.app | List directory contents |
| 17 | Multi-File Operations | ✅ Published | jarvis-blog-murex.vercel.app | Batch operations |
| 18 | Search: grep, find | ✅ Published | jarvis-blog-murex.vercel.app | Pattern matching |
| 19 | File Watching: change detection | ✅ Published | jarvis-blog-murex.vercel.app | Monitor file changes |
| 20 | File Editing: patching | ✅ Published | jarvis-blog-murex.vercel.app | Edit files safely |
| 21 | Binary File Detection | ✅ Published | jarvis-blog-murex.vercel.app | Skip binary files |
| 22 | File Diff Preview | ✅ Published | jarvis-blog-murex.vercel.app | Show differences |

#### Day 3: Tool Use Loop
| # | Tutorial | Status | Blog URL | Notes |
|---|----------|--------|----------|-------|
| 25 | Tool Use Concept: LLM Function Calling | ✅ Published | GitHub | JSON tool calls intro |
| 26 | JSON Schema for Tool Definitions | 🔄 In Progress | - | Tool schema format |
| 27 | Anthropic Tool Use Format | ⚪ Not Started | - | Claude-specific |
| 28 | Parsing Tool Calls | ⚪ Not Started | - | Extract structured calls |
| 29 | Tool Execution Loop | ⚪ Not Started | - | Call → Execute → Return |
| 30 | Error Handling in Tool Loop | ⚪ Not Started | - | Graceful failures |
| 31 | ReAct Pattern | ⚪ Not Started | - | Thought → Action → Observation |
| 32 | Multi-Step Tasks | ⚪ Not Started | - | Planning before execution |
| 33 | Self-Correction | ⚪ Not Started | - | When tools fail |
| 34 | Token Tracking | ⚪ Not Started | - | Monitor costs |
| 35 | Conversation Persistence | ⚪ Not Started | - | Save/load sessions |
| 36 | Hands-on: Complete Tool Use System | ⚪ Not Started | - | End-to-end |

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
