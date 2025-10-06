# Task: Fix Templates Not Being Packaged (v0.5.1)

## Date
2025-10-04 12:12

## Prompt
User: "I tried a new project using the pipx-installed tool, and `air init` created the `.air` folder structure, but no `air-config.json` file. Please investigate this bug by reproducing in a temp folder"

Follow-up: "This work should be tracked as a task"

## Problem

When installing air-toolkit v0.5.0 via pipx/pip, the templates directory wasn't included in the package, causing `air init` to fail with:

```
✗ Templates directory not found at 
/Users/gpeddle/.local/pipx/venvs/air-toolkit/lib/python3.13/site-packages/air/templates
💡 Hint: Ensure air-toolkit is properly installed
```

**Result:** `.air/` directory created but no `air-config.json`, `README.md`, `CLAUDE.md`, or `.gitignore` files.

## Root Cause

The `pyproject.toml` file was missing the `[tool.setuptools.package-data]` section to explicitly include template files in the distribution package.

While Python packages (.py files) are automatically discovered by setuptools, **data files** like templates need to be explicitly declared.

## Actions Taken

1. **Reproduced the bug**
   - Created temp directory: `/tmp/test-air-init-bug`
   - Ran `air init test-project` with pipx-installed version
   - Confirmed: directory structure created but no files
   - Confirmed error: Templates directory not found

2. **Identified the issue**
   - Checked `pyproject.toml` packaging configuration
   - Found missing `[tool.setuptools.package-data]` section
   - Template files exist in source but not included in wheel

3. **Applied fix**
   - Added package-data configuration to `pyproject.toml`:
     ```toml
     [tool.setuptools.package-data]
     air = ["templates/**/*", "templates/**/**/*"]
     ```

4. **Verified fix**
   - Rebuilt package: `python -m build`
   - Checked wheel contents: Templates now included
   - Installed locally: `pip install --force-reinstall dist/air_toolkit-0.5.0-py3-none-any.whl`
   - Tested: `air init test-project-2` ✅ Success!
   - Verified all files created:
     - air-config.json ✅
     - README.md ✅
     - CLAUDE.md ✅
     - .gitignore ✅
     - .air/ directory structure ✅

5. **Version bump**
   - Will bump to v0.5.1 (bugfix release)
   - Update CHANGELOG.md

## Files Changed

- `pyproject.toml` (lines 55-56)
  - Added `[tool.setuptools.package-data]` section
  - Includes all template files recursively

## Outcome
✅ Success

Bug fixed! Templates are now properly packaged and `air init` works correctly in pipx/pip installations.

## Testing

**Before Fix:**
```bash
pipx install air-toolkit==0.5.0
air init test
# Result: Error - templates not found
```

**After Fix:**
```bash
pip install air-toolkit==0.5.1  # (once published)
air init test
# Result: ✓ Project created successfully
# Files: air-config.json, README.md, CLAUDE.md, .gitignore
```

## Notes

### Why This Happened

When developing with `pip install -e .` (editable mode), templates are accessible directly from the source directory, so this bug wasn't caught during development. It only appeared when installed as a packaged wheel.

### Package Data in Python

setuptools has three ways to include data files:
1. **MANIFEST.in** (legacy, works but requires separate file)
2. **package_data** in setup.py (deprecated for pyproject.toml)
3. **[tool.setuptools.package-data]** in pyproject.toml ✅ (modern approach)

We used option 3 as it's the current best practice for PEP 621 compliant projects.

### Template Files Included

```
air/templates/
├── ai/
│   ├── README.md.j2
│   └── task.md.j2
└── assessment/
    ├── CLAUDE.md.j2
    ├── README.md.j2
    └── gitignore.j2
```

All 5 template files are now properly packaged.

### Verification Command

To check if templates are in a wheel:
```bash
unzip -l dist/air_toolkit-0.5.1-py3-none-any.whl | grep templates
```

Should show all template files.

## Related Issues

This is why proper release testing is important:
1. Test in clean environment (not editable install)
2. Test via pipx/pip (not just source)
3. Test on different machines

Going forward, we should add this to the release checklist.
