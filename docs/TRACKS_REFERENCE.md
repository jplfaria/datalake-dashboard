# Datalake Dashboard - Technical Reference

## Overview

The Datalake Dashboard is a standalone genomic analysis viewer that displays multi-track heatmaps, phylogenetic trees, UMAP cluster plots, metabolic maps, and distribution charts for a user genome compared against reference genomes in a pangenome database.

- **Architecture**: Pure vanilla HTML/CSS/JS, Canvas API, no frameworks
- **Data source**: GenomeDataLakeTables SQLite database (split-table schema)
- **Database-agnostic**: Reads any BERDL DB; organism info extracted dynamically
- **Rendering**: HTML5 Canvas for heatmap/cluster, SVG for distributions, Escher.js for metabolic maps

---

## Data Pipeline

### Script Execution Order

```
berdl_tables.db (SQLite)
    |
    ├── generate_metadata.py    → data/metadata.json
    ├── generate_genes_data.py  → data/genes_data.json (36 fields/gene)
    │   └── generate_phenotypes_data.py → appends 3 fields (39 total)
    ├── generate_tree_data.py   → data/tree_data.json
    ├── generate_cluster_data.py → data/cluster_data.json
    ├── generate_reactions_data.py → data/reactions_data.json
    └── generate_summary_stats.py → data/summary_stats.json
```

### KBase vs Standalone

In KBase, `data_extractor.py` computes all 39 fields inline (identical logic). The standalone scripts and KBase extractor produce identical output for the same input DB.

---

## Gene Array (39 Fields)

Each gene is stored as a flat JSON array with 39 elements. The viewer references fields by index via `config.json`.

| Index | Field | Type | Range | Source |
|-------|-------|------|-------|--------|
| 0 | ID | int | 0..n_genes-1 | Enumeration order from `user_feature ORDER BY start, feature_id` |
| 1 | FID | string | - | `user_feature.feature_id` |
| 2 | LENGTH | int | >0 | `user_feature.length` (nucleotides) |
| 3 | START | int | >=0 | `user_feature.start` (genomic coordinate) |
| 4 | STRAND | binary | {0, 1} | `1` if `strand == "+"`, else `0` |
| 5 | CONS_FRAC | float | [0, 1] | Conservation fraction: `n_genomes_in_cluster / n_ref_genomes`. Max across clusters for multi-cluster genes |
| 6 | PAN_CAT | int | {0, 1, 2} | Pangenome category: `0`=Unknown, `1`=Accessory, `2`=Core |
| 7 | FUNC | string | - | RAST annotation preferred over Bakta; falls back to "hypothetical protein" |
| 8 | N_KO | int | >=0 | Count of semicolon-separated KEGG terms in `ontology_KEGG` |
| 9 | N_COG | int | >=0 | Count of COG terms in `ontology_COG` |
| 10 | N_PFAM | int | >=0 | Count of Pfam terms in `ontology_PFAM` |
| 11 | N_GO | int | >=0 | Count of GO terms in `ontology_GO` |
| 12 | LOC | int | {0-5} | Primary subcellular localization (psortb): 0=Cytoplasmic, 1=CytoMembrane, 2=Periplasmic, 3=OuterMembrane, 4=Extracellular, 5=Unknown |
| 13 | RAST_CONS | float | [-1, 1] | RAST annotation consistency vs cluster. `-1`=N/A |
| 14 | KO_CONS | float | [-1, 1] | KEGG consistency vs cluster |
| 15 | GO_CONS | float | [-1, 1] | GO consistency vs cluster |
| 16 | EC_CONS | float | [-1, 1] | EC consistency vs cluster |
| 17 | AVG_CONS | float | [-1, 1] | Mean of all non-negative consistency scores |
| 18 | BAKTA_CONS | float | [-1, 1] | Bakta annotation consistency vs cluster |
| 19 | EC_AVG_CONS | float | [-1, 1] | Reserved/alias (currently equals EC_CONS) |
| 20 | SPECIFICITY | float | [-1, 1] | Annotation specificity heuristic. `-1`=no cluster |
| 21 | IS_HYPO | binary | {0, 1} | `1` if both RAST and Bakta call it hypothetical |
| 22 | HAS_NAME | binary | {0, 1} | `1` if `user_feature.aliases` is non-empty |
| 23 | N_EC | int | >=0 | Count of EC numbers in `ontology_EC` |
| 24 | AGREEMENT | int | {0-3} | RAST/Bakta agreement: 0=both hypo, 1=one hypo, 2=different, 3=identical |
| 25 | CLUSTER_SIZE | int | >=0 | Total features in pangenome cluster. Max across clusters for multi-cluster genes |
| 26 | N_MODULES | int | 0 | Placeholder (always 0, not yet computed) |
| 27 | EC_MAP_CONS | float | -1 | Placeholder (always -1, not yet computed) |
| 28 | PROT_LEN | int | >0 | Protein length in amino acids. Falls back to `length // 3` if no sequence |
| 29 | REACTIONS | string | - | Semicolon-joined sorted reaction IDs from `genome_reaction` |
| 30 | RICH_FLUX | float | - | Max flux value under rich media from FBA. `-1`=no data |
| 31 | RICH_CLASS | int | {-1,0,1,2} | Rich media flux class: -1=no data, 0=essential, 1=variable, 2=blocked |
| 32 | MIN_FLUX | float | - | Max flux value under minimal media. `-1`=no data |
| 33 | MIN_CLASS | int | {-1,0,1,2} | Minimal media flux class |
| 34 | PSORTB_NEW | int | {0-5} | Secondary localization (psortb) |
| 35 | ESSENTIALITY | float | [-1, 1] | Average essentiality score across reactions: essential=1.0, variable=0.5, blocked=0.0 |
| 36 | N_PHENOTYPES | int | >=0 | Count of distinct phenotype conditions for this gene |
| 37 | N_FITNESS | int | >=0 | Count of phenotypes with fitness scores |
| 38 | FITNESS_AVG | float | - | Average fitness score across scored phenotypes. `-1`=no data |

---

## Consistency Score Algorithm

Consistency measures how well a user gene's annotation agrees with other genes in the same pangenome cluster.

1. For each of the gene's pangenome cluster IDs (may be multiple, semicolon-separated):
2. Load all reference genes in that cluster from `pangenome_feature`
3. For each annotation source (RAST, KO, GO, EC, Bakta):
   - If user annotation is empty or no references exist: score = `-1` (N/A)
   - Otherwise: `score = exact_matches / total_reference_annotations`
4. For multi-cluster genes: take `max()` score across all clusters
5. AVG_CONS = mean of all non-negative per-source scores; `-1` if all are N/A

**Interpretation:**
- `0.0` = user annotation disagrees with all cluster members
- `1.0` = user annotation matches all cluster members
- `-1` = no data available (gene has no cluster or annotation source is empty)

**Script**: `generate_genes_data.py:128-135` (`compute_consistency()`), orchestrated at lines `326-371`

---

## Specificity Score Algorithm

Heuristic 0.0-1.0 score estimating how well-characterized a gene's function is.

**Base signals** (take max):
- EC number present: 0.9
- KO assignment: 0.7
- Gene name: 0.6
- COG: 0.5, GO: 0.5, Pfam: 0.4

**Adjustments:**
- Function text contains EC pattern: +0.1
- "hypothetical"/"uncharacterized"/"DUF" keywords: cap at 0.3
- "putative"/"predicted" keywords: cap at 0.5
- "conserved protein unknown": cap at 0.2
- Fully hypothetical (both RAST + Bakta): 0.0
- No pangenome cluster: -1

**Script**: `generate_genes_data.py:91-125`

---

## Tracks

### Track Types and Color Schemes

| Type | Color Scheme | Hex Values | Description |
|------|-------------|------------|-------------|
| `sequential` | Light→dark blue | `rgb(235,240,250)` → `rgb(45,100,180)` | Continuous gradient, min-max normalized |
| `consistency` | Blue→white→orange | `#2563eb` → `#ffffff` → `#f97316` | 0=disagreement, 0.5=partial, 1=agreement. Gray (#e5e7eb) for N/A. Colorblind-safe |
| `diverging` | Purple→white→teal | `#7c3aed` → `#ffffff` → `#0d9488` | Negative→neutral→positive. Gray for N/A. Colorblind-safe |
| `flux` | Blue→white→red | `#2563eb` → `#ffffff` → `#dc2626` | Reverse→zero→forward flux |
| `binary` | Purple/orange | `#6366f1` / `#f97316` | Two-state toggle |
| `categorical` | 6-color palette | `#9ca3af`, `#f59e0b`, `#22c55e`, `#3b82f6`, `#ec4899`, `#ef4444` | Gray, amber, green, blue, pink, red |

### Active Tracks (22)

| Track ID | Name | Field | Type | Default |
|----------|------|-------|------|---------|
| order | Gene Order | ID | sequential | on |
| strand | Gene Direction | STRAND | binary | on |
| conservation | Pangenome Conservation | CONS_FRAC | sequential | on |
| pan_category | Core/Accessory | PAN_CAT | categorical | on |
| avg_cons | Function Consensus (avg) | AVG_CONS | consistency | on |
| rast_cons | RAST Consistency | RAST_CONS | consistency | off |
| ko_cons | KO Consistency | KO_CONS | consistency | off |
| go_cons | GO Consistency | GO_CONS | consistency | off |
| ec_cons | EC Consistency | EC_CONS | consistency | off |
| bakta_cons | Bakta Consistency | BAKTA_CONS | consistency | off |
| specificity | Annotation Specificity | SPECIFICITY | consistency | off |
| n_ko | # KEGG Terms | N_KO | sequential | off |
| n_cog | # COG Terms | N_COG | sequential | off |
| n_pfam | # Pfam Terms | N_PFAM | sequential | off |
| n_go | # GO Terms | N_GO | sequential | off |
| localization | Subcellular Localization | LOC | categorical | off |
| has_name | Has Gene Name | HAS_NAME | binary | off |
| n_ec | # EC Numbers | N_EC | sequential | off |
| cluster_size | Cluster Size | CLUSTER_SIZE | sequential | off |
| prot_len | Protein Length | PROT_LEN | sequential | off |
| rich_flux | Flux (rich media) | RICH_FLUX | sequential | off |
| min_flux | Flux (minimal media) | MIN_FLUX | sequential | off |
| rich_class | Flux Class (rich) | RICH_CLASS | categorical | off |
| min_class | Flux Class (minimal) | MIN_CLASS | categorical | off |
| essentiality | Gene Essentiality | ESSENTIALITY | sequential | off |
| n_phenotypes | # Phenotypes | N_PHENOTYPES | sequential | off |
| n_fitness | # Fitness Scores | N_FITNESS | sequential | off |
| fitness_avg | Avg Fitness Score | FITNESS_AVG | diverging | off |

### Placeholder Tracks (not shown in UI)

| Track ID | Name | Notes |
|----------|------|-------|
| neighborhood | Neighborhood Conservation | Not yet computed |
| n_modules | KEGG Module Hits | Data always 0 (index 26) |
| ec_map_cons | EC Mapped Consistency | Data always -1 (index 27) |

---

## Analysis Views

Pre-configured track + sort combinations for common analysis workflows.

| View | Tracks Shown | Sort | Purpose |
|------|-------------|------|---------|
| Characterization Targets | pan_category, conservation, avg_cons, specificity | Pangenome Status | Find conserved genes with unknown function |
| Annotation Quality | avg_cons, specificity | Lowest Consistency | Spot annotation conflicts and gaps |
| Metabolic Landscape | n_ec, ec_cons, rich_class, essentiality | None | Map enzymatic and metabolic gene activity |
| Pangenome Structure | conservation, pan_category, cluster_size, strand | Conservation | Explore pangenome architecture and gene families |
| Knowledge Coverage | has_name, n_ko, n_go, n_pfam, n_ec | Annotation Depth | How well-characterized is each gene? |
| Consistency Comparison | rast_cons, ko_cons, bakta_cons, ec_cons, go_cons | Lowest Consistency | Compare consistency across annotation sources |

---

## Tree View

### Construction

- **Distance metric**: Jaccard distance on binary pangenome cluster presence/absence vectors
- **Input**: `(n_genomes x n_clusters)` binary matrix
- **Linkage**: UPGMA (unweighted pair group method with arithmetic mean) via `scipy.cluster.hierarchy.linkage(method="average")`
- **Leaf ordering**: `scipy.cluster.hierarchy.leaves_list(Z)`
- **Script**: `generate_tree_data.py`

### Per-Genome Metadata

| Field | Source |
|-------|--------|
| Taxonomy | `genome.taxonomy` |
| Feature count | `COUNT(*) FROM user_feature/pangenome_feature` |
| Contig count | `genome.n_contigs` |
| ANI to user | `ani` table (`MAX(ani)` where genome is involved) |
| CheckM completeness | `genome.checkm_completeness` |
| CheckM contamination | `genome.checkm_contamination` |
| Genome kind | `genome.kind` (clade, member, or user) |

### Stat Bars

| Stat | Color | Description |
|------|-------|-------------|
| Gene Count | #3b82f6 (blue) | Total genes in genome |
| Cluster Count | #ec4899 (pink) | Distinct pangenome clusters |
| Core % | #22c55e (green) | Percentage of core genes |
| Assembly Contigs | #f59e0b (amber) | Contig count |
| Missing Core | #ef4444 (red) | Core clusters absent from genome |
| KEGG Coverage | #ec4899 (pink) | % genes with KO assignments (user only) |
| Avg Consistency | #f97316 (orange) | Mean consistency score (user only) |
| Hypothetical % | #9ca3af (gray) | % hypothetical genes (user only) |
| EC Coverage | #22c55e (green) | % genes with EC numbers (user only) |
| Annotation Depth | #3b82f6 (blue) | Avg ontology terms per gene (user only) |

---

## Cluster View (UMAP)

Two separate UMAP embeddings computed via `generate_cluster_data.py`.

### Gene Features Embedding

- **Input**: 22 numeric features per gene (CONS_FRAC, consistency scores, specificity, ontology counts, cluster_size, prot_len, is_hypo, has_name, strand, pan_cat, agreement)
- **Preprocessing**: `-1` sentinel replaced with `0.0`, min-max normalization per column
- **UMAP params**: `n_neighbors=30, min_dist=0.1, metric="euclidean"`
- **Shows**: Functional similarity between genes

### Presence/Absence Embedding

- **Input**: `(n_genes x n_ref)` binary matrix of cluster-genome membership
- **UMAP params**: `n_neighbors=30, min_dist=0.1, metric="jaccard"`
- **Shows**: Co-occurrence patterns across reference genomes

### Color-by Options

pan_category, conservation, avg_cons, localization, n_ko, essentiality, cluster_size, specificity

---

## Metabolic Map

- **Engine**: Escher.js (embedded)
- **Maps**: Global Metabolism (`metabolic_map_full.json`) and Core Metabolism (`metabolic_map_core.json`)
- **Reaction coloring**: Based on conservation, flux, or essentiality from `reactions_data.json`
- **ID matching**: Reactions use `rxnXXXXX` format; Escher uses `rxnXXXXX_c0` (compartment suffix). The viewer generates all compartment variations (`_c0`, `_e0`, `_p0`, `_m0`, `_x0`) for matching.
- **Script**: `generate_reactions_data.py`

### Per-Reaction Fields

| Field | Description |
|-------|-------------|
| genes | Gene boolean expression string |
| equation | Named chemical equation |
| directionality | Forward, reverse, or reversible |
| gapfilling | Gapfilling status |
| conservation | Fraction of genomes with this reaction |
| flux_rich / flux_min | FBA flux values |
| class_rich / class_min | FBA flux classification |

---

## Summary Stats

Generated by `generate_summary_stats.py`.

### Missing Functions

- Gapfilled reaction count from `genome_reaction WHERE gapfilling_status IS NOT NULL`
- Top 20 gapfilled reactions with equation names

### Growth Phenotypes

- From `genome_phenotype`: positive/negative growth counts
- Average gapfilled reactions per negative phenotype
- Zero-gap and max-gap counts
- Top 10 most frequent gapfilled reaction sets

### Genome Comparison

- Reference genome count from `pangenome_feature`
- Closest ANI from `ani` table

---

## Colorblind Accessibility

All color palettes have been audited using Brettel/Machado CVD simulation matrices for Protanopia, Deuteranopia, and Tritanopia.

**Key design decisions:**
- Consistency uses blue-white-orange (avoids red-green)
- Diverging/fitness uses purple-white-teal (avoids red-green)
- Purple (#8b5cf6) replaced with pink (#ec4899) globally (blue and purple are indistinguishable under Deuteranopia)
- 0 FAIL results across all 3 CVD types
- 5 WARN results remain (reduced contrast in 6-color categorical palettes, inherent and unavoidable)

---

## Configuration (`config.json`)

All field indices, track definitions, sort presets, analysis views, and categories are defined in `config.json`. The viewer reads this at startup. No field indices are hardcoded in `index.html`.

Critical dynamic values (never hardcoded):
- `METADATA.n_ref_genomes` - reference genome count
- `genes.length` - gene count
- `METADATA.organism` - organism name
