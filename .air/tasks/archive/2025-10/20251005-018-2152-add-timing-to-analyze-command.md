# Task: Add timing information to air analyze command

## Date
2025-10-05 21:52

## Prompt
During `air analyze` add timing code and emit elapsed time for each Analysis step, as well as a total elapsed time at the end of the run.

## Actions Taken
1. Added `import time` to analyze.py
2. Implemented timing for single-repo analysis:
   - Overall analysis start/end time
   - Classification timing
   - Individual analyzer timing (security, performance, architecture, quality, code_structure)
   - Dependency checking timing
   - Display formatted timing summary with ⏱️ emoji
3. Implemented timing for multi-repo analysis:
   - Dependency graph build timing
   - Per-level timing (with repo count)
   - Dependency gap check timing
   - Total time and average per repo
4. Tested both single-repo and multi-repo timing output

## Files Changed
- `src/air/commands/analyze.py` - Added comprehensive timing throughout analysis workflow

## Outcome
✅ Success

Timing information is now displayed for all analysis operations:

**Single Repo Example (ng-anlx):**


**Multi-Repo Example (2 repos):**


## Notes
- Timing is displayed in seconds with 2 decimal precision
- Individual repo analyses show their timing even when part of multi-repo runs
- Multi-repo timing includes level-by-level breakdown for dependency-ordered analysis
- Helps identify performance bottlenecks (e.g., code_structure analyzer took 3.48s on meditech-rpa-cdk)
- The ⏱️ emoji makes timing sections easy to spot in output
