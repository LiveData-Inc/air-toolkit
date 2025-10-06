# Task: Move air-config.json to .air/ folder (Breaking Change for v0.6.3)

## Date
2025-10-06 06:54

## Prompt
For v0.6.3, a breaking change is to move the air-config.json file inside the .air folder. This is a breaking change and must be fully implemented such that all code uses the new location, and `air upgrade` checks for and corrects the problem if the file is in the wrong location (the project root folder). Update all documentation and all prompts to reflect the change.

## Actions Taken
1. Created task file with ordinal-based naming
2. Analyzed all references to air-config.json in codebase (56 files)
3. Updated filesystem.py:
   - Added get_config_path() helper function
   - Updated get_project_root() to check both new and legacy locations
   - Updated load_config() to use get_config_path()
4. Updated upgrade.py with migration logic:
   - Added migrate_config action to detect and move config from root to .air/
   - Updated backup logic to handle both locations
   - Added _migrate_config() helper function
5. Updated init.py to create config in .air/ using get_config_path()
6. Updated all command files to use get_config_path():
   - status.py, validate.py, link.py, pr.py, summary.py
   - classify.py, review.py, claude.py, completion.py
7. Updated core/models.py ProjectStructure to reference .air/air-config.json
8. Updated templates/assessment/README.md.j2 for new config location
9. Batch updated documentation files:
   - CLAUDE.md, README.md, QUICKSTART.md
   - docs/COMMANDS.md, docs/ARCHITECTURE.md, PROJECT-STATUS.md
10. Updated CHANGELOG.md with v0.6.3 breaking change notice
11. Batch updated all test files (6 files) for new config location
12. Fixed test failures by ensuring .air directory exists before writing config
13. Verified all tests pass:
    - test_filesystem.py: 18/18 passed
    - test_commands.py (init): 9/9 passed  
    - test_upgrade_command.py: 20/20 passed

## Files Changed
- `src/air/services/filesystem.py` - Added get_config_path(), updated get_project_root() and load_config()
- `src/air/commands/upgrade.py` - Added migration logic and _migrate_config() function
- `src/air/commands/init.py` - Updated to use get_config_path()
- `src/air/commands/status.py` - Updated to use get_config_path()
- `src/air/commands/validate.py` - Updated to use get_config_path()
- `src/air/commands/link.py` - Updated to use get_config_path()
- `src/air/commands/pr.py` - Updated to use get_config_path()
- `src/air/commands/summary.py` - Updated to use get_config_path()
- `src/air/commands/classify.py` - Updated to use get_config_path()
- `src/air/commands/review.py` - Updated to use get_config_path()
- `src/air/commands/claude.py` - Updated to use get_config_path()
- `src/air/utils/completion.py` - Updated to use get_config_path()
- `src/air/core/models.py` - Updated ProjectStructure to reference .air/air-config.json
- `src/air/templates/assessment/README.md.j2` - Updated config location references
- `CLAUDE.md` - Updated all air-config.json references
- `README.md` - Updated all air-config.json references
- `QUICKSTART.md` - Updated all air-config.json references
- `docs/COMMANDS.md` - Updated all air-config.json references
- `docs/ARCHITECTURE.md` - Updated all air-config.json references
- `PROJECT-STATUS.md` - Updated all air-config.json references
- `CHANGELOG.md` - Added v0.6.3 breaking change section
- `tests/integration/test_commands.py` - Updated config paths
- `tests/integration/test_upgrade_command.py` - Updated config paths
- `tests/unit/test_errors.py` - Updated config paths
- `tests/unit/test_filesystem.py` - Updated config paths and added .air directory creation
- `tests/unit/test_link.py` - Updated config paths
- `tests/unit/test_templates.py` - Updated config paths

## Outcome
✅ Success

Breaking change fully implemented for v0.6.3:
- Config file location moved from project root to `.air/air-config.json`
- Centralized config path resolution via `get_config_path()` helper
- Automatic migration via `air upgrade --force`
- Backward compatibility: all commands detect and use correct location
- All 47 tests passing (18 filesystem + 9 init + 20 upgrade)
- Documentation and templates updated throughout

## Notes
This breaking change improves project organization by keeping all AIR-specific files in the `.air/` directory. The migration is seamless for users - they just need to run `air upgrade --force` on existing projects. New projects automatically use the new location.
