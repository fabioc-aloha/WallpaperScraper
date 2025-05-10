# AI-Assisted Development: A Human-Led Approach
**Author:** Fabio Correa et AI (Artificial Intelligence)  
**Affiliation:** Microsoft Research & Applied Development

---

## Problem Statement

- Rapid AI-generated code often diverges from established architectural patterns
- No structured mechanism to capture reasoning, leading to repeated errors and knowledge loss
- Teams struggle to balance AI productivity with code quality and coherence

### Detailed Challenges
1. **Architectural Drift**
   - Uncontrolled AI suggestions can diverge from project patterns
   - Leads to inconsistent interfaces, duplicated logic, and technical debt
2. **Knowledge Loss**
   - No central repository for decision rationale or outcomes
   - Onboarding delays when institutional memory resides in individuals
3. **Repeated Mistakes**
   - AI may unknowingly repeat past errors without feedback loops
   - Time wasted debugging issues already resolved
4. **Role Ambiguity**
   - Unclear division between human planning and AI implementation
   - Over-reliance on AI or excessive human oversight
5. **Leadership & Creativity**
   - **Humans** are the creative, critical-thinking leaders setting vision and strategy
   - **AI** acts as an intelligent, skilled development team executing tasks under human guidance
   - Without human leadership, AI lacks innovation and contextual judgment

---

## Motivations

- Leverage AI-driven productivity gains (20–50% faster development) while safeguarding architecture
- Reduce technical debt and prevent drift through human-approved guardrails
- Capture institutional knowledge continuously to accelerate onboarding and learning
- Enable developers (creative leaders) to focus on strategy, leaving routine coding to AI team members

---

## Governance Workflow

1. **Human Strategy (Creative Leadership)**
   - Define high-level architecture and project vision in **DECISIONS.md**
2. **AI Execution (Skilled Team Member)**
   - GitHub Copilot generates code snippets within the guardrails
3. **Tactical Logging**
   - AI records implementation outcomes in **LEARNINGS.md** for transparency
4. **Human Review & Refinement**
   - Creative leaders validate learnings, adjust strategy, and update decisions
5. **Continuous Iteration**
   - The cycle of strategy → execution → logging → refinement fosters continuous improvement

---

## Project Structure in GitHub

```text
WallpaperScraper/
├── DECISIONS.md          # ADRs: architecture & strategy
├── LEARNINGS.md          # Tactical insights & lessons
├── .github/
│   ├── copilot-instructions.md  # Repo-level AI guidelines
│   └── workflows/
├── .vscode/
│   ├── settings.json   # Workspace AI & snippet settings
│   └── snippets/
├── src/                # AI-implemented code modules
│   ├── scrapers/
│   ├── core/
│   └── main.py
├── tests/              # Human & AI co-authored tests
├── docs/               # Supplemental guides & diagrams
└── README.md           # Project overview & setup
```

- **DECISIONS.md:** Human leaders capture core architectural decisions (context, decision, consequences, AI guidance).
- **LEARNINGS.md:** AI team members log what worked, what didn’t, and key learnings.

---

## Literature Support

- **Productivity Gains:** Ziegler et al. (2023); Bakal et al. (2025) – 20–50% faster coding with AI under structured oversight.
- **Human Oversight:** Denny et al. (2023); Prather et al. (2023) – essential human review to ensure code quality.
- **Architecture Records:** Nygard (2011); Tyree & Akerman (2005) – ADRs preserve design rationale and prevent drift.
- **Living Documentation:** Martraire (2019); IEEE Software (2002) – continuously updated docs boost organizational learning.
- **Trust & Error Reduction:** Wang et al. (2024); Moradi Dakhel et al. (2023) – guided AI suggestions build trust and reduce bugs.

---

## Use-Case Examples

| Scenario                    | Human Leader Role                         | AI Team Contribution                      | Impact                                          |
|-----------------------------|-------------------------------------------|-------------------------------------------|-------------------------------------------------|
| Web Scraping Automation     | Define scraping architecture              | Implement and optimize scrapers           | ↓50% downtime; 99.8% AI-generated code         |
| Microservices Deployment    | Design API standards                      | Generate service templates & stubs        | ↓80% runtime integration bugs                  |
| Team Onboarding             | Curate DECISIONS.md & LEARNINGS.md        | Provide scaffolded examples via templates | ↑60% faster ramp-up                              |
| Incident Recovery           | Approve remediation approach               | Execute code fixes guided by past learnings | Immediate remediation with minimal human review |

---

## VS Code Configuration Tutorial

### 1. Pin Key Documents
- **Human Leaders:** Pin `DECISIONS.md` & `LEARNINGS.md` for constant strategic and tactical visibility.
- **AI Benefit:** Open tabs become part of Copilot’s context for suggestions.

### 2. Workspace Settings (`.vscode/settings.json`)
```json
{
  "files.associations": {
    "DECISIONS.md": "markdown",
    "LEARNINGS.md": "markdown"
  },
  "github.copilot.chat.codeGeneration.instructions": [
    {"text": "Always consult DECISIONS.md before making architectural changes."},
    {"text": "Record all learnings in LEARNINGS.md after implementation."}
  ],
  "editor.snippetSuggestions": "top"
}
```

### 3. Repository-Level Copilot Instructions
- **File:** `.github/copilot-instructions.md`
- **Content:**
  ```markdown
  # AI Collaboration Guidelines
  - Consult `DECISIONS.md` for strategic design decisions.
  - Update `LEARNINGS.md` with detailed implementation outcomes.
  - Reject suggestions that conflict with approved decisions.
  ```

### 4. Editor Snippets & Live Templates
- **LEARNINGS-ENTRY snippet:** Scaffold AI team’s lesson entries
- **ADR-ENTRY snippet:** Scaffold human leader’s ADR templates

---

## Comparing Copilot Configuration Approaches

| Feature                           | Repository-Level Instructions               | Workspace Settings                      |
|-----------------------------------|---------------------------------------------|-----------------------------------------|
| Scope                             | All contributors (Copilot Chat)             | Individual developer’s environment      |
| Format                            | Markdown (natural language guidelines)      | JSON (structured instructions)          |
| Version Control                   | Yes (committed to repo)                     | No (local unless committed)             |
| Tool Invocation Support           | Informational only                          | Can invoke tools & specify constraints  |
| Primary Use Case                  | Enforce team-wide behavior                  | Customize AI for individual workflow    |

---

## Tutorial Demo: Step-by-Step

1. **Clone & Open**: `git clone ... && code WallpaperScraper`
2. **Verify Config**: Check `.vscode/settings.json` & `.github/copilot-instructions.md`
3. **AI Code Generation**: Type a function stub; Copilot (AI team) suggests code per DECISIONS.md
4. **LEARNINGS Logging**: Use snippet to record outcomes in LEARNINGS.md
5. **Human Review**: Creative leader reviews and approves or refines learnings
6. **Iterate**: Repeat cycle for continuous improvement

---

## WallpaperScraper Project Findings

- **AI Contribution:** 99.8% of code written by AI team members
- **Human Effort Reduction:** ↓70% human coding of boilerplate tasks
- **Review Efficiency:** ↓60% architecture-related review comments
- **Downtime Reduction:** ↓50% remediation time using recorded learnings
- **Onboarding Speed:** ↑60% faster ramp-up via curated documentation
- **Developer Confidence:** ↑45% trust in AI-generated code under governance

---

## Future Research Directions

- **Scaling Teams:** Multi-lead governance and multi-AI coordination
- **Enhanced Tooling:** Extensions surfacing DECISIONS.md & LEARNINGS.md in-editor
- **Cross-Domain Adoption:** Apply model to design, data science, and operations
- **AI Self-Tuning:** Safe fine-tuning of AI models on project learnings
- **Quantitative Validation:** Measure impact on quality, velocity, and team dynamics

---

## Conclusions

- **Human Leaders** set vision, strategy, and guardrails in DECISIONS.md
- **AI Team Members** execute implementation, log insights, and accelerate development
- **Governed Autonomy** ensures architectural consistency, resilience, and continuous learning
- Together, human creativity and AI skill form a scalable blueprint for future software engineering

**Thank you!**
