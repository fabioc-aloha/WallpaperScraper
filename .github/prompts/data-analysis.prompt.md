---
mode: "agent"
model: "gpt-4"
tools: ["workspace", "run_in_terminal", "read_file", "create_file"]
description: "Data analysis and visualization workflow"
---

# Data Analysis Episode Template

## Phase 1: Data Exploration and Understanding
- Load and inspect data structure, types, and quality
- Identify missing values, outliers, and data anomalies
- Generate descriptive statistics and initial visualizations
- Document data source and collection methodology

## Phase 2: Data Cleaning and Preprocessing
- Handle missing values with appropriate strategies
- Detect and address outliers based on domain knowledge
- Transform data types and normalize scales as needed
- Create derived features and engineered variables

## Phase 3: Analysis and Modeling
- Apply appropriate statistical or machine learning methods
- Validate assumptions and check model diagnostics
- Implement cross-validation and performance evaluation
- Document methodology and parameter choices

## Phase 4: Visualization and Reporting
- Create clear, informative visualizations
- Generate summary statistics and key findings
- Document insights and recommendations
- Prepare reproducible analysis scripts

Use Python data science libraries from ${workspaceFolder}/.venv
