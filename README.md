# Genome Heatmap Viewer

**Interactive multi-track visualization for bacterial genome annotations, pangenome analysis, and metabolic modeling.**

<img src="https://img.shields.io/badge/Status-Active-success" alt="Active"> <img src="https://img.shields.io/badge/Genes-3%2C235-blue" alt="3,235 genes"> <img src="https://img.shields.io/badge/Tracks-28%20active-purple" alt="28 tracks"> <img src="https://img.shields.io/badge/Genomes-14-orange" alt="14 genomes">

---

## 🚀 Quick Start

### Try it Live
**GitHub Pages:** https://jplfaria.github.io/genome-heatmap-viewer/

### Run Locally
```bash
git clone https://github.com/jplfaria/genome-heatmap-viewer.git
cd genome-heatmap-viewer
python3 -m http.server 8000
# Open http://localhost:8000
```

---

## 📚 Documentation

### For Users
- **[User Guide](docs/USER_GUIDE.md)** - How to use the viewer
- **[Track Reference](docs/technical/TRACK_DOCUMENTATION.md)** - Complete track documentation (3,500+ lines)
- **Help Tab** - Built-in help in the viewer

### For Developers
- **[Technical Documentation](docs/technical/)** - Code references, formulas, database queries
- **[Project Status](docs/project/PROJECT_STATUS.md)** - Current status and roadmap
- **[Setup Guide](#development-setup)** - How to regenerate data files

### For Deployers
- **[KBase Deployment](docs/technical/DEPLOYMENT_SUMMARY.md)** - KBase integration guide
- **[Recent Fixes](docs/technical/FIXES_APPLIED.md)** - Latest bug fixes and improvements

---

## 📊 Features

### 🎨 Multi-Tab Interface

| Tab | Description | Key Features |
|-----|-------------|--------------|
| **Tracks** | Main heatmap visualization | 28 configurable tracks, 7 sort presets, 6 analysis views |
| **Distributions** | Statistical distributions | Histograms, pie charts, statistics for each track |
| **Tree** | Phylogenetic dendrogram | UPGMA tree, genome stats, Jaccard distances |
| **Cluster** | UMAP gene clustering | 2 embeddings, 10 color modes, interactive scatter plot |
| **Metabolic Map** | Pathway visualization | Escher maps, flux predictions, conservation coloring |
| **Help** | Documentation | Comprehensive built-in help |

### 📈 Data Coverage

- **3,235 genes** × 38 fields = ~175,000 data points
- **14 genomes** (user + 13 reference) in pangenome analysis
- **28 active tracks** covering annotations, pangenome, metabolism, phenotypes
- **1,279 reactions** in metabolic model

### 🔬 Track Categories

**Pangenome Analysis:**
- Core/Accessory classification
- Conservation across genomes
- Cluster size and membership

**Annotation Quality:**
- RAST, Bakta, KO, COG, Pfam, GO, EC terms
- Consistency scores across sources
- Annotation specificity

**Metabolic Modeling:**
- FBA flux predictions (rich/minimal media)
- Reaction classifications (essential/variable/blocked)
- Metabolic pathway coverage

**Phenotypes:**
- Gene essentiality scores
- Fitness associations
- Growth predictions

---

## 🗂️ Repository Structure

```
genome-heatmap-viewer/
├── index.html                  # Main viewer application
├── config.json                 # Track definitions and UI config
├── README.md                   # This file
│
├── data/                       # Generated data files
│   ├── genes_data.json         # Main gene data (3,235 × 38 fields, 585 KB)
│   ├── tree_data.json          # UPGMA phylogenetic tree
│   ├── cluster_data.json       # UMAP embeddings
│   ├── reactions_data.json     # Metabolic reactions
│   ├── metadata.json           # Organism metadata
│   ├── summary_stats.json      # Summary statistics
│   ├── ref_genomes_data.json   # Reference genome stats
│   └── metabolic_map_*.json    # Escher pathway maps
│
├── scripts/                    # Data generation scripts
│   ├── generate_genes_data.py  # Extract gene data from database
│   ├── generate_tree_data.py   # Compute UPGMA tree
│   ├── generate_cluster_data.py # Compute UMAP embeddings
│   ├── generate_reactions_data.py # Extract metabolic data
│   └── ... (11 scripts total)
│
├── docs/                       # Documentation
│   ├── technical/              # Technical documentation
│   │   ├── TRACK_DOCUMENTATION.md    # Complete track reference
│   │   ├── FIXES_APPLIED.md          # Recent bug fixes
│   │   └── DEPLOYMENT_SUMMARY.md     # Deployment guide
│   ├── project/                # Project documentation
│   │   ├── PROJECT_STATUS.md         # Status and roadmap
│   │   ├── ACTION_PLAN.md            # Development plan
│   │   └── CLAUDE.md                 # AI instructions
│   └── archived/               # Historical documents
│
├── tests/                      # Automated tests
│   └── viewer.spec.js          # Playwright tests (80+ tests)
│
├── sync-to-kbase.sh           # Sync to KBase module
└── berdl_tables.db            # Source database (not in git)
```

---

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- BERDL SQLite database (`berdl_tables.db`)
- Python packages: `numpy`, `scipy`, `umap-learn`

### Generate Data Files

```bash
# Install dependencies
pip install numpy scipy umap-learn

# Generate all data files
cd scripts/
python generate_metadata.py          # Organism metadata
python generate_genes_data.py        # Main gene data
python generate_tree_data.py         # Phylogenetic tree
python generate_cluster_data.py      # UMAP embeddings
python generate_reactions_data.py    # Metabolic reactions
python generate_summary_stats.py     # Summary stats
python extract_pan_genome_features.py # Reference genome stats
```

**Output:** Data files written to parent directory

### Validate Data

```bash
cd scripts/
python validate_genes_data.py        # Spot-check 10 random genes
python validate_data_integrity.py    # Comprehensive validation
```

**Expected:** All checks pass ✅

### Run Tests

```bash
# Install test dependencies
npm install

# Run Playwright tests
npm test
```

**Expected:** 80+ tests passing ✅

---

## 🔄 Syncing to KBase

The viewer is integrated into the **KBDatalakeDashboard** KBase module.

### Sync Latest Changes

```bash
./sync-to-kbase.sh
# Files copied to ~/repos/KBDatalakeDashboard/data/heatmap/
```

### Deploy to KBase

```bash
cd ~/repos/KBDatalakeDashboard

# Test locally
kb-sdk test

# Deploy to AppDev
kb-sdk deploy --appdev

# Test at https://ci.kbase.us
```

**Note:** KBase version loads data from Workspace objects, not static JSON files.

---

## 🎨 Color Schemes (Colorblind-Safe)

### Pangenome Categories
- 🟢 **Green** - Core genes (>95% genomes)
- 🟠 **Orange** - Accessory genes (5-95%)
- ⚪ **Gray** - Unknown (<5% or no cluster)

### Consistency Scores
- 🟠 **Orange** - High agreement (1.0)
- 🔵 **Blue** - Low agreement (0.0)
- ⚪ **Gray** - N/A (no cluster)

### Binary Tracks
- 🟣 **Purple** - Forward strand / Has feature
- 🟠 **Orange** - Reverse strand / Lacks feature

---

## 🔍 Key Data Fields

Each gene has 38 fields (see [TRACK_DOCUMENTATION.md](docs/technical/TRACK_DOCUMENTATION.md) for complete reference):

### Core Fields
- `ID`, `FID` (locus tag), `FUNC` (function), `LENGTH`, `START`, `STRAND`, `PROT_LEN`

### Pangenome
- `CONS_FRAC` (conservation 0-1), `PAN_CAT` (core/accessory/unknown), `CLUSTER_SIZE`

### Consistency Scores (-1=N/A, 0-1 scale)
- `AVG_CONS`, `RAST_CONS`, `KO_CONS`, `GO_CONS`, `EC_CONS`, `BAKTA_CONS`, `SPECIFICITY`

### Annotation Depth
- `N_KO`, `N_COG`, `N_PFAM`, `N_GO`, `N_EC`, `N_MODULES`, `HAS_NAME`, `IS_HYPO`

### Localization
- `LOC` (Cytoplasmic/Periplasmic/Membrane/Extracellular)

### Metabolic
- `REACTIONS`, `RICH_FLUX`, `MIN_FLUX`, `RICH_CLASS`, `MIN_CLASS`

### Phenotype
- `ESSENTIALITY`, `N_PHENOTYPES`

---

## 🧪 Testing

### Automated Tests (Playwright)
```bash
npm test  # Run 80+ tests
```

### Manual Test Workflows
1. **Characterization Targets** - Find core genes with unknown function
2. **Metabolic Gap Analysis** - Identify missing reactions
3. **Annotation Quality Review** - Compare RAST vs Bakta consistency

See [tests/viewer.spec.js](tests/viewer.spec.js) for test suite.

---

## ✅ Recent Updates

### 2026-02-16: Multi-Cluster Consistency Fix
**Critical Fix:** 266 genes (8.2%) now use MAX consistency across all pangenome clusters
- Previously used only FIRST cluster
- Affects: RAST, KO, GO, EC, Bakta consistency tracks
- [Details](docs/technical/FIXES_APPLIED.md)

### 2026-02-16: Comprehensive Documentation
**Added:** [TRACK_DOCUMENTATION.md](docs/technical/TRACK_DOCUMENTATION.md) (3,500+ lines)
- Complete technical reference for all 28 tracks
- Formulas, database queries, code references
- Biological interpretation and examples

---

## 🤝 Contributing

### Reporting Issues
Found a bug or have a suggestion? [Open an issue](https://github.com/jplfaria/genome-heatmap-viewer/issues)

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

---

## 📞 Support

- **KBase Support:** https://www.kbase.us/support
- **GitHub Issues:** https://github.com/jplfaria/genome-heatmap-viewer/issues
- **Documentation:** See [docs/](docs/) directory

---

## 👥 Credits

- **Christopher Henry** - Requirements, data pipeline
- **Jose Faria** - Development
- **Adam Arkin Lab** - Reference data, RB-TnSeq fitness data
- **Claude Sonnet 4.5** - Development assistance

---

## 📄 License

See KBase licensing terms.

---

## 🔗 Related Projects

- **KBase:** https://www.kbase.us
- **BERDL Dashboard:** https://genomics.lbl.gov/~aparkin/KBase/berdl_dashboard_output.html
- **ModelSEED:** https://modelseed.org
- **Escher:** https://escher.github.io
