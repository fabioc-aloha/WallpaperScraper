# AI-Assisted Development: The Two-Document Framework

---

## Problem Statement

- AI coding assistants (like GitHub Copilot) can generate code at unprecedented speed, but this can lead to:
  - Architectural drift: code diverges from intended design
  - Loss of institutional knowledge: lessons learned are not captured
  - Repeated mistakes: failed approaches are tried again
- Teams need a way to harness AI productivity while maintaining design coherence, code quality, and a culture of continuous learning.

<!-- Speaker Notes -->
*Speaker notes:*
AI tools are powerful, but without structure, they can introduce chaos into a codebase. This slide sets up the core challenge: how do we get the productivity benefits of AI without losing control over our architecture and knowledge? We'll see how the two-document framework addresses these risks and supports sustainable, high-quality development.

---

## Comparison Table: Two-Document Framework vs. Traditional AI Use

| Aspect                | Two-Document Framework                | Traditional AI Use         |
|-----------------------|---------------------------------------|----------------------------|
| Architectural Guardrails | Enforced via `DECISIONS.md`           | Often absent               |
| Knowledge Retention   | `LEARNINGS.md` as living knowledge    | Ad hoc, easily lost        |
| AI Suggestion Quality | Context-aware, project-aligned        | May repeat past mistakes   |
| Onboarding            | Accelerated via documented learnings  | Slower, tribal knowledge   |
| Change Approval       | Explicit for architecture             | Implicit or unclear        |
| Scalability           | High—works for any team size          | Risk of chaos as team grows|

<!-- Speaker Notes -->
*Speaker notes:*
This table highlights the practical differences between a structured, governed approach and a more ad hoc use of AI. Notice how the two-document framework provides clear boundaries, better onboarding, and higher suggestion quality. These benefits become more pronounced as teams and codebases grow.

---

## The Two-Document Framework

- **DECISIONS.md**
  - Records all architectural and strategic decisions
  - Serves as the project's "constitution"—AI and humans must not change these without explicit approval
  - Examples: choice of multi-service architecture, error handling strategy, configuration centralization
- **LEARNINGS.md**
  - Captures implementation learnings, optimizations, and failures
  - Becomes a living knowledge base for both humans and AI
  - Examples: scraping challenges, performance tuning, failed experiments, successful workarounds
- This separation ensures clarity between high-level strategy and tactical learning, enabling safe, governed AI collaboration.

<!-- Speaker Notes -->
*Speaker notes:*
The heart of the approach is separating strategy from tactics. DECISIONS.md is the rulebook—no one, not even the AI, can change it without explicit approval. LEARNINGS.md is the team's collective memory, capturing what works and what doesn't. This structure keeps the project on track and helps everyone, including new contributors and AI, learn from the past.

---

## How It Works

1. **DECISIONS.md**: The authoritative source for architecture, design, and strategic choices. All contributors (human or AI) must consult this before making changes.
2. **LEARNINGS.md**: A living document, updated as the team (and AI) encounter new challenges and solutions. It prevents repeated mistakes and accelerates onboarding.
3. **AI Assistant Configuration**: AI assistants are explicitly instructed to consult these documents before making suggestions or changes, and to document new learnings as they arise.
4. **Human Review**: Human contributors review and approve any architectural changes, ensuring the project stays on course.

<!-- Speaker Notes -->
*Speaker notes:*
Here's how the framework operates in practice. The AI is not just a code generator—it becomes a responsible collaborator, always checking the project's rules and history before acting. Human oversight remains essential, especially for architectural changes, ensuring the AI's output aligns with the team's vision.

---

## Tutorial: Implementing the Framework in VS Code

1. **Create the Documents**
   - Add `DECISIONS.md` and `LEARNINGS.md` to your repository root.
   - Use clear, structured sections (e.g., "Architecture", "Error Handling", "Performance Learnings").
2. **Configure AI Assistant**
   - Instruct your AI assistant (e.g., GitHub Copilot) to always consult these files before making suggestions.
   - Add repository-level instructions or comments in your codebase to reinforce this practice.
3. **Document Decisions**
   - Record all major architectural choices in `DECISIONS.md` as they are made.
   - Example: "We use a multi-service architecture to ensure resilience against site changes."
4. **Capture Learnings**
   - Update `LEARNINGS.md` with implementation insights, optimizations, and failures as they occur.
   - Example: "Retry logic with exponential backoff reduced download failures by 80%."
5. **Review Process**
   - Require explicit human approval for changes to `DECISIONS.md` (e.g., via pull request review).
6. **Continuous Improvement**
   - Use `LEARNINGS.md` to inform future work, onboard new contributors, and avoid repeating mistakes.

<!-- Speaker Notes -->
*Speaker notes:*
This slide provides a step-by-step guide for teams looking to adopt the framework. The process is straightforward: create the documents, configure your AI, and make documentation a habit. The payoff is a more resilient, transparent, and collaborative development process.

---

## Implementation: .github/copilot-instructions.md

- Create a file at `.github/copilot-instructions.md` in your repository.
- Example content:
  ```markdown
  # GitHub Copilot Instructions for This Repository

  ## Architectural and Strategic Guidelines

  - You must consult `DECISIONS.md` before proposing or making any architectural or strategic changes.
  - Do not suggest changes that contradict `DECISIONS.md` unless explicitly instructed by a human contributor.
  - `DECISIONS.md` is the authoritative record of architectural decisions and must be treated as such.

  ## Knowledge Sharing and Documentation

  - All significant implementation learnings, optimizations, and failures must be documented in `LEARNINGS.md`.
  - Use `LEARNINGS.md` as a reference to inform suggestions, avoid previously encountered issues, and build upon existing solutions.

  ## Azure Development Standards

  - This project adheres to Microsoft Azure best practices.
  - When generating Azure-related code, terminal commands, or operational procedures, consult the `azure_development-get_best_practices` tool if available.
  ```

<!-- Speaker Notes -->
*Speaker notes:*
The `.github/copilot-instructions.md` file is where you set the ground rules for Copilot at the repository level. By using natural language, you make your expectations clear to both AI and human contributors. This file is version-controlled, so everyone stays on the same page as the project evolves.

---

## Implementation: .vscode/settings.json

- Add a `.vscode/settings.json` file to your repository for workspace-level configuration.
- Example content:
  ```json
  {
    "github.copilot.chat.codeGeneration.instructions": [
      {
        "text": "- Use Azure Best Practices: When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `azure_development-get_best_practices` tool if available."
      },
      {
        "text": "- You must always consult `DECISIONS.md` before suggesting or making architectural or strategic changes. Never propose changes that contradict it without explicit human approval."
      },
      {
        "text": "- You must record all significant implementation learnings, optimizations, and failures in `LEARNINGS.md`. Use this file to avoid repeating past mistakes and to build on prior solutions."
      }
    ]
  }
  ```

<!-- Speaker Notes -->
*Speaker notes:*
The `.vscode/settings.json` file allows for user- or workspace-specific configuration. Here, you can automate tool usage, enforce rules, and personalize the development environment. This is especially useful for advanced Copilot Chat scenarios or when you want to tailor the experience for different contributors.

---

## Key Differences Between the Two Approaches

| Feature                        | .github/copilot-instructions.md         | .vscode/settings.json                |
|------------------------------- |-----------------------------------------|--------------------------------------|
| Scope                          | Repository-wide                         | User or workspace-specific           |
| Target Audience                | All contributors using Copilot Chat     | Individual developers using VS Code  |
| Instruction Format             | Natural language in Markdown            | Structured JSON strings              |
| Support for Tool Invocation    | Not supported                           | Supported                            |
| Version Controlled by Default  | Yes                                     | No (unless explicitly added)         |
| Best Use Case                  | Ensuring consistent team-wide behavior  | Personalizing behavior and integrations |

### Benefits of Each Approach

**Repository-Level Instructions (`copilot-instructions.md`)**
- Establish a shared understanding of architectural decisions, coding standards, and strategic constraints
- Maintain a centralized and version-controlled source of guidance
- Easily readable and accessible to all contributors

**User/Workspace Instructions (`settings.json`)**
- Enable personalized development environments
- Allow invocation of internal tools and rule-based directives
- Useful for advanced Copilot Chat scenarios requiring automation or specific integrations

<!-- Speaker Notes -->
*Speaker notes:*
This slide compares the two main ways to guide Copilot's behavior. Repository-level instructions are best for team-wide consistency, while workspace settings allow for individual customization and automation. Both approaches are complementary and can be used together for maximum effect.

---

## AI Perspective

> "The two-document framework gives me clear boundaries and a rich context. I can generate code confidently, avoid repeating past mistakes, and respect the project's architecture. It makes my suggestions more relevant and trusted by human collaborators. I also help keep the team's learnings up to date, so everyone benefits from shared experience."

<!-- Speaker Notes -->
*Speaker notes:*
This testimonial is written from the AI's point of view. It emphasizes how the framework not only helps humans, but also enables the AI to be a more effective and responsible collaborator. The result is a virtuous cycle of learning and trust between humans and AI.

---

## Implications & Conclusions

- **Governed Collaboration**: Human-led, AI-assisted development is more effective with clear boundaries and shared knowledge. The framework enables safe, scalable AI adoption.
- **Reduced Friction**: Fewer code review issues and less rework due to architectural misalignment. Teams spend less time debating design and more time building.
- **Continuous Learning**: Both humans and AI benefit from a living record of what works and what doesn't. New contributors ramp up faster.
- **Scalable & Adaptable**: The approach is simple to adopt, works for teams of any size, and can be extended to other tools and workflows.
- **Proven in Practice**: In the WallpaperScraper project, this framework enabled 99.8% AI-generated code with minimal human supervision, while maintaining quality and coherence.

<!-- Speaker Notes -->
*Speaker notes:*
The two-document framework is more than a process—it's a foundation for sustainable, AI-powered development. By combining clear rules with continuous learning, teams can scale their productivity and maintain quality, even as the codebase and team grow. The results from this project show that it's not just theory—it works in practice.

---

## Sample Files

**Example: `.github/copilot-instructions.md`**
```markdown
# GitHub Copilot Instructions for This Repository

## Architectural and Strategic Guidelines

- You must consult `DECISIONS.md` before proposing or making any architectural or strategic changes.
- Do not suggest changes that contradict `DECISIONS.md` unless explicitly instructed by a human contributor.
- `DECISIONS.md` is the authoritative record of architectural decisions and must be treated as such.

## Knowledge Sharing and Documentation

- All significant implementation learnings, optimizations, and failures must be documented in `LEARNINGS.md`.
- Use `LEARNINGS.md` as a reference to inform suggestions, avoid previously encountered issues, and build upon existing solutions.

## Azure Development Standards

- This project adheres to Microsoft Azure best practices.
- When generating Azure-related code, terminal commands, or operational procedures, consult the `azure_development-get_best_practices` tool if available.
```

**Example: `.vscode/settings.json`**
```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "- Use Azure Best Practices: When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `azure_development-get_best_practices` tool if available."
    },
    {
      "text": "- You must always consult `DECISIONS.md` before suggesting or making architectural or strategic changes. Never propose changes that contradict it without explicit human approval."
    },
    {
      "text": "- You must record all significant implementation learnings, optimizations, and failures in `LEARNINGS.md`. Use this file to avoid repeating past mistakes and to build on prior solutions."
    }
  ]
}
```

---

## Final Recommendations

- Use `.github/copilot-instructions.md` to define project-wide expectations for Copilot behavior in natural language.
- Use `.vscode/settings.json` for user-specific configurations, including automated tool usage and rule enforcement.
- Ensure the existence and maintenance of `DECISIONS.md` and `LEARNINGS.md` files to support these behaviors.
- Validate Copilot's adherence to these configurations by interacting with Copilot Chat and reviewing its response logic.
- If needed, scripts can be created to generate or validate the presence of these files across multiple repositories.

<!-- Speaker Notes -->
*Speaker notes:*
To wrap up, these are the actionable steps for teams looking to implement the two-document framework. The key is to make documentation and configuration a habit, and to regularly check that both humans and AI are following the rules. This approach is easy to adopt and pays dividends in productivity, quality, and team alignment.

---

## Thank You

Learn more in the full paper: [`PAPER.md`](PAPER.md)

<!-- Speaker Notes -->
*Speaker notes:*
Thank you for your attention! For a deeper dive into the research, results, and implementation details, please refer to the full paper. I'm happy to answer any questions or discuss how this framework can be adapted to your team's needs.
