# BERDL Database Schema Analysis & Gap Analysis

**Date:** 2026-02-14
**Database Files:** `berdl_tables (1).db` and `berdl_tables (2).db` (identical, MD5: 37717123ff6c409a7ed041e1d6703ff2)
**Size:** 132 MB each
**Organism:** Acinetobacter baylyi ADP1 (RAST annotation)
**Genome ID:** `user_Acinetobacter_baylyi_ADP1_RAST`
**Genes:** 3,235 genes in user genome

---

## Database Comparison

### Files are IDENTICAL
Both `berdl_tables (1).db` and `berdl_tables (2).db` have the same MD5 hash and contain the same data.

### Organism Change
- **Old implementation:** E. coli K-12 MG1655 (GCF_000005845.2), 4,617 genes, 36 genomes in pangenome
- **New database:** Acinetobacter baylyi ADP1, 3,235 genes, 14 genomes total (13 reference + 1 user)

---

## Complete Table Inventory (13 tables)

### 1. `genome` - Genome metadata
**Schema:**
```sql
CREATE TABLE "genome" (
  "id" VARCHAR(255) NOT NULL,
  "gtdb_taxonomy" VARCHAR(1000),
  "ncbi_taxonomy" VARCHAR(1000),
  "n_contigs" INTEGER,
  "n_features" INTEGER
)
```

**Row count:** 14 genomes

**Genome list:**
| genome_id | n_features |
|-----------|------------|
| GB_GCA_002694305.1 | 3,617 |
| RS_GCF_000046845.1 | 3,273 |
| RS_GCF_000302115.1 | 3,465 |
| RS_GCF_000368685.1 | 3,275 |
| RS_GCF_000621045.1 | 3,318 |
| RS_GCF_001485005.1 | 3,311 |
| RS_GCF_010577805.1 | 3,285 |
| RS_GCF_010577855.1 | 3,276 |
| RS_GCF_010577875.1 | 3,292 |
| RS_GCF_010577895.1 | 3,279 |
| RS_GCF_010577925.1 | 3,322 |
| RS_GCF_010577955.1 | 3,617 |
| RS_GCF_900465415.1 | 3,424 |
| **user_Acinetobacter_baylyi_ADP1_RAST** | **3,235** |

---

### 2. `genome_ani` - Average Nucleotide Identity
**Schema:**
```sql
CREATE TABLE "genome_ani" (
  "genome1" VARCHAR(255) NOT NULL,
  "genome2" VARCHAR(255) NOT NULL,
  "ani" FLOAT NOT NULL,
  "af1" FLOAT NOT NULL,
  "af2" FLOAT NOT NULL,
  "kind" VARCHAR(255) NOT NULL
)
```

**Row count:** 1

**Sample:**
```
genome1: user_Acinetobacter_baylyi_ADP1_RAST
genome2: RS_GCF_000368685.1
ani: 99.97
af1: 99.47
af2: 99.83
kind: kepangenomes
```

---

### 3. `genome_features` - Main gene features table (USER GENOME ONLY)
**Schema:**
```sql
CREATE TABLE "genome_features" (
  "id" INTEGER,
  "genome_id" VARCHAR(255) NOT NULL,
  "contig_id" VARCHAR(255) NOT NULL,
  "feature_id" VARCHAR(255) NOT NULL,
  "length" INTEGER NOT NULL,
  "start" INTEGER,
  "end" INTEGER,
  "strand" VARCHAR(1),
  "sequence" TEXT,
  "sequence_hash" VARCHAR(255),
  "bakta_function" VARCHAR(255),
  "rast_function" VARCHAR(255),
  "cog" VARCHAR(255),
  "ec" VARCHAR(255),
  "gene_names" VARCHAR(255),
  "go" VARCHAR(1000),
  "ko" VARCHAR(1000),
  "pfam" VARCHAR(1000),
  "so" VARCHAR(1000),
  "uniref_100" VARCHAR(255),
  "uniref_90" VARCHAR(255),
  "uniref_50" VARCHAR(255),
  "pangenome_cluster_id" VARCHAR(255),
  "pangenome_is_core" BOOLEAN,
  "psortb" VARCHAR(255),
  "reactions" TEXT,                       -- NEW: semicolon-separated reaction IDs
  "rich_media_flux" REAL,                 -- NEW: flux value in rich media
  "rich_media_class" VARCHAR(255),        -- NEW: essential/variable/blocked
  "minimal_media_flux" REAL,              -- NEW: flux value in minimal media
  "minimal_media_class" VARCHAR(255),     -- NEW: essential/variable/blocked
  "rast_consistency" REAL,                -- NEW: but all NULL (0 non-null values)
  "other_rast_annotations" TEXT           -- NEW: but all empty (0 non-empty values)
)
```

**Row count:** 3,235 (user genome only - NO reference genome genes)

**Field coverage for user genome:**
| Field | Non-null/Non-empty | Percentage | Notes |
|-------|-------------------|------------|-------|
| reactions | 866 | 26.8% | Semicolon-separated reaction IDs (e.g., "rxn05294") |
| rich_media_flux | 866 | 26.8% | Range: 0.0 to 119.3, avg: 2.20 |
| rich_media_class | 866 | 26.8% | essential (270), variable (405), blocked (191), NULL (2,369) |
| minimal_media_flux | 866 | 26.8% | Range: 0.0 to 13.25, avg: 0.37 |
| minimal_media_class | 866 | 26.8% | essential (302), variable (322), blocked (242), NULL (2,369) |
| psortb | 606 | 18.7% | Localization predictions |
| rast_consistency | 0 | 0% | All NULL - field exists but unpopulated |
| other_rast_annotations | 0 | 0% | All empty - field exists but unpopulated |

**CRITICAL DIFFERENCE vs old DB:**
- Old: `genome_features` contained ALL genes from ALL genomes
- New: `genome_features` contains ONLY user genome genes
- Reference genome genes are now in `pan_genome_features` table

---

### 4. `pan_genome_features` - Reference genome features (NO USER GENOME)
**Schema:**
```sql
CREATE TABLE "pan_genome_features" (
  "id" INTEGER,
  "genome_id" VARCHAR(255) NOT NULL,
  "contig_id" VARCHAR(255) NOT NULL,
  "feature_id" VARCHAR(255) NOT NULL,
  "length" INTEGER NOT NULL,
  "start" INTEGER,
  "end" INTEGER,
  "strand" VARCHAR(1),
  "sequence" TEXT,
  "sequence_hash" VARCHAR(255),
  "cluster_id" VARCHAR(255),              -- pangenome cluster ID
  "is_core" BOOLEAN,
  "bakta_function" VARCHAR(255),
  "rast_function" VARCHAR(255),
  "gene_names" VARCHAR(255),
  "cog" VARCHAR(1000),
  "ec" VARCHAR(1000),
  "ko" VARCHAR(1000),
  "pfam" VARCHAR(1000),
  "go" VARCHAR(1000),
  "so" VARCHAR(1000),
  "uniref_100" VARCHAR(255),
  "uniref_90" VARCHAR(255),
  "uniref_50" VARCHAR(255),
  "reaction" TEXT,                        -- NEW: reactions (different column name!)
  "rich_media_flux" REAL,                 -- NEW: flux data
  "rich_media_class" VARCHAR(255),
  "minimal_media_flux" REAL,
  "minimal_media_class" VARCHAR(255)
)
```

**Row count:** 43,754 (13 reference genomes, NO user genome)

**Distribution by genome:**
| Genome | Gene count |
|--------|-----------|
| GB_GCA_002694305.1 | 3,617 |
| RS_GCF_010577955.1 | 3,617 |
| RS_GCF_000302115.1 | 3,465 |
| RS_GCF_900465415.1 | 3,424 |
| RS_GCF_010577925.1 | 3,322 |
| ... (9 more genomes) | ... |

**CRITICAL:** User genome genes are NOT in this table (unlike old DB where `pan_genome_features` included user_genome)

**Field naming inconsistency:**
- `genome_features.reactions` (plural) vs `pan_genome_features.reaction` (singular)
- Both are semicolon-separated lists of reaction IDs

---

### 5. `genome_reactions` - Reaction-level flux/class data
**Schema:**
```sql
CREATE TABLE "genome_reactions" (
  "genome_id" TEXT,
  "reaction_id" TEXT,
  "genes" TEXT,                           -- Gene association (e.g., "gene1 or (gene2 and gene3)")
  "equation_names" TEXT,                  -- Human-readable equation
  "equation_ids" TEXT,                    -- Compound ID equation
  "directionality" TEXT,                  -- forward/reverse/reversible
  "upper_bound" INTEGER,
  "lower_bound" INTEGER,
  "gapfilling_status" TEXT,               -- none/rich/minimal
  "rich_media_flux" REAL,
  "rich_media_class" TEXT,                -- DIFFERENT VALUES than genome_features!
  "minimal_media_flux" REAL,
  "minimal_media_class" TEXT
)
```

**Row count:** 17,984 reactions across all genomes

**User genome:** Reactions present for `user_Acinetobacter_baylyi_ADP1_RAST`

**Flux class values (DIFFERENT from genome_features!):**
| rich_media_class | Count | Avg flux |
|------------------|-------|----------|
| blocked | 7,196 | 0.0 |
| forward_only | 3,797 | 0.93 |
| essential_forward | 2,549 | 0.36 |
| reversible | 2,400 | 0.75 |
| reverse_only | 1,117 | -1.80 |
| essential_reverse | 925 | -0.78 |

**Gapfilling status:**
- none: 16,606 (92.3%)
- rich: 811 (4.5%)
- minimal: 567 (3.2%)

**Gene association examples:**
```
genes: "ACIAD_RS12875 or (ACIAD_RS13845 or ACIAD_RS11005)"
genes: "ACIAD_RS15910"
```

**CRITICAL:** This table has MORE DETAILED flux classes (6 categories) than genome_features (3 categories)

---

### 6. `gene_reaction_data` - Gene-to-reaction mapping with flux
**Schema:**
```sql
CREATE TABLE "gene_reaction_data" (
  "genome_id" VARCHAR(255) NOT NULL,
  "gene_id" VARCHAR(255) NOT NULL,
  "reaction" TEXT,                        -- Semicolon-separated reaction IDs
  "rich_media_flux" REAL,
  "rich_media_class" VARCHAR(255),
  "minimal_media_flux" REAL,
  "minimal_media_class" VARCHAR(255)
)
```

**Row count:** 12,311 gene-reaction associations across all genomes

**Distribution:**
| Genome | Gene-reaction records |
|--------|----------------------|
| GB_GCA_002694305.1 | 897 |
| RS_GCF_000046845.1 | 872 |
| RS_GCF_000302115.1 | 892 |
| RS_GCF_000368685.1 | 873 |
| RS_GCF_000621045.1 | 879 |

**Sample:**
```
genome_id: RS_GCF_010577925.1
gene_id: NZ_MPVY01000001.1_41
reaction: rxn02200;rxn02201;rxn02503
rich_media_flux: 0.00811
rich_media_class: variable
```

**Use case:** Links genes to reactions, with gene-level flux aggregated across all reactions

---

### 7. `gene_phenotypes` - Gene-phenotype associations with fitness data
**Schema:**
```sql
CREATE TABLE "gene_phenotypes" (
  "genome_id" TEXT,
  "gene_id" TEXT,
  "phenotype_id" TEXT,                    -- Compound ID (e.g., cpd00020)
  "phenotype_name" TEXT,                  -- Compound name (e.g., "Pyruvic Acid")
  "association_sources" TEXT,             -- "model_prediction"
  "model_pred_reactions" TEXT,            -- Semicolon-separated reactions
  "model_pred_max_flux" REAL,
  "fitness_match" TEXT,                   -- has_score/no_fitness_data_for_phenotype/no_fitness_ortholog/no_score_for_gene_phenotype
  "fitness_max" REAL,
  "fitness_min" REAL,
  "fitness_avg" REAL,
  "fitness_count" REAL,
  "essentiality_fraction" REAL            -- 0.0-1.0, fraction of conditions where gene is essential
)
```

**Row count:** 239,584 gene-phenotype associations across all genomes

**User genome coverage:**
- **Unique genes:** 2,297 out of 3,235 (71%)
- **Total phenotype records:** 169,085
- **Has fitness data:** 101,853 (60.2%)

**Fitness match distribution:**
| fitness_match | Count | % of total |
|---------------|-------|-----------|
| has_score | 101,853 | 42.5% |
| no_fitness_data_for_phenotype | 73,887 | 30.8% |
| no_fitness_ortholog | 51,193 | 21.4% |
| no_score_for_gene_phenotype | 12,651 | 5.3% |

**Essentiality fraction stats:**
- Non-null: 146,197 (61%)
- Range: 0.0 to 1.0
- Average: 0.022 (2.2% essentiality rate)

**Sample record:**
```
genome_id: user_Acinetobacter_baylyi_ADP1_RAST
gene_id: ACIAD_RS08130
phenotype_id: cpd00020
phenotype_name: Pyruvic Acid
association_sources: model_prediction
model_pred_reactions: rxn00423
model_pred_max_flux: 0.0064
fitness_match: has_score
fitness_max: 0.1328
fitness_min: -0.4522
fitness_avg: -0.1746
fitness_count: 11.0
essentiality_fraction: 0.0769
```

**Use case:** For each gene-phenotype pair, provides:
1. Model predictions (which reactions link gene to phenotype)
2. Experimental fitness data (if available)
3. Essentiality fraction across multiple conditions

---

### 8. `growth_phenotype_summary` - Per-genome growth phenotype stats
**Schema:**
```sql
CREATE TABLE "growth_phenotype_summary" (
  "genome_id" TEXT,
  "taxonomy" REAL,                        -- Empty/NULL
  "false_positives" INTEGER,
  "false_negatives" INTEGER,
  "true_positives" INTEGER,
  "true_negatives" INTEGER,
  "accuracy" REAL,
  "positive_growth" INTEGER,              -- Number of positive growth phenotypes
  "negative_growth" INTEGER,              -- Number of negative growth phenotypes
  "avg_positive_growth_gaps" INTEGER,     -- Average gaps for positive growth
  "avg_negative_growth_gaps" REAL,        -- Average gaps for negative growth
  "closest_user_genomes" REAL,            -- Empty/NULL
  "source" TEXT                           -- "pangenome" or "user"
)
```

**Row count:** 573 records

**User genome record:**
```
genome_id: user_Acinetobacter_baylyi_ADP1_RAST
false_positives: 0
false_negatives: 0
true_positives: 0
true_negatives: 0
accuracy: 0.0
positive_growth: 19
negative_growth: 193
avg_positive_growth_gaps: 0
avg_negative_growth_gaps: 3.45
source: user
```

**Interpretation:**
- 19 compounds where user genome can grow
- 193 compounds where user genome cannot grow
- Average of 3.45 gapfilled reactions needed for negative growth conditions

---

### 9. `growth_phenotypes_detailed` - Per-phenotype growth simulation results
**Schema:**
```sql
CREATE TABLE "growth_phenotypes_detailed" (
  "genome_id" TEXT,
  "phenotype_id" TEXT,                    -- Compound ID
  "phenotype_name" TEXT,
  "class" TEXT,                           -- "P" (positive) or "N" (negative)
  "simulated_objective" REAL,             -- FBA objective value
  "observed_objective" INTEGER,           -- Experimental result (0/1)
  "gap_count" INTEGER,                    -- Number of reactions gapfilled
  "gapfilled_reactions" TEXT,             -- Semicolon-separated reaction IDs
  "reaction_count" INTEGER,               -- Total reactions active in simulation
  "transports_added" TEXT,
  "closest_experimental_data" TEXT,
  "source" TEXT                           -- "pangenome"
)
```

**Row count:** 121,519 phenotype simulations across all genomes

**User genome:**
- Total records: 212
- Positive growth (P): 19
- Negative growth (N): 193
- Average gap count: 3.14

**Sample:**
```
genome_id: RS_GCF_000368685.1
phenotype_id: cpd00020
phenotype_name: Pyruvic Acid
class: P
simulated_objective: 4.26
observed_objective: 0
gap_count: 0
gapfilled_reactions: (empty)
reaction_count: 393
source: pangenome
```

**Use case:** Detailed results for each growth phenotype test:
- Which compounds support growth (class P vs N)
- How many reactions needed to be gapfilled to enable growth
- FBA objective value (growth rate)

---

### 10. `missing_functions` - Gapfilling analysis across conditions
**Schema:**
```sql
CREATE TABLE "missing_functions" (
  "Reaction" TEXT,
  "RAST_function" TEXT,
  "RichGapfill" INTEGER,                  -- Count of genomes needing this for rich media
  "MinimalGapfill" INTEGER,               -- Count for minimal media
  "PhenotypeGapfill" INTEGER,             -- Count for phenotype tests
  "ModuleGapfill" INTEGER,                -- Count for KEGG modules
  "Pangenome" INTEGER                     -- Count across pangenome
)
```

**Row count:** 243 reactions frequently needing gapfilling

**Sample:**
```
Reaction: rxn05469
RAST_function: Pyruvate [e0] + H+ [e0] <=> Pyruvate [c0] + H+ [c0]
RichGapfill: 0
MinimalGapfill: 1
PhenotypeGapfill: 0
ModuleGapfill: 0
Pangenome: 0
```

**Use case:** Identifies commonly missing reactions across the pangenome, highlighting potential annotation gaps or evolutionary losses

---

### 11. `ontology_terms` - Ontology term definitions
**Schema:**
```sql
CREATE TABLE "ontology_terms" (
  "ontology_prefix" TEXT,
  "identifier" TEXT,
  "label" TEXT,
  "definition" TEXT,
  "ec" TEXT
)
```

**Row count:** 11,539 terms

**Distribution by ontology:**
| ontology_prefix | Count |
|----------------|-------|
| seed.role | 2,256 |
| PFAM | 1,937 |
| SO | 1,889 |
| KEGG | 1,790 |
| GO | 1,423 |
| seed.reaction | 990 |
| EC | 909 |
| COG | 345 |

**Sample:**
```
ontology_prefix: GO
identifier: GO:0000015
label: phosphopyruvate hydratase complex
definition: A multimeric enzyme complex which catalyzes...
```

---

### 12. `ontology_definitions` - Ontology source definitions
**Schema:**
```sql
CREATE TABLE "ontology_definitions" (
  "ontology_prefix" TEXT,
  "definition" TEXT
)
```

**Row count:** 8 ontology sources

---

### 13. `ontology_relationships` - Ontology term relationships
**Schema:**
```sql
CREATE TABLE "ontology_relationships" (
  "subject" TEXT,
  "predicate" TEXT,
  "object" TEXT
)
```

**Row count:** 4,728 relationships

**Sample:**
```
subject: GO:0000015
predicate: is_a
object: GO:1902494
```

**Use case:** Ontology hierarchy for GO terms (parent-child relationships)

---

## NEW FIELDS vs Current Implementation

### Fields in NEW DB but NOT currently extracted:

#### From `genome_features` (user genome):
1. **reactions** (TEXT) - Semicolon-separated reaction IDs
   - Coverage: 866/3,235 genes (26.8%)
   - Example: "rxn05294" or "rxn00132;rxn00363;rxn00708"

2. **rich_media_flux** (REAL) - Flux value in rich media FBA
   - Coverage: 866/3,235 genes (26.8%)
   - Range: 0.0 to 119.3, avg: 2.20
   - **Visualization potential:** Heatmap track showing metabolic activity

3. **rich_media_class** (VARCHAR) - Flux classification
   - Coverage: 866/3,235 genes (26.8%)
   - Values: essential (270), variable (405), blocked (191)
   - **Visualization potential:** Categorical track, color-coded

4. **minimal_media_flux** (REAL) - Flux value in minimal media FBA
   - Coverage: 866/3,235 genes (26.8%)
   - Range: 0.0 to 13.25, avg: 0.37
   - **Visualization potential:** Heatmap track, compare vs rich media

5. **minimal_media_class** (VARCHAR) - Flux classification
   - Coverage: 866/3,235 genes (26.8%)
   - Values: essential (302), variable (322), blocked (242)
   - **Visualization potential:** Categorical track

6. **psortb** (VARCHAR) - Localization predictions
   - Coverage: 606/3,235 genes (18.7%)
   - **BETTER than current implementation:** Current uses generic "localization" field
   - **Visualization potential:** Replace existing localization track with PSORTb predictions

7. **rast_consistency** (REAL) - RAST consistency score
   - Coverage: 0/3,235 (0%) - **FIELD EXISTS BUT UNPOPULATED**
   - **Current implementation:** Computes this during extraction
   - **Action needed:** Continue computing this in extraction script

8. **other_rast_annotations** (TEXT) - Alternative RAST annotations
   - Coverage: 0/3,235 (0%) - **FIELD EXISTS BUT UNPOPULATED**
   - **Action needed:** Ignore this field

#### From `genome_reactions`:
9. **equation_names** (TEXT) - Human-readable reaction equation
10. **equation_ids** (TEXT) - ModelSEED compound ID equation
11. **directionality** (TEXT) - forward/reverse/reversible
12. **upper_bound** (INTEGER) - Flux upper bound
13. **lower_bound** (INTEGER) - Flux lower bound
14. **gapfilling_status** (TEXT) - none/rich/minimal
15. **genes** (TEXT) - Gene association logic (e.g., "gene1 or (gene2 and gene3)")
16. **rich_media_class** (detailed) - 6 categories instead of 3:
    - forward_only, reverse_only, essential_forward, essential_reverse, reversible, blocked
17. **minimal_media_class** (detailed) - Same 6 categories

#### From `gene_reaction_data`:
18. **Gene-level flux aggregation** - Already in genome_features, but this table shows multi-reaction genes

#### From `gene_phenotypes`:
19. **phenotype_id** (TEXT) - Compound ID for growth phenotype
20. **phenotype_name** (TEXT) - Compound name
21. **association_sources** (TEXT) - How gene-phenotype link was determined
22. **model_pred_reactions** (TEXT) - Reactions linking gene to phenotype
23. **model_pred_max_flux** (REAL) - Maximum flux through these reactions
24. **fitness_match** (TEXT) - Whether experimental fitness data exists
25. **fitness_max** (REAL) - Maximum fitness score
26. **fitness_min** (REAL) - Minimum fitness score
27. **fitness_avg** (REAL) - Average fitness score
28. **fitness_count** (REAL) - Number of fitness experiments
29. **essentiality_fraction** (REAL) - Fraction of conditions where gene is essential
   - **Coverage for user genome:** 2,297/3,235 genes (71%) have phenotype data
   - **Visualization potential:**
     - Track: "# Phenotypes" (count of phenotypes per gene)
     - Track: "Avg Fitness Score" (fitness_avg)
     - Track: "Essentiality Fraction" (0.0-1.0 heatmap)

#### From `growth_phenotype_summary`:
30. **positive_growth** (INTEGER) - Number of positive growth phenotypes
31. **negative_growth** (INTEGER) - Number of negative growth phenotypes
32. **avg_positive_growth_gaps** (INTEGER) - Average gapfilling for positive growth
33. **avg_negative_growth_gaps** (REAL) - Average gapfilling for negative growth
   - **Visualization potential:** Genome-level stats for Tree tab

#### From `growth_phenotypes_detailed`:
34. **Per-phenotype growth simulation results** - Not gene-level, but useful for metabolic map context

---

## Data Pipeline Gap Analysis

### Scripts that need updating:

#### 1. `generate_genes_data.py` - MAJOR UPDATES NEEDED
**Current:** Extracts 29 fields per gene from old DB schema
**New fields to add:**
- reactions (semicolon-separated)
- rich_media_flux
- rich_media_class
- minimal_media_flux
- minimal_media_class
- psortb (replace current localization field)
- Number of phenotypes (from gene_phenotypes join)
- Average fitness score (from gene_phenotypes)
- Essentiality fraction (from gene_phenotypes)

**Schema change to handle:**
- User genome genes in `genome_features` (old: all genomes in this table)
- Reference genes in `pan_genome_features` (old: reference genes here too)
- Need to JOIN user genome genes with pan_genome_features for consistency calculations

**Output:** Expand from 29 fields to ~38 fields per gene

#### 2. `generate_reactions_data.py` - REPLACE TSV INPUT WITH DB
**Current:** Reads from `genome_reactions.tsv` (temporary file)
**New:** Read from `genome_reactions` table in SQLite DB
**New fields available:**
- equation_names (human-readable)
- equation_ids (compound IDs)
- directionality
- upper_bound, lower_bound
- gapfilling_status
- genes (gene association logic)
- More detailed flux classes (6 categories instead of 3)

**Action:** Rewrite script to query DB instead of parsing TSV

#### 3. `generate_tree_data.py` - SCHEMA CHANGES
**Current:** Computes UPGMA tree from `pan_genome_features` with Jaccard distance
**New:** `pan_genome_features` no longer includes user genome
**Action:**
- JOIN `genome_features` (user genome) with `pan_genome_features` (reference genomes)
- Use `cluster_id` in pan_genome_features vs `pangenome_cluster_id` in genome_features
- Add growth phenotype stats to tree (from growth_phenotype_summary)

#### 4. `generate_cluster_data.py` - SCHEMA CHANGES
**Current:** Computes UMAP embeddings from genes_data.json
**New:** Could incorporate phenotype data into embeddings
**Action:** Minimal changes, but could add phenotype-based embedding mode

---

## Mapping to Meeting Transcript Visualizations

From the Slack meeting transcript, Chris mentioned these visualizations:

### 1. "Gene heatmap colored by flux"
**Data source:** `genome_features.rich_media_flux` or `minimal_media_flux`
**Current status:** Placeholder track exists, data now available
**Action:** Populate flux tracks in genes_data.json

### 2. "Gene heatmap colored by flux class"
**Data source:** `genome_features.rich_media_class` or `minimal_media_class`
**Current status:** Placeholder track exists, data now available
**Values:** essential, variable, blocked
**Action:** Populate flux class tracks

### 3. "Reaction heatmap colored by flux"
**Data source:** `genome_reactions.rich_media_flux`
**Current status:** Implemented in Metabolic Map tab
**Action:** Update to use DB instead of TSV

### 4. "Reaction heatmap colored by flux class"
**Data source:** `genome_reactions.rich_media_class` (6 categories)
**Current status:** Implemented in Metabolic Map tab (but only 3 categories)
**Action:** Expand to 6 categories: forward_only, reverse_only, essential_forward, essential_reverse, reversible, blocked

### 5. "Phenotype data"
**Data source:** `gene_phenotypes` table
**Tracks to add:**
- Number of phenotypes per gene
- Average fitness score
- Essentiality fraction
**Current status:** Not implemented
**Action:** Add 3 new tracks to genes_data.json

### 6. "Growth phenotype summary"
**Data source:** `growth_phenotype_summary` and `growth_phenotypes_detailed`
**Visualization:** Stats panel or detail view
**Current status:** Not implemented
**Action:** Add genome-level growth stats to Tree tab or new summary panel

---

## Critical Schema Differences to Handle

### 1. User genome vs reference genomes in DIFFERENT tables
**Old DB:**
- All genes in `genome_features`
- Subset also in `pan_genome_features` with cluster assignments

**New DB:**
- User genome genes ONLY in `genome_features`
- Reference genes ONLY in `pan_genome_features`
- **Column name inconsistency:** `pangenome_cluster_id` vs `cluster_id`
- **Column name inconsistency:** `reactions` (plural) vs `reaction` (singular)

**Action required:**
- Scripts must UNION data from both tables
- Handle column name differences in queries

### 2. Consistency scores not pre-computed
**Old DB:** Consistency scores computed by pipeline
**New DB:** `rast_consistency` field exists but is ALL NULL
**Action:** Continue computing consistency scores in Python extraction script (as currently done)

### 3. Flux class granularity mismatch
**genome_features:** 3 categories (essential, variable, blocked)
**genome_reactions:** 6 categories (forward_only, reverse_only, essential_forward, essential_reverse, reversible, blocked)

**Interpretation:**
- Gene-level flux is AGGREGATED across all reactions for that gene (lossy)
- Reaction-level flux preserves directionality information (more precise)

**Action:** Use reaction-level flux classes for Metabolic Map, gene-level for Tracks tab

### 4. Phenotype data is SPARSE but RICH
- 71% of genes have phenotype associations
- 60% of phenotype records have fitness data
- Average of 73 phenotypes per gene (for genes with phenotypes)
- **Action:** Gracefully handle genes with no phenotype data (display as N/A or gray)

---

## Recommended Next Steps

### Phase 1: Schema Migration (update extraction scripts)
1. Update `generate_genes_data.py` to:
   - Query both `genome_features` and `pan_genome_features`
   - Extract new flux fields (4 fields: 2 flux, 2 class)
   - Extract psortb localization
   - JOIN with `gene_phenotypes` to add: # phenotypes, avg fitness, essentiality fraction (3 fields)
   - **Total new fields:** 7 (bringing total from 29 to 36)

2. Update `generate_reactions_data.py` to:
   - Query `genome_reactions` table instead of TSV
   - Add equation_names, directionality, gapfilling_status
   - Expand flux_class categories from 3 to 6

3. Update `generate_tree_data.py` to:
   - Handle split between genome_features (user) and pan_genome_features (references)
   - Add growth phenotype summary stats per genome

### Phase 2: UI Updates (new tracks and visualizations)
4. Add 7 new tracks to Tracks tab:
   - Rich media flux (heatmap)
   - Rich media class (categorical: essential/variable/blocked)
   - Minimal media flux (heatmap)
   - Minimal media class (categorical)
   - Number of phenotypes (numeric)
   - Average fitness score (heatmap)
   - Essentiality fraction (heatmap 0.0-1.0)

5. Update Metabolic Map tab:
   - Expand flux class legend from 3 to 6 categories
   - Add reaction directionality indicators
   - Add gapfilling status indicators

6. Add growth phenotype summary panel (new feature):
   - Show positive/negative growth counts
   - Show gapfilling statistics
   - Per-genome comparison in Tree tab

### Phase 3: Testing and Validation
7. Update Playwright tests for new fields and tracks
8. Validate consistency score computation matches expected values
9. Cross-check flux values between gene-level and reaction-level aggregations
10. Verify phenotype data joins correctly (handle sparse data)

---

## Summary Statistics

### Database Size and Scope
- **Size:** 132 MB
- **Tables:** 13
- **Total rows:** ~612,000 across all tables
- **Organism:** Acinetobacter baylyi ADP1
- **Genes in user genome:** 3,235
- **Genomes in pangenome:** 14 (13 reference + 1 user)

### New Data Availability
- **Genes with flux data:** 866/3,235 (26.8%)
- **Genes with phenotype data:** 2,297/3,235 (71.0%)
- **Genes with fitness data:** 101,853 phenotype records (60.2% of phenotype data)
- **Growth phenotypes tested:** 212 compounds (19 positive, 193 negative)
- **Reactions in genome:** 17,984 total (user genome subset available)

### Data Completeness Issues
- **rast_consistency:** 0% populated (compute in script)
- **other_rast_annotations:** 0% populated (ignore)
- **psortb:** 18.7% coverage (better than nothing)
- **Flux data:** 26.8% coverage (genes with metabolic reactions only - expected)

---

## Files Comparison: Identical Databases

Both `berdl_tables (1).db` and `berdl_tables (2).db` are IDENTICAL:
- **MD5 hash:** 37717123ff6c409a7ed041e1d6703ff2
- **Size:** 132 MB each
- **All tables match exactly**

**Conclusion:** Use either file, they contain the same data. Likely duplicates from same upload.
