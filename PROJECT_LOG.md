# PROJECT_LOG.md

## 2026-05-12 - Project Root Directory Cleanup

### Context

After the major refactoring, the project root still contained various system files, temporary directories, and unorganized example data that cluttered the repository structure.

### Changes

**Removed Files**
- `.DS_Store` - macOS system file
- `SDF_keys_short.txt` - Obsolete key list
- `INIT.md` - No longer needed after refactoring completion

**Deleted Directories**
- `output/` - Old generated files (refs.bib, keys.txt, etc.)
- `temp/` - Temporary working files

**Reorganized**
- Moved `bib_LaMET/` and `bib_SDF/` to `examples/` directory for better organization

**Updated**
- `.gitignore` - Removed exclusions for bib directories to track examples

### Result

The project root now contains only essential files and directories:
- Core documentation (SPEC, AGENTS, CLAUDE, README, PROJECT_LOG)
- Source code (`src/`)
- Example data (`examples/`)
- Configuration files (requirements.txt, .gitignore, LICENSE)

---

## 2026-05-12 - Major Repository Refactoring

### Context

The repository contained a collection of standalone Python scripts for BibTeX management without clear structure. The `INIT.md` protocol was present but not applied to the repository itself.

### Changes

**Directory Restructure**
- Reorganized code into `src/` with three logical modules:
  - `src/core/` - Shared utilities (from `bib_utils.py`)
  - `src/commands/` - Command-line tools (from `bib_*.py` and `*_keys.py` scripts)
  - `src/inspire/` - INSPIRE-HEP integration (from `sync_inspire_citations.py`)

**Documentation**
- Created `SPEC.md` - Project structure and module responsibilities
- Created `AGENTS.md` - Coding conventions and workflow rules
- Created `CLAUDE.md` - Quick entry point for AI agents
- Updated `README.md` - User-facing documentation aligned with new structure

**Environment**
- Created `.gitignore` with Python-specific ignores
- Created `requirements.txt` with explicit dependency (bibtexparser)
- Initialized `.venv` for local Python environment

### Rationale

The previous flat structure made it difficult to understand module relationships and responsibilities. The new structure:
- Groups related functionality logically
- Separates reusable utilities from command implementations
- Makes dependencies between modules explicit
- Follows Python package conventions

### Migration Notes

Old scripts can be located in the new structure:
- `bib_utils.py` → `src/core/utils.py`
- `bib_joint.py` → `src/commands/merge.py`
- `bib_unique.py` → `src/commands/deduplicate.py`
- `bib_folder.py` → `src/commands/process_folder.py`
- `compare_keys.py` → `src/commands/compare.py`
- `find_repeat_key.py` → `src/commands/find_duplicates.py`
- `sync_inspire_citations.py` → `src/inspire/sync.py`

All functionality remains identical; only import paths and file locations changed.
