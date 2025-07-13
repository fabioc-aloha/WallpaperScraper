---
mode: "agent"
model: "gpt-4"
tools: ["workspace", "run_in_terminal", "read_file"]
description: "Python performance analysis and optimization"
---

# Performance Optimization Episode Template

## Phase 1: Performance Profiling and Analysis
- Use cProfile and line_profiler to identify bottlenecks
- Analyze memory usage with memory_profiler
- Identify CPU-intensive operations and I/O bottlenecks
- Measure baseline performance metrics

## Phase 2: Optimization Strategy Planning
- Prioritize optimizations based on impact and effort
- Consider algorithmic improvements and data structure changes
- Evaluate opportunities for caching and memoization
- Plan for parallel processing where appropriate

## Phase 3: Implementation and Testing
- Implement targeted optimizations incrementally
- Use numpy and scipy for numerical computations
- Apply generator patterns for memory efficiency
- Optimize database queries and I/O operations

## Phase 4: Validation and Monitoring
- Measure performance improvements against baseline
- Ensure correctness is maintained through testing
- Monitor production performance and resource usage
- Document optimization techniques for future reference

Use Python performance tools from ${workspaceFolder}/.venv
