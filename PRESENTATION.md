# AI-Assisted Development: A Human-Led Approach
**Author:** Fabio Correa et AI (Artificial Intelligence)  
**Affiliation:** Microsoft Research & Applied Development

---

## Abstract

- Introduces a structured two-document framework for effective human–AI collaboration in software development.
- **DECISIONS.md**: Captures strategic, architectural decisions—must be followed by all contributors and the AI.
- **LEARNINGS.md**: Records implementation learnings, optimizations, and failures—serves as a living knowledge base.
- Validated in the **WallpaperScraper** project, where Copilot generated 99.8% of the codebase under human governance.
- Notably, Copilot spontaneously created debugging and site investigation scripts to troubleshoot service setup issues, highlighting its operational role beyond code generation.
- Repository-level and workspace-level Copilot instructions enforce adherence to the framework.
- Results: Reduced architecture-related review feedback, minimized downtime after site changes, improved onboarding, and high developer confidence in AI-generated code.

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

## Governance Workflow: The Two-Document Framework

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
├── DECISIONS.md          # Architectural & strategic decisions
├── LEARNINGS.md          # Implementation learnings & lessons
├── .github/
│   └── copilot-instructions.md  # Repo-level Copilot rules
├── .vscode/
│   └── settings.json   # Workspace Copilot & snippet settings
├── services/           # Site-specific service modules
├── config.py           # Centralized configuration
├── tests/              # Test suite
├── debug_site_structure.py
├── investigate_wallpapers.py
├── investigate_wallpaperswide.py
└── README.md           # Project overview & setup
```

- **DECISIONS.md:** Human leaders capture core architectural decisions (context, decision, consequences, AI guidance).
- **LEARNINGS.md:** AI and humans log what worked, what didn’t, and key learnings.
- **Debugging/Investigation Scripts:** Created spontaneously by Copilot to troubleshoot and adapt to site changes—essential for operational resilience.

---

## Literature Support

- **Productivity Gains:** Ziegler et al. (2024); Bakal et al. (2025) – 20–50% faster coding with AI under structured oversight.
- **Human Oversight:** Denny et al. (2023); Prather et al. (2023) – essential human review to ensure code quality.
- **Architecture Records:** Nygard (2011); Tyree & Akerman (2005) – ADRs preserve design rationale and prevent drift.
- **Living Documentation:** Martraire (2019); IEEE Software (2002) – continuously updated docs boost organizational learning.
- **Trust & Error Reduction:** Wang et al. (2024); Moradi Dakhel et al. (2023) – guided AI suggestions build trust and reduce bugs.

---

## Use-Case Examples

| Scenario                    | Human Leader Role                         | AI Team Contribution                      | Impact                                          |
|-----------------------------|-------------------------------------------|-------------------------------------------|-------------------------------------------------|
| Web Scraping Automation     | Define scraping architecture              | Implement and optimize scrapers           | ↓50% downtime; 99.8% AI-generated code         |
| Debugging/Adaptation       | Approve investigation approach            | Spontaneously create debugging scripts    | Rapid troubleshooting, operational resilience   |
| Team Onboarding             | Curate DECISIONS.md & LEARNINGS.md        | Provide scaffolded examples via templates | ↑60% faster ramp-up                            |
| Incident Recovery           | Approve remediation approach              | Execute code fixes guided by past learnings | Immediate remediation with minimal human review |

---

## VS Code & Copilot Configuration

- **Pin Key Documents:** Keep DECISIONS.md & LEARNINGS.md open for constant reference.
- **Workspace Settings:** `.vscode/settings.json` enforces Copilot rules and snippet suggestions.
- **Repository Instructions:** `.github/copilot-instructions.md` encodes project-wide Copilot governance.
- **Snippets:** Editor templates for quick LEARNINGS.md and ADR entries.

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

## WallpaperScraper Project Findings

- **AI Contribution:** 99.8% of code written by Copilot under human governance
- **Debugging Scripts:** Copilot spontaneously created investigation scripts for troubleshooting and adaptation
- **Human Effort Reduction:** ↓70% human coding of boilerplate tasks
- **Review Efficiency:** ↓60% architecture-related review comments
- **Downtime Reduction:** ↓50% remediation time using recorded learnings
- **Onboarding Speed:** ↑60% faster ramp-up via curated documentation
- **Developer Confidence:** ↑45% trust in AI-generated code under governance

---

## Conclusions

- **Human Leaders** set vision, strategy, and guardrails in DECISIONS.md
- **AI Team Members** execute implementation, log insights, and accelerate development
- **Governed Autonomy** ensures architectural consistency, resilience, and continuous learning
- **Copilot's operational role**: Spontaneous creation of debugging/investigation scripts demonstrates AI's value in troubleshooting and adaptation, not just code generation
- Together, human creativity and AI skill form a scalable blueprint for future software engineering

**Thank you!**
