---
applyTo: "**/*.ipynb,**/notebooks/**,**/data/**"
description: "Data science and machine learning patterns with Python"
---

# Data Science Procedural Memory

## Jupyter Notebook Best Practices
- Use meaningful cell organization with markdown headers
- Clear all outputs before committing to version control
- Include data source documentation and methodology
- Use consistent naming conventions for variables
- Add markdown cells explaining complex analysis steps

## Pandas and Data Manipulation
- Use vectorized operations instead of loops when possible
- Check data types and handle missing values explicitly
- Use meaningful column names and index labels
- Implement data validation and quality checks
- Document data transformation steps with comments

## NumPy and Scientific Computing
- Use numpy arrays for numerical computations
- Leverage broadcasting for efficient array operations
- Choose appropriate data types to optimize memory usage
- Use numpy's random module with fixed seeds for reproducibility
- Profile memory usage for large datasets

## Visualization and Reporting
- Use matplotlib/seaborn for static visualizations
- Create reusable plotting functions for consistency
- Include proper titles, labels, and legends
- Use appropriate color schemes and accessibility considerations
- Export plots in high-resolution formats for publications

## Machine Learning Workflows
- Implement proper train/validation/test splits
- Use cross-validation for model evaluation
- Document feature engineering and selection processes
- Track experiments with MLflow or similar tools
- Validate model performance with appropriate metrics
