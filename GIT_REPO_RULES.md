# GIT REPO RULES — DO NOT DELETE

## ⚠️ CRITICAL WARNING

**This repo (`build-coding-agent`) is ONLY for course materials.**

### What Gets Pushed Here:
- ✅ Course curriculum (CURRICULUM.md)
- ✅ Tutorial files (tutorials/)
- ✅ Code examples (src/, solutions/)
- ✅ Documentation (README.md, etc.)
- ✅ Course-specific scripts

### What NEVER Gets Pushed Here:
- ❌ MEMORY.md
- ❌ SOUL.md
- ❌ AGENTS.md
- ❌ USER.md
- ❌ TOOLS.md
- ❌ HEARTBEAT.md
- ❌ Any files from ~/.openclaw/workspace/
- ❌ Personal learning notes
- ❌ Automation scripts

### How to Prevent Accidental Pollution:

1. **Always work from THIS directory:**
   ```bash
   cd ~/workspace/jarvis-learning/courses/build-coding-agent
   ```

2. **Check git remote BEFORE pushing:**
   ```bash
   git remote -v
   # Should show: build-coding-agent.git, NOT jarvis-learning.git
   ```

3. **Verify only course files are staged:**
   ```bash
   git status
   # Should only show course-related files
   ```

4. **Never push from parent workspace directory:**
   ```bash
   # WRONG:
   cd ~/workspace/jarvis-learning
   git push
   
   # CORRECT:
   cd ~/workspace/jarvis-learning/courses/build-coding-agent
   git push
   ```

### If You Accidentally Polluted the Repo:

1. STOP — don't push anything else
2. Clone the repo fresh to /tmp
3. Identify what shouldn't be there
4. Delete polluted files from the repo
5. Push clean state
6. Document what happened

### History:
- 2026-03-28: Accidentally pushed entire workspace (~50 personal files). Fixed by rebuilding repo with only course content.

---
**Remember:** This repo is PUBLIC. Only course content goes here.
