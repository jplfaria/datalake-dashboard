# Genome Heatmap Viewer - Development Guide

## Project Overview

This is a **standalone genome visualization tool** that will be wrapped as a KBase narrative app. It displays pangenome data from BERDL databases as interactive heatmap tracks.

**Key Architecture Principle**: The viewer is **database-agnostic** - it dynamically adapts to any BERDL database without hardcoding organism names, gene counts, or field mappings.

## Deployment Model

```
┌─────────────────────────────────────────────────────────┐
│ KBase Narrative App (Future)                            │
│  ├─ Takes workspace object (BERDL DB)                   │
│  ├─ Runs generation scripts (Python)                    │
│  ├─ Outputs JSON data files                             │
│  └─ Serves standalone viewer (HTML/CSS/JS)              │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Standalone Viewer (Current)                             │
│  ├─ Pure HTML/CSS/JS (no frameworks)                    │
│  ├─ Canvas API for heatmap rendering                    │
│  ├─ D3.js for dendrogram & clustering                   │
│  ├─ Escher.js for metabolic maps                        │
│  └─ Loads pre-generated JSON data files                 │
└─────────────────────────────────────────────────────────┘
```

## Data Pipeline

### Input
**BERDL Database** (`berdl_tables.db`) - SQLite database with:
- `genome` - User genome + reference genomes
- `genome_features` - User genome genes with full annotations
- `pan_genome_features` - Reference genome genes (cluster mappings)
- `pangenome_cluster` - Cluster definitions
- `genome_reactions` - Metabolic reactions per genome
- `gene_phenotypes` - Essentiality and fitness data
- Other tables: ontology_terms, genome_ani, etc.

### Generation Scripts (Python)
All scripts auto-detect the user genome: `SELECT id FROM genome WHERE id LIKE 'user_%'`

1. **`generate_metadata.py`** → `metadata.json`
   - Organism name (parsed from genome_id)
   - Genome ID, assembly, taxonomy
   - Gene count, reference genome count

2. **`generate_genes_data.py`** → `genes_data.json`
   - Main data file: array of 36-field gene arrays
   - Handles split tables (genome_features + pan_genome_features)
   - Computes consistency scores from cluster annotations
   - Multi-cluster genes: take max score across clusters
   - Fields 0-28: core annotations, 29-35: new fields (reactions, flux, essentiality)

3. **`generate_tree_data.py`** → `tree_data.json`
   - UPGMA hierarchical clustering on Jaccard distances
   - Cluster presence/absence matrix
   - Genome metadata (taxonomy, ANI, stats)

4. **`generate_cluster_data.py`** → `cluster_data.json`
   - Pangenome cluster definitions
   - Member genomes per cluster
   - Conservation and annotation data

5. **`generate_reactions_data.py`** → `reactions_data.json`
   - Metabolic reactions from genome_reactions table
   - Flux data (rich/minimal media)
   - Gene-reaction mappings for cross-linking

### Output JSON Files
```
metadata.json          - Genome info (organism, ID, counts)
genes_data.json        - 3,235 × 36 gene data array
tree_data.json         - Dendrogram linkage + genome stats
cluster_data.json      - Pangenome cluster definitions
reactions_data.json    - Metabolic reactions + flux
metabolic_map_*.json   - Escher pathway maps (static)
config.json            - Track definitions (genome-agnostic)
```

## Phase 0: Database Migration (COMPLETED)

**Goal**: Migrate from old E. coli DB to new BERDL split-table schema and make everything database-agnostic.

### What We Did

#### 1. Updated All Generation Scripts
- **Dynamic user genome detection**: `WHERE id LIKE 'user_%'` instead of hardcoded
- **Split-table schema**: UNION genome_features + pan_genome_features
- **Consistency score computation**: Compare user gene vs all cluster members (not pre-computed)
- **Multi-cluster handling**: Semicolon-separated cluster IDs, use max score
- **Error handling**: Graceful fallbacks for missing tables (phenotype_module)

#### 2. Added 7 New Gene Fields (Indices 29-35)
- `REACTIONS` (29): Semicolon-separated reaction IDs
- `RICH_FLUX` (30): Metabolic flux in rich media
- `RICH_CLASS` (31): Flux class (blocked, forward, reverse, reversible, essential)
- `MIN_FLUX` (32): Metabolic flux in minimal media
- `MIN_CLASS` (33): Flux class in minimal media
- `PSORTB_NEW` (34): Updated subcellular localization
- `ESSENTIALITY` (35): Gene essentiality score (0-1 from phenotypes)

#### 3. Made Organism Metadata Dynamic
- Created `generate_metadata.py` to extract from DB
- Removed hardcoded organism info from config.json
- Viewer loads metadata.json and adapts automatically
- Organism name parsed from genome_id (e.g., `user_Acinetobacter_baylyi_ADP1_RAST` → "Acinetobacter baylyi ADP1")

#### 4. Activated Flux & Essentiality Tracks
- Updated config.json with 5 new active tracks
- Updated index.html for 6-category flux classes
- Reduced placeholder_tracks from 6 to 1 (only neighborhood remains)

#### 5. Migrated Test Data
- Organism: E. coli K-12 MG1655 (4,617 genes) → **Acinetobacter baylyi ADP1** (3,235 genes)
- Genomes: 36 → **14 genomes** (13 ref + 1 user)
- Fields: 29 → **36 fields** per gene
- All JSON data regenerated and verified

### Key Code Patterns from Phase 0

**Dynamic user genome detection:**
```python
user_genome_row = conn.execute(
    "SELECT id FROM genome WHERE id LIKE 'user_%' LIMIT 1"
).fetchone()
user_genome_id = user_genome_row["id"]
```

**Consistency score computation:**
```python
def compute_consistency(user_annotation, cluster_annotations):
    if not cluster_annotations or not user_annotation:
        return -1
    matches = sum(1 for ann in cluster_annotations if ann == user_annotation)
    return round(matches / len(cluster_annotations), 4)
```

**Multi-cluster handling:**
```python
cluster_ids = row["pangenome_cluster_id"].split(";") if row["pangenome_cluster_id"] else []
for cluster_id in cluster_ids:
    cluster_id = cluster_id.strip()
    if cluster_id:
        # Compute metric for this cluster
        # Take max across all clusters
```

**Split-table UNION:**
```python
# User genome from genome_features
user_genes = conn.execute("""
    SELECT * FROM genome_features WHERE genome_id = ?
""", (user_genome_id,)).fetchall()

# Reference genomes from pan_genome_features
ref_clusters = defaultdict(list)
for row in conn.execute("""
    SELECT cluster_id, genome_id, rast_function, ko, ...
    FROM pan_genome_features WHERE cluster_id IS NOT NULL
"""):
    ref_clusters[row["cluster_id"]].append(dict(row))
```

## Important Constraints

### Do NOT Hardcode
- ❌ Organism names, genome IDs, assembly IDs
- ❌ Gene counts, reference genome counts
- ❌ Field indices (use config.json mappings)
- ❌ Pangenome cluster counts

### Always Use
- ✅ Dynamic detection: `WHERE id LIKE 'user_%'`
- ✅ Config-driven field mappings: `F.CONS_FRAC`, `F.AVG_CONS`
- ✅ Graceful fallbacks for missing data: `try/except`, default values
- ✅ Database queries over file parsing
- ✅ Generate metadata from DB, not config

## Tech Stack

**Frontend (Standalone Viewer)**
- Vanilla HTML/CSS/JS - No build step, no frameworks
- Canvas API - Heatmap rendering (high performance)
- D3.js v7 - Dendrogram, clustering visualization
- Escher.js 1.7.3 - Metabolic pathway maps

**Backend (Generation Scripts)**
- Python 3.8+
- SQLite3 (database queries)
- NumPy, SciPy (clustering, distance calculations)
- Pandas (optional, for data processing)

**Data Format**
- JSON - All data files use compact JSON (no whitespace)
- Arrays - Gene data as arrays (not objects) for size efficiency
- Indices - Field access by index (faster than key lookup)

## File Organization

```
genome-heatmap-viewer/
├── index.html                      # Main viewer (standalone app)
├── config.json                     # Track definitions (genome-agnostic)
├── kbase_logo.png                  # Branding
│
├── generate_metadata.py            # Extract organism info from DB
├── generate_genes_data.py          # Main gene data extraction
├── generate_tree_data.py           # Dendrogram clustering
├── generate_cluster_data.py        # Pangenome clusters
├── generate_reactions_data.py      # Metabolic reactions
│
├── metadata.json                   # Organism info (generated)
├── genes_data.json                 # Gene data array (generated)
├── tree_data.json                  # Dendrogram (generated)
├── cluster_data.json               # Clusters (generated)
├── reactions_data.json             # Reactions (generated)
├── metabolic_map_full.json         # Escher map (static)
├── metabolic_map_core.json         # Escher map (static)
│
├── CLAUDE.md                       # This file
├── README.md                       # User documentation
├── PROJECT_STATUS.md               # Implementation status
├── COMPREHENSIVE_GAP_ANALYSIS.md   # Phase planning
│
└── .gitignore                      # Ignore *.db files (too large)
```

## Development Workflow

### Adding a New Track

1. **Add field to gene data** (if needed)
   - Update `generate_genes_data.py` to extract field from DB
   - Add to gene array at next available index
   - Update `config.json` fields mapping

2. **Define track in config.json**
   ```json
   {
     "id": "my_track",
     "name": "My Track Name",
     "field": "MY_FIELD",
     "type": "sequential|categorical|consistency|binary",
     "enabled": false,
     "categories": "my_categories"  // if categorical
   }
   ```

3. **Update index.html** (if needed)
   - Add color scale for new track type
   - Add tooltip description in TRACKS array
   - Render logic already handles most cases automatically

4. **Regenerate data**
   ```bash
   python3 generate_genes_data.py
   ```

### Adding a New Data Source

1. **Create `generate_X_data.py`** script
2. **Add to config.json** `data_files`
3. **Add lazy-load in index.html** (see Tree/Cluster/Metabolic tabs)
4. **Document in CLAUDE.md**

## Common Issues & Solutions

### Issue: Consistency scores are all NULL
**Cause**: Old DB had pre-computed scores; new DB requires computation
**Solution**: Implemented `compute_consistency()` in generate_genes_data.py

### Issue: Multi-cluster genes show wrong values
**Cause**: Gene belongs to multiple clusters (semicolon-separated IDs)
**Solution**: Split cluster IDs, compute for each, take max value

### Issue: sqlite3.Row has no .get() method
**Cause**: sqlite3.Row doesn't support dict .get() method
**Solution**: Use `row["key"] if "key" in row.keys() else default`

### Issue: phenotype_module table not found
**Cause**: Table doesn't exist in some DB versions
**Solution**: Wrap in try/except, skip gracefully with warning

### Issue: Organism name hardcoded
**Cause**: Legacy approach assumed single organism
**Solution**: Created generate_metadata.py to extract from DB dynamically

## Next Steps: Phase 1

See COMPREHENSIVE_GAP_ANALYSIS.md for full plan. Phase 1 focus:
- Phenotype data integration
- Fitness score visualization
- Missing BERDL dashboard features
- Advanced drill-down views

## Testing

**Manual Testing:**
```bash
# Start local server
python3 -m http.server 8889

# Open browser
open http://localhost:8889/

# Check console for errors
# Verify KPI stats match database
# Test track toggling, sorting, search
```

**Playwright Tests:**
```bash
# Run test suite
npm test

# Note: Tests currently expect E. coli data - need update for ADP1
```

## Git Workflow

```bash
# Never commit database files (too large for GitHub)
echo "*.db" >> .gitignore

# Always commit generated JSON files
git add metadata.json genes_data.json tree_data.json cluster_data.json reactions_data.json

# Descriptive commits with Co-Authored-By line
git commit -m "Add essentiality track

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

## Memory Management

This codebase uses persistent auto memory at:
`/Users/jplfaria/.claude/projects/-Users-jplfaria-repos-genome-heatmap-viewer/memory/`

- `MEMORY.md` - Key facts, loaded into every session (keep concise, <200 lines)
- Topic files - Detailed notes on specific areas

Update memory when you learn:
- Critical bugs and their fixes
- Database schema quirks
- Performance optimizations
- User preferences

Do NOT save in memory:
- Temporary session state
- In-progress work
- Speculative ideas
- Session-specific context
