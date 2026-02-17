# GENOME HEATMAP VIEWER — COMPREHENSIVE GAP ANALYSIS & BUILD PLAN
**Analysis Date:** 2026-02-14
**Current Commit:** eb19ca9
**Analyzed By:** Claude Opus 4.6 with 3 specialized agents

---

## EXECUTIVE SUMMARY

This document provides an exhaustive analysis comparing:
1. **Current Genome Heatmap Viewer capabilities** (E. coli K-12, 4,617 genes, 35 ref genomes)
2. **New BERDL database schema** (ADP1, 3,235 genes, flux/phenotype/fitness data)
3. **BERDL Reference Dashboards** (Adam Arkin's production dashboards)
4. **Meeting requirements** (touchvase_dash.txt transcript, Chris Henry guidance)

**Key Findings:**
- ✅ **22 capabilities fully functional** (tracks, tree, clusters, metabolic map)
- ⚠️ **3 capabilities broken** (metabolic map data is wrong organism)
- ❌ **6 placeholder tracks** awaiting data
- 🆕 **34 new data fields** available in new DB schema
- 📊 **8 visualization types** from reference dashboards not yet implemented

---

## PART 1: CURRENT STATE ASSESSMENT

### 1.1 What We Have Working ✅

| Category | Feature | Status | Test Coverage |
|----------|---------|--------|---------------|
| **Data Pipeline** | 4 extraction scripts (genes, tree, cluster, reactions) | ✅ STABLE | 13 tests |
| **Tracks Tab** | 24 active data tracks with Canvas heatmap | ✅ STABLE | 8 tests |
| **Tracks Tab** | 6 analysis view presets | ✅ STABLE | 2 tests |
| **Tracks Tab** | 7 sort presets | ✅ STABLE | 2 tests |
| **Tracks Tab** | Gene search (ID/function/KO) | ✅ STABLE | 2 tests |
| **Tracks Tab** | Zoom 1x-100x with minimap navigation | ✅ STABLE | 4 tests |
| **Tracks Tab** | Gene detail panel (click-to-open) | ✅ STABLE | 2 tests |
| **Tree Tab** | UPGMA dendrogram (36 genomes, Jaccard distance) | ✅ STABLE | 5 tests |
| **Tree Tab** | 3 collapsible stat bars (genes, clusters, core %) | ✅ STABLE | 1 test |
| **Tree Tab** | User genome highlighting | ✅ STABLE | 1 test |
| **Cluster Tab** | UMAP scatter (2 embedding modes, 4,617 genes) | ✅ STABLE | 5 tests |
| **Cluster Tab** | Color by 10 track options | ✅ STABLE | 1 test |
| **Cluster Tab** | Zoom/pan with mouse | ✅ MANUAL | 0 tests |
| **Metabolic Map Tab** | Escher pathway maps (2 maps: full/core) | ✅ STABLE | 2 tests |
| **Metabolic Map Tab** | Reaction coloring (conservation/flux) | ⚠️ WRONG DATA | 1 test |
| **Metabolic Map Tab** | Reaction detail panel (click-to-open) | ✅ STABLE | 1 test |
| **Global** | 4-tab navigation with lazy loading | ✅ STABLE | 2 tests |
| **Global** | KPI summary bar (7 stats) | ✅ STABLE | 4 tests |
| **Global** | KBase-branded UI (teal/blue theme) | ✅ STABLE | - |
| **Testing** | 71 Playwright tests (9 suites) | ✅ PASSING | - |

**Gene Data Fields (29):**
- ID, FID, LENGTH, START, STRAND, CONS_FRAC, PAN_CAT, FUNC
- N_KO, N_COG, N_PFAM, N_GO, N_EC, N_MODULES
- LOC, RAST_CONS, KO_CONS, GO_CONS, EC_CONS, BAKTA_CONS, AVG_CONS, EC_AVG_CONS, EC_MAP_CONS
- SPECIFICITY, IS_HYPO, HAS_NAME, AGREEMENT, CLUSTER_SIZE, PROT_LEN

### 1.2 What's Broken ⚠️

| Issue | Impact | Root Cause | Fix Required |
|-------|--------|------------|--------------|
| **Metabolic Map data is Acinetobacter** | HIGH | `reactions_data.json` generated from placeholder TSV | Switch `generate_reactions_data.py` to new DB schema |
| **Gene cross-links to Tracks tab** | HIGH | Gene IDs don't match (Acinetobacter vs E. coli) | Same as above |
| **Reaction conservation %** | MEDIUM | Comparing against 14 Acinetobacter genomes instead of 35 E. coli | Same as above |

### 1.3 What's Placeholder (Awaiting Data) ⏳

| Track | Status | Notes |
|-------|--------|-------|
| Neighborhood Conservation* | PENDING | Awaiting BERDL pipeline update |
| Flux (minimal media)* | PENDING | **NOW AVAILABLE** in new DB schema |
| Flux (rich media)* | PENDING | **NOW AVAILABLE** in new DB schema |
| Rxn Class (minimal)* | PENDING | **NOW AVAILABLE** in new DB schema |
| Rxn Class (rich)* | PENDING | **NOW AVAILABLE** in new DB schema |
| # Phenotypes* | PENDING | **NOW AVAILABLE** in new DB schema |
| # Fitness Scores* | PENDING | **NOW AVAILABLE** in new DB schema |

---

## PART 2: NEW DATABASE SCHEMA (13 Tables, 34 New Fields)

### 2.1 Schema Overview

**Source:** `/Users/jplfaria/Downloads/berdl_tables (1).db` and `berdl_tables (2).db` (identical, 132 MB each)

**Organism:** Acinetobacter baylyi ADP1 (3,235 genes, 14 genomes)

**Tables:**
1. `genome` (14 genomes)
2. `genome_ani` (1 ANI record)
3. `genome_features` (3,235 genes - **USER GENOME ONLY**)
4. `pan_genome_features` (43,754 genes - **REFERENCE GENOMES ONLY**)
5. `genome_reactions` (17,984 reactions)
6. `gene_reaction_data` (12,311 gene-reaction links)
7. `gene_phenotypes` (239,584 gene-phenotype associations)
8. `growth_phenotype_summary` (573 records)
9. `growth_phenotypes_detailed` (121,519 phenotype simulations)
10. `missing_functions` (243 commonly gapfilled reactions)
11. `ontology_terms` (11,539 terms)
12. `ontology_definitions` (8 ontology sources)
13. `ontology_relationships` (4,728 relationships)

**CRITICAL STRUCTURAL CHANGE:**
- **Old DB:** All genes in `genome_features`
- **New DB:** User genome in `genome_features`, references in `pan_genome_features`
- **Scripts must UNION both tables to get full gene set**

### 2.2 New Data Fields (34)

#### **From `genome_features` (8 fields):**

| Field | Type | Coverage | Values | Visualization Use |
|-------|------|----------|--------|-------------------|
| `reactions` | TEXT | 26.8% | Semicolon-separated rxn IDs | Gene-to-reaction links |
| `rich_media_flux` | REAL | 26.8% | 0-119.3, avg 2.20 | **NEW TRACK:** Flux (rich) |
| `rich_media_class` | TEXT | 26.8% | essential/variable/blocked (3 cats) | **NEW TRACK:** Rxn Class (rich) |
| `minimal_media_flux` | REAL | 26.8% | 0-13.25, avg 0.37 | **NEW TRACK:** Flux (minimal) |
| `minimal_media_class` | TEXT | 26.8% | essential/variable/blocked (3 cats) | **NEW TRACK:** Rxn Class (minimal) |
| `psortb` | TEXT | 18.7% | Cytoplasmic/CytoplasmicMembrane/etc. | **REPLACE LOC:** Better localization |
| `rast_consistency` | REAL | 0% | **ALL NULL** | **COMPUTE IN SCRIPT** (like old DB) |
| `other_rast_annotations` | TEXT | 0% | **ALL EMPTY** | Ignore |

#### **From `genome_reactions` (9 fields):**

| Field | Type | Values | Visualization Use |
|-------|------|--------|-------------------|
| `genome_id` | TEXT | "user_Acinetobacter_..." | Filter to user genome |
| `reaction_id` | TEXT | "rxn00001", etc. | Match to Escher maps |
| `genes` | TEXT | Gene association logic (GPR) | Gene cross-links |
| `equation_names` | TEXT | "H2O + NAD = NADH + O2 + H+" | Reaction detail panel |
| `equation_ids` | TEXT | "cpd00001 + cpd00003 = ..." | Compound mapping |
| `directionality` | TEXT | forward/reverse/reversible | Reaction detail panel |
| `upper_bound/lower_bound` | INTEGER | Flux bounds | FBA model constraints |
| `gapfilling_status` | TEXT | none (92%)/rich (4.5%)/minimal (3.2%) | Reaction detail panel |
| `rich_media_flux/minimal_media_flux` | REAL | Flux values | **METABOLIC MAP:** Color by flux |
| `rich_media_class/minimal_media_class` | TEXT | 6 categories* | **METABOLIC MAP:** Color by flux class |

**6 flux class categories** (expanded from current 3):
- `forward_only`, `reverse_only`, `essential_forward`, `essential_reverse`, `reversible`, `blocked`

#### **From `gene_phenotypes` (12 fields):**

| Field | Type | Coverage | Values | Visualization Use |
|-------|------|----------|--------|-------------------|
| `phenotype_id` | TEXT | 71% | "cpd00027" | Phenotype cross-links |
| `phenotype_name` | TEXT | 71% | "D-Glucose" | **NEW TRACK:** Phenotype names |
| `association_sources` | TEXT | 71% | model_pred/fitness_match | Association confidence |
| `model_pred_reactions` | TEXT | 71% | Linking reactions | Gene→phenotype pathway |
| `model_pred_max_flux` | REAL | 71% | Max flux | **NEW TRACK:** Phenotype flux |
| `fitness_match` | TEXT | 60% | yes/no | **NEW TRACK:** Has fitness data |
| `fitness_max/min/avg` | REAL | 60% | -5.0 to 2.0 | **NEW TRACK:** Fitness score |
| `fitness_count` | REAL | 60% | 1-10 experiments | Fitness confidence |
| `essentiality_fraction` | REAL | 71% | 0.0-1.0 | **NEW TRACK:** Gene essentiality |

**Coverage stats:**
- 2,297/3,235 genes (71%) have phenotype data
- 101,853/239,584 phenotype records (60%) have fitness data
- Average 74 phenotypes per gene

#### **From `growth_phenotype_summary` (5 fields):**

| Field | Type | Use |
|-------|------|-----|
| `false_positives/negatives` | INTEGER | Model validation stats |
| `true_positives/negatives` | INTEGER | Model validation stats |
| `accuracy` | REAL | Model quality score |

### 2.3 Data Completeness Summary

| Data Type | Coverage | Notes |
|-----------|----------|-------|
| **Basic annotation** | 100% | RAST + Bakta functions |
| **Ontology terms** | 73-96% | KO (96%), COG (96%), Pfam (90%), GO (73%), EC (47%) |
| **Pangenome clusters** | 100% | All genes assigned |
| **Localization (PSORTb)** | 18.7% | Sparse but useful (was ~100% in old DB) |
| **Metabolic reactions** | 26.8% | Genes with metabolic roles |
| **Gene flux (rich/minimal)** | 26.8% | Genes in FBA model |
| **Phenotype associations** | 71% | **EXCELLENT** coverage |
| **Fitness data** | 60% of phenotypes | **VERY GOOD** experimental validation |
| **Consistency scores** | 0% | **ALL NULL** - must compute in script |

---

## PART 3: REFERENCE DASHBOARDS (Adam Arkin's BERDL Output)

**URLs:**
- https://genomics.lbl.gov/~aparkin/KBase/berdl_output_ADP1.html
- https://genomics.lbl.gov/~aparkin/KBase/berdl_output_ECOLI.html

### 3.1 Dashboard Architecture

**Structure:** Single-page, 14 sections, dark theme (#1a1a2e background, cyan accent)

**Sections:**
1. KPI Summary Cards (8 metrics)
2. Gene Content Dendrogram (UPGMA, Jaccard)
3. Genome Ribbon (sortable, searchable, 4 functional categories)
4. Functional Category Improbability (box-whisker plots, z-score outliers)
5. Drill-down Heatmaps (inline expansion of cluster presence/absence)
6. Gapfilled Reactions (5-evidence matrix)
7. Missing Core Genes (tiered by category)
8. KEGG Pathway Completeness (z-score ranking)
9. KEGG Module Completeness (z-score ranking)
10. Metabolic Pathway Maps (Escher with support coloring)
11. PSORTb Subcellular Localization (donut chart)
12. Growth Phenotype Predictions (FBA validation)
13. Phenotype Prediction Landscape (477-genome accuracy histogram)
14. Gene Essentiality Matrix (rich vs. minimal cross-tab)

### 3.2 Features We DON'T Have Yet

| Feature | BERDL Dashboards | Current GHV | Gap |
|---------|-----------------|-------------|-----|
| **KPI Summary Cards** | ✅ 8 metrics at top | ❌ KPI bar in sidebar | **ADD:** Move KPI to top, expand to 8 metrics |
| **Gene Content Dendrogram** | ✅ UPGMA, Jaccard | ❌ No pangenome tree | **ADD:** Already have tree_data.json, need to render |
| **Statistical Outlier Detection** | ✅ Z-score flagging, box-whisker plots | ❌ No stats | **ADD:** Compute z-scores for functional categories |
| **Drill-down Heatmaps** | ✅ Click category → cluster matrix | ❌ No drill-down | **ADD:** Inline expansion on category click |
| **Gapfilled Reactions** | ✅ 5-evidence matrix | ❌ No gapfilling view | **FUTURE:** Requires gapfilling_status in reactions |
| **Missing Core Genes** | ✅ Tiered list | ❌ No missing core view | **ADD:** Filter to core-absent genes |
| **KEGG Pathway Completeness** | ✅ Z-score ranking | ❌ No pathway view | **ADD:** KO→pathway mapping, z-score comparison |
| **KEGG Module Completeness** | ✅ Z-score ranking | ❌ No module view | **ADD:** Module coverage already computed (N_MODULES field) |
| **Global Gene Search** | ✅ Integrated search box | ❌ Per-tab search only | **ENHANCE:** Global search in header |
| **Sortable Genome Ribbon** | ✅ 3 sort modes | ✅ 7 sort modes | **CURRENT:** GHV has MORE sort options |
| **Phenotype Validation Histogram** | ✅ 477-genome landscape | ❌ No phenotype view | **ADD:** When phenotype data integrated |
| **Gene Essentiality Matrix** | ✅ Rich vs. minimal cross-tab | ❌ No essentiality view | **ADD:** When essentiality data integrated |

### 3.3 Features We Have That They DON'T

| Feature | Current GHV | BERDL Dashboards |
|---------|-------------|------------------|
| **Multi-track heatmap** | ✅ 24 active tracks | ❌ Only 4 ribbon categories |
| **Consistency scores** | ✅ 6 sources (RAST, KO, GO, EC, Bakta, Avg) | ❌ Only RAST consistency |
| **Annotation specificity** | ✅ Precision metric (0-1) | ❌ Not shown |
| **Cluster scatter plots** | ✅ UMAP embeddings (2 modes) | ❌ No clustering view |
| **Interactive zoom/pan** | ✅ Minimap, zoom slider | ❌ Static visualizations |
| **Analysis view presets** | ✅ 6 curated presets | ❌ No presets |
| **71 Playwright tests** | ✅ Automated validation | ❌ No tests |

---

## PART 4: MEETING REQUIREMENTS (touchvase_dash.txt Transcript)

### 4.1 Key Requirements Mentioned

**From Chris Henry (23 mentions):**
1. ✅ "Flux information for both pan genome and genome" → **NOW IN NEW DB**
2. ✅ "Reaction essentiality in genes table" → **NOW IN NEW DB** (rich/minimal media)
3. ✅ "Flux on Escher map view" → **READY TO IMPLEMENT**
4. ✅ "Essentiality as ribbon view" → **READY TO IMPLEMENT**
5. ✅ "Fitness data fully integrated" → **NOW IN NEW DB** (60% coverage)
6. ✅ "Gene-phenotype table" → **NOW IN NEW DB** (gene_phenotypes)
7. ✅ "Growth phenotype summary table" → **NOW IN NEW DB**
8. ✅ "Media table for rich/minimal definitions" → **MISSING** (Chris said he'd add)
9. ⏳ "Genome reactions table" → **NOW IN NEW DB** (was TSV, now in DB)
10. ❌ "Distance matrix for phenotype genomes" → **NOT IN DB YET**
11. ❌ "Tree view with phenotype data" → **AWAITING DISTANCE MATRIX**
12. ✅ "6 TSV files from app" → **SCRIPT GENERATES 6 TABLES**

**From Filipe/Boris (4 mentions):**
1. ✅ "Ontology prefix standardization" → **DONE** (ontology_underscore_name)
2. ✅ "All ontologies in ontology_terms table" → **NOW IN NEW DB** (11,539 terms)
3. ✅ "Annotation files with feature_id + ontology columns" → **RAST FORMAT CONFIRMED**
4. ✅ "Media composition table" → **PENDING** (Chris to add)

**From Jose (8 mentions):**
1. ✅ "Dashboard as standalone app" → **CURRENT GHV IS STANDALONE**
2. ✅ "Take database as input" → **SCRIPTS USE DB**
3. ✅ "JSON file output for viz" → **CURRENT PIPELINE**
4. ⏳ "KBase module deployment" → **PENDING** (Chris to initialize)
5. ✅ "Test locally without KBase" → **CURRENT GHV WORKS STANDALONE**
6. ❌ "Poster updates with dashboard elements" → **NOT DONE YET**

### 4.2 Visualization Requirements from Meeting

| Visualization Type | Mentioned By | Status |
|--------------------|-------------|--------|
| Flux heatmap (rich/minimal) | Chris | ⏳ DATA READY, UI NOT BUILT |
| Flux class ribbon | Chris | ⏳ DATA READY, UI NOT BUILT |
| Essentiality ribbon | Chris | ⏳ DATA READY, UI NOT BUILT |
| Fitness score track | Chris | ⏳ DATA READY, UI NOT BUILT |
| Phenotype count track | Chris | ⏳ DATA READY, UI NOT BUILT |
| Phenotype tree view | Chris | ❌ AWAITING DISTANCE MATRIX |
| Gapfilled reactions matrix | Chris | ⏳ DATA READY, UI NOT BUILT |
| Growth phenotype summary | Chris | ⏳ DATA READY, UI NOT BUILT |

---

## PART 5: COMPREHENSIVE GAP ANALYSIS

### 5.1 Data Pipeline Gaps

| Gap | Impact | Fix Required | Priority |
|-----|--------|--------------|----------|
| **generate_genes_data.py uses old schema** | HIGH | Add 7 new fields: reactions, rich_media_flux/class, minimal_media_flux/class, essentiality | **P0** |
| **generate_reactions_data.py uses TSV** | HIGH | Rewrite to query `genome_reactions` table | **P0** |
| **No phenotype extraction script** | MEDIUM | Create `generate_phenotypes_data.py` | **P1** |
| **No growth phenotype script** | LOW | Create `generate_growth_data.py` | **P2** |
| **generate_tree_data.py doesn't handle split tables** | MEDIUM | UNION `genome_features` + `pan_genome_features` | **P1** |
| **Consistency scores must be computed** | HIGH | `rast_consistency` is NULL in DB, script must calculate | **P0** |

### 5.2 UI Track Gaps (6 Placeholder Tracks)

| Track | Data Available | UI Status | Priority |
|-------|----------------|-----------|----------|
| Flux (rich media) | ✅ YES (new DB) | ❌ PLACEHOLDER | **P0** |
| Flux (minimal media) | ✅ YES (new DB) | ❌ PLACEHOLDER | **P0** |
| Rxn Class (rich) | ✅ YES (new DB) | ❌ PLACEHOLDER | **P0** |
| Rxn Class (minimal) | ✅ YES (new DB) | ❌ PLACEHOLDER | **P0** |
| # Phenotypes | ✅ YES (new DB) | ❌ PLACEHOLDER | **P1** |
| # Fitness Scores | ✅ YES (new DB) | ❌ PLACEHOLDER | **P1** |
| Neighborhood Conservation | ❌ NO | ❌ PLACEHOLDER | **P3** |

### 5.3 Visualization Feature Gaps (vs. BERDL Dashboards)

| Feature | Data Available | UI Status | Priority |
|---------|----------------|-----------|----------|
| KPI Summary Cards (top of page) | ✅ YES | ❌ NOT BUILT | **P1** |
| Gene Content Dendrogram | ✅ YES (tree_data.json) | ❌ NOT RENDERED | **P2** |
| Statistical Outlier Detection (z-scores) | ⚠️ NEED REF STATS | ❌ NOT BUILT | **P2** |
| Drill-down Cluster Heatmaps | ⚠️ NEED CLUSTER PA MATRIX | ❌ NOT BUILT | **P2** |
| Missing Core Genes View | ✅ YES | ❌ NOT BUILT | **P2** |
| KEGG Pathway Completeness | ⚠️ NEED PATHWAY MAPPING | ❌ NOT BUILT | **P3** |
| Global Gene Search (header) | ✅ YES | ⚠️ PER-TAB ONLY | **P1** |
| Phenotype Validation Histogram | ⚠️ NEED 477-GENOME DATA | ❌ NOT BUILT | **P3** |
| Gene Essentiality Matrix | ✅ YES (new DB) | ❌ NOT BUILT | **P2** |

### 5.4 Data Quality Gaps

| Issue | Count | Impact | Fix |
|-------|-------|--------|-----|
| IS_HYPO too narrow | 660+ genes | MEDIUM | Add multi-level annotation quality track |
| RAST/Bakta disagreement | 85% of genes | INFO | Expected, no fix needed |
| FUNC prefers RAST when hypo | Unknown | LOW | Prefer non-hypo annotation |
| Multi-cluster genes | 266 genes | LOW | Investigate root cause |
| PSORTb localization sparse | 81.3% missing | MEDIUM | **NEW DB HAS ONLY 18.7%** - data regressed |

---

## PART 6: BUILD PLAN (Prioritized by Impact)

### Phase 0: Critical Fixes (Week 1) 🔥

**Goal:** Fix broken Metabolic Map tab with correct organism data

#### Task 0.1: Switch to New DB Schema
**Files to modify:**
- `generate_genes_data.py` - Add UNION of `genome_features` + `pan_genome_features`
- `generate_reactions_data.py` - Rewrite to query `genome_reactions` table instead of TSV

**New fields to add (7):**
1. `REACTIONS` (index 29) - Semicolon-separated reaction IDs
2. `RICH_FLUX` (index 30) - Rich media flux
3. `RICH_CLASS` (index 31) - Rich media flux class (essential/variable/blocked)
4. `MIN_FLUX` (index 32) - Minimal media flux
5. `MIN_CLASS` (index 33) - Minimal media flux class
6. `PSORTB_NEW` (index 34) - Updated PSORTb localization
7. `ESSENTIALITY` (index 35) - Essentiality fraction (from gene_phenotypes)

**Outcome:** `genes_data.json` expands from 29 to 36 fields, reactions_data.json uses correct organism

#### Task 0.2: Update Metabolic Map Tab
**Files to modify:**
- `index.html:2652-2700` - Expand flux classes from 3 to 6 categories
- `index.html:2668-2700` - Update color scales

**New flux class categories:**
- Forward only, reverse only, essential forward, essential reverse, reversible, blocked

**Outcome:** Metabolic map shows correct ADP1 data, gene cross-links work

#### Task 0.3: Update Tests
**Files to modify:**
- `tests/viewer.spec.js:804-845` - Update expected reaction counts, genome ID

**Outcome:** All 71 tests pass with ADP1 data

---

### Phase 1: Fill Placeholder Tracks (Week 2) 📊

**Goal:** Activate 6 placeholder tracks with new data

#### Task 1.1: Add Flux Tracks
**Files to modify:**
- `config.json:58-65` - Remove `*` from track names, set enabled: true
- `index.html:927-950` - Update track descriptions

**Tracks to activate:**
- `flux_rich` (RICH_FLUX field)
- `flux_minimal` (MIN_FLUX field)
- `rxn_class_rich` (RICH_CLASS field)
- `rxn_class_min` (MIN_CLASS field)

**Outcome:** 4 new functional tracks, heatmap shows metabolic activity

#### Task 1.2: Add Phenotype/Fitness Tracks
**Prerequisites:** Create `generate_phenotypes_data.py` script

**New extraction script:**
```python
# Extract from gene_phenotypes table
# For each gene:
#   - Count distinct phenotypes (N_PHENOTYPES)
#   - Count records with fitness_match='yes' (N_FITNESS)
#   - Average essentiality_fraction (ESSENTIALITY)
```

**Output:** `phenotypes_data.json` with per-gene phenotype stats

**Files to modify:**
- `generate_phenotypes_data.py` (NEW) - Extract phenotype data
- `genes_data.json` - Add 2 fields: N_PHENOTYPES (index 36), N_FITNESS (index 37)
- `config.json:58-65` - Activate `n_phenotypes`, `n_fitness` tracks
- `index.html:927-950` - Update descriptions

**Outcome:** 6/6 placeholder tracks activated

---

### Phase 2: Dashboard Enhancements (Week 3) 🎨

**Goal:** Match BERDL dashboard quality

#### Task 2.1: KPI Summary Cards (Top of Page)
**Files to modify:**
- `index.html:504-513` - Move KPI bar from sidebar to page top
- `index.html:277-297` - Restyle as 8 cards instead of bar

**8 KPI Cards:**
1. Total Genes (4,617)
2. Core Genes (3,626)
3. Accessory Genes (587)
4. Unknown/Unique (404)
5. Avg Consistency (0.84)
6. Low Consistency (<0.5 count)
7. No Cluster (404)
8. Missing Core (compute: core clusters absent from user genome)

**Design:**
- 2 rows × 4 columns grid
- Card: white background, shadow, left cyan border (KBase theme)
- Icon + metric + label layout

**Outcome:** Professional dashboard header

#### Task 2.2: Global Gene Search (Header)
**Files to modify:**
- `index.html:514-521` - Move search box from sidebar to global header
- `index.html:1382-1414` - Unify search logic across tabs

**Features:**
- Search box in header (visible on all tabs)
- Filters all tabs simultaneously (highlights in Tracks, Cluster, Tree leaf labels)
- Shows result count: "X genes match 'query'"

**Outcome:** Consistent search UX across all tabs

#### Task 2.3: Missing Core Genes View
**Prerequisites:** Compute missing core genes

**New analysis view:**
- Name: "Missing Core Functions"
- Filters to: genes where cluster is core BUT gene not in user genome
- Sorts by: functional category (phage → COG → annotated → unannotated)
- Tracks shown: pan_category, conservation, avg_cons, is_hypo

**Files to modify:**
- `config.json:75-82` - Add new analysis view
- `index.html:1185-1232` - Add button

**Outcome:** Quickly identify conserved functions absent from user genome

#### Task 2.4: Gene Content Dendrogram
**Prerequisites:** Verify tree_data.json has correct data

**Current status:** Tree tab shows genome tree, NOT gene content dendrogram

**Fix:**
- Tree tab SHOULD show phylogenetic tree (if we had ANI/16S data)
- Gene content dendrogram = pangenome cluster presence/absence tree
- **DECISION NEEDED:** Do we want both trees, or is Tree tab already correct?

**If adding gene content tree:**
- Add new tab "Gene Content Tree" OR
- Add dropdown in Tree tab: "Tree Type: [Phylogenetic | Gene Content]"

**Outcome:** TBD based on stakeholder preference

---

### Phase 3: Advanced Features (Week 4+) 🚀

#### Task 3.1: Drill-down Cluster Heatmaps
**Prerequisites:** Extract cluster presence/absence matrix from DB

**Implementation:**
- Click functional category in genome ribbon → inline expansion
- Shows heatmap: genes (rows) × reference genomes (cols)
- Cell color: present (green) / absent (gray)
- Highlights user genome column

**Files to modify:**
- Create `generate_cluster_pa_matrix.py` - Extract presence/absence from `pan_genome_features`
- `index.html:1416-1482` - Expand gene detail panel to show cluster heatmap

**Outcome:** Understand which reference genomes share each gene

#### Task 3.2: Statistical Outlier Detection
**Prerequisites:** Compute z-scores for functional categories

**Implementation:**
- For each functional category (COG, KO, GO, etc.):
  - Count genes in user genome
  - Compare to reference genome distribution
  - Compute z-score: (user - mean) / std
  - Flag if |z| > 1.0 (outlier)
- Show box-whisker plot with user genome as diamond
- Yellow diamond = enriched, orange diamond = depleted

**Files to modify:**
- Create `generate_category_stats.py` - Compute z-scores
- Add new section to Tracks tab (below ribbon)
- Render D3.js box plots

**Outcome:** Identify unusual functional enrichment/depletion

#### Task 3.3: KEGG Pathway/Module Completeness
**Prerequisites:** Map KO terms to pathways/modules

**Implementation:**
- For each KEGG pathway:
  - Count KO terms present in user genome
  - Compare to expected KO count for pathway
  - Compute z-score vs. reference genomes
- Sort pathways by z-score (most complete → least)
- Show as table: Pathway Name | User KO Count | Expected | Z-score

**Files to modify:**
- `generate_genes_data.py` - Add pathway mapping (currently only modules)
- Add new section "KEGG Pathway Coverage" to Tracks tab

**Outcome:** Identify complete vs. incomplete pathways

#### Task 3.4: Gene Essentiality Matrix
**Prerequisites:** Phenotype data integrated (Phase 1.2)

**Implementation:**
- 2×2 cross-tab heatmap:
  - Rows: Essential in rich media? (Y/N)
  - Cols: Essential in minimal media? (Y/N)
- Cell: gene count
- Click cell → filter to those genes

**Files to modify:**
- Add new section "Gene Essentiality" to Tracks tab or Cluster tab
- Render as interactive heatmap

**Outcome:** Identify media-dependent vs. universally essential genes

#### Task 3.5: Growth Phenotype Summary Panel
**Prerequisites:** Create `generate_growth_data.py`

**Implementation:**
- Extract from `growth_phenotype_summary` table
- Show validation stats: TP/FP/TN/FN, accuracy
- Show phenotype count: positive/negative growth
- Compare to reference genome distribution

**Files to modify:**
- Create `generate_growth_data.py` - Extract growth stats
- Add new section "Growth Phenotype Validation" to Tree tab or global header

**Outcome:** Understand FBA model quality

---

## PART 7: IMMEDIATE ACTION ITEMS (This Week)

### Priority 0 (Critical - Fix Broken Features)

1. ✅ **Copy new DB to repo directory**
   ```bash
   cp "/Users/jplfaria/Downloads/berdl_tables (1).db" \
      /Users/jplfaria/repos/genome-heatmap-viewer/berdl_tables.db
   ```

2. ✅ **Update generate_genes_data.py**
   - Add UNION query for `genome_features` + `pan_genome_features`
   - Add 7 new fields: reactions, rich_flux, rich_class, min_flux, min_class, psortb_new, essentiality
   - Handle NULL consistency scores (compute manually like old script)
   - Test output: should get 3,235 genes (ADP1)

3. ✅ **Update generate_reactions_data.py**
   - Replace TSV parsing with DB query
   - Query `genome_reactions` WHERE `genome_id LIKE 'user_%'`
   - Expand flux classes from 3 to 6 categories
   - Build gene index from new `reactions` field in genes_data.json
   - Test output: should get ~1,100 reactions (ADP1 subset)

4. ✅ **Regenerate all JSON files**
   ```bash
   python3 generate_genes_data.py berdl_tables.db > genes_data.json
   python3 generate_tree_data.py berdl_tables.db > tree_data.json
   python3 generate_cluster_data.py berdl_tables.db > cluster_data.json
   python3 generate_reactions_data.py berdl_tables.db > reactions_data.json
   ```

5. ✅ **Update index.html Metabolic Map**
   - Expand `getReactionScale()` to handle 6 flux classes
   - Update legend labels
   - Test: click reaction should show correct ADP1 data

6. ✅ **Update Playwright tests**
   - Update expected genome ID: "user_Acinetobacter_baylyi_ADP1_RAST"
   - Update expected gene count: 3,235
   - Update expected reaction count: ~1,100
   - Run tests: `npx playwright test`

### Priority 1 (High - Enable Placeholder Tracks)

7. ✅ **Create generate_phenotypes_data.py**
   - Query `gene_phenotypes` table
   - Aggregate per gene: count phenotypes, count fitness records, avg essentiality
   - Output: phenotypes_data.json OR merge into genes_data.json as 3 new fields

8. ✅ **Update config.json**
   - Remove `*` from placeholder track names
   - Set enabled: true for 6 tracks
   - Update descriptions

9. ✅ **Update index.html**
   - Map new fields to track renderers
   - Test: toggle tracks, verify heatmap rendering

10. ✅ **Run full test suite**
    ```bash
    npx playwright test
    npm run validate  # If exists
    ```

### Priority 2 (Medium - Dashboard Enhancements)

11. ⏳ **Redesign KPI bar as cards**
    - Move from sidebar to page top
    - Add 1 new KPI: Missing Core count
    - Restyle as 2×4 grid

12. ⏳ **Add global search**
    - Move search box to header
    - Unify search logic across tabs

13. ⏳ **Add Missing Core analysis view**
    - Filter to core-absent genes
    - Sort by functional category

### Priority 3 (Low - Advanced Features)

14. ⏳ **Drill-down heatmaps** (if time permits)
15. ⏳ **Statistical outliers** (if time permits)
16. ⏳ **Pathway completeness** (if time permits)

---

## PART 8: RISK ASSESSMENT

### High Risk 🔴

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **E. coli data not available** | HIGH | HIGH | Chris said ADP1 first, E. coli later. Proceed with ADP1, switch organism when E. coli DB arrives. |
| **Consistency scores still NULL** | MEDIUM | HIGH | Compute manually in script like old DB. Use same cluster-based logic. |
| **Performance degradation (239K phenotype records)** | MEDIUM | MEDIUM | Aggregate in extraction script, don't load raw phenotype table into browser. |
| **UI breaks with 36 gene fields** | LOW | HIGH | Test thoroughly after adding fields. Canvas rendering should handle any field count. |

### Medium Risk 🟡

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Reference genome stats not in DB** | MEDIUM | MEDIUM | Z-score outlier detection requires ref stats. May need separate ref genome analysis. |
| **Pathway mapping not available** | MEDIUM | LOW | KEGG pathway completeness requires KO→pathway mapping. Use KEGG API or flat file. |
| **Multi-organism support needed** | LOW | MEDIUM | New DB has 14 genomes but only 1 is "user_". Plan for multi-organism dropdown. |
| **Flux class categorical colors** | LOW | LOW | 6 categories vs current 3. Need good color palette (colorblind-safe). |

### Low Risk 🟢

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Test failures after schema change** | HIGH | LOW | Expected. Update tests systematically. |
| **Legacy code dependencies** | LOW | LOW | Vanilla JS = no framework version conflicts. |
| **Browser compatibility** | LOW | LOW | Canvas/SVG widely supported. Test in Chrome/Firefox/Edge. |

---

## PART 9: SUCCESS CRITERIA

### Week 1 (Phase 0)
- ✅ All 71 Playwright tests pass with ADP1 data
- ✅ Metabolic Map tab shows correct organism (Acinetobacter)
- ✅ Gene cross-links from reactions to Tracks tab work
- ✅ genes_data.json has 36 fields (was 29)
- ✅ reactions_data.json uses DB instead of TSV

### Week 2 (Phase 1)
- ✅ 6/6 placeholder tracks activated (flux × 2, rxn class × 2, phenotypes, fitness)
- ✅ Heatmap renders all 30 active tracks (was 24)
- ✅ Phenotype data integrated (gene count, fitness count, essentiality)
- ✅ New analysis views use phenotype data

### Week 3 (Phase 2)
- ✅ KPI summary cards at page top (8 cards)
- ✅ Global gene search in header (works across all tabs)
- ✅ Missing Core analysis view shows conserved absent genes
- ✅ Dashboard matches BERDL reference quality

### Week 4+ (Phase 3)
- ✅ Drill-down cluster heatmaps (inline expansion)
- ✅ Statistical outlier detection (z-score flagging)
- ✅ KEGG pathway completeness view
- ✅ Gene essentiality matrix
- ✅ Growth phenotype validation panel

---

## PART 10: LONG-TERM VISION

### Multi-Organism Support
**Goal:** Single viewer can display any BERDL genome

**Requirements:**
- Organism dropdown in header
- Load organism-specific JSON files on demand
- URL parameter: `?organism=ecoli` or `?organism=adp1`
- GitHub Pages hosts multiple datasets

**Files needed per organism:**
- genes_data.json
- tree_data.json
- cluster_data.json
- reactions_data.json
- phenotypes_data.json
- config.json (organism-specific track names, etc.)

### KBase Integration
**Goal:** Deploy as KBase narrative cell

**Requirements (from meeting):**
- Create KBase module: `KBDatalakeDashboard`
- Input: BERDLTables workspace object (will have genome ID, DB path)
- Output: HTML report with embedded viewer
- Use KBUtilLib for workspace access
- Docker container with all dependencies

**Challenges:**
- Escher.js CDN may not work in KBase (offline environment)
- Need to bundle Escher library locally
- Large JSON files may exceed KBase report size limits
- May need to serve from KBase object store instead

### Reference Data Deployment (Boris)
**Goal:** Persistent reference genome data for pangenome comparisons

**Requirements:**
- 35 reference genomes × 8 organisms = 280 genomes
- Shared cluster definitions (cross-organism pangenomes)
- ANI matrix (genome distance)
- Pathway/module definitions (KEGG, MetaCyc, ModelSEED)

**Storage:**
- S3 bucket or KBase reference data store
- Versioned (BERDL_v1.0, BERDL_v1.1, etc.)
- Indexed for fast lookup

---

## APPENDICES

### A. File References

**Meeting transcript:** `/Users/jplfaria/Downloads/touchvase_dash.txt`
**New databases:** `/Users/jplfaria/Downloads/berdl_tables (1).db`, `berdl_tables (2).db`
**Reference dashboards:**
- https://genomics.lbl.gov/~aparkin/KBase/berdl_output_ADP1.html
- https://genomics.lbl.gov/~aparkin/KBase/berdl_output_ECOLI.html

**Detailed analyses:**
- `NEW_BERDL_DB_SCHEMA_ANALYSIS.md` - 600+ lines, exhaustive schema docs
- `PROJECT_STATUS.md` - Current state snapshot
- Agent outputs:
  - Web search researcher (Adam's dashboards): Agent ID ac3e809
  - Codebase analyzer (GHV capabilities): Agent ID a5f5871
  - Database profiler (new schema): Agent ID ad79e28

### B. Schema Comparison Tables

**See:** `NEW_BERDL_DB_SCHEMA_ANALYSIS.md` sections:
- Table-by-table comparison (old vs new)
- Field-by-field coverage analysis
- Sample data for all 13 tables
- Distribution statistics for numeric fields

### C. Test Coverage Map

**See:** `PROJECT_STATUS.md` section 8 (Testing Coverage):
- 9 test suites × 71 tests
- Line numbers for each test
- Scientific correctness validation criteria

---

## SUMMARY CHECKLIST

### Immediate (This Week)
- [ ] Copy new DB to repo
- [ ] Update generate_genes_data.py (add 7 fields)
- [ ] Update generate_reactions_data.py (query DB)
- [ ] Regenerate all JSON files
- [ ] Update Metabolic Map flux classes (3→6)
- [ ] Update tests for ADP1 data
- [ ] Create generate_phenotypes_data.py
- [ ] Activate 6 placeholder tracks
- [ ] Run full test suite

### Short-term (Next 2 Weeks)
- [ ] Redesign KPI bar as cards
- [ ] Add global gene search
- [ ] Add Missing Core analysis view
- [ ] Add Gene Essentiality matrix
- [ ] Add Growth Phenotype panel

### Long-term (Month+)
- [ ] Drill-down cluster heatmaps
- [ ] Statistical outlier detection
- [ ] KEGG pathway completeness
- [ ] Multi-organism support
- [ ] KBase module deployment
- [ ] Reference data deployment (Boris)

---

**Document Version:** 1.0
**Last Updated:** 2026-02-14
**Next Review:** After Phase 0 completion
