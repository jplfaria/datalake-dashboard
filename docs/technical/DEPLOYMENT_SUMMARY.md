# Deployment Summary - 2026-02-16

## ✅ Changes Deployed

### Critical Fix: Multi-Cluster Gene Consistency
- **266 genes** (8.2% of dataset) now use **MAX consistency** across all pangenome clusters
- Previously used FIRST cluster only - now matches conservation computation approach
- Affects all 6 consistency tracks: RAST, KO, GO, EC, Bakta, Average

### Code Improvements
- `generate_genes_data.py`: Loop through all cluster_ids, take MAX of consistency scores
- `generate_cluster_data.py`: Remove EC_MAP_CONS from UMAP (deprecated field)

### Documentation Added
- **TRACK_DOCUMENTATION.md** (3,500+ lines): Comprehensive technical reference for all 28 tracks, tree/cluster/metabolic map/distributions tabs
- **FIXES_APPLIED.md**: Detailed summary of issues found and fixes applied

### Data Files Regenerated
- `genes_data.json`: Updated with fixed consistency scores (avg_cons mean: 0.697)
- `cluster_data.json`: Cleaner 22-feature UMAP (removed deprecated field)

---

## 🚀 Deployment Locations

### 1. GitHub Repository (Main Source)
- **URL:** https://github.com/jplfaria/genome-heatmap-viewer
- **Commit:** c3b6f2a
- **Status:** ✅ Pushed
- **Files:** All source code, data files, documentation

### 2. GitHub Pages (Standalone Viewer)
- **URL:** https://jplfaria.github.io/genome-heatmap-viewer/
- **Deploy Source:** main branch (root directory)
- **Status:** ✅ Auto-deploying (builds in ~2-5 minutes)
- **Access:** Public, uses static JSON data files

### 3. KBase Module Repository
- **URL:** https://github.com/jplfaria/KBDatalakeDashboard
- **Commit:** 084fa55
- **Status:** ✅ Pushed
- **Files:** Viewer code only (data loaded dynamically from Workspace)
- **Location:** `data/heatmap/` directory

---

## 📊 Verification Checklist

### GitHub Pages (https://jplfaria.github.io/genome-heatmap-viewer/)
- [ ] Wait 2-5 minutes for GitHub Pages to rebuild
- [ ] Open URL, verify app loads
- [ ] Check Tracks tab → Enable "Function Consensus (avg)" track
- [ ] Sample a few multi-cluster genes, verify consistency scores look reasonable
- [ ] Check Cluster tab → Verify UMAP renders (22 features instead of 23)
- [ ] Open Help tab → Verify comprehensive documentation

### KBase Deployment (Next Step)
The viewer code is synced to KBDatalakeDashboard repo. To deploy to KBase:

```bash
cd ~/repos/KBDatalakeDashboard

# Build the module
kb-sdk test  # Optional: run tests first

# Register to AppDev
kb-sdk deploy --appdev

# Test at https://ci.kbase.us
# Search for "KBDatalakeDashboard2" or "Genome Datalake Dashboard"
```

**Note:** KBase version loads data from Workspace objects, NOT static JSON files. The multi-cluster consistency fix will only be visible after:
1. Re-running the BERDL data pipeline to regenerate genome objects
2. OR manually uploading updated genes_data.json as a new GenomeDataLakeTables object

---

## 🔍 Impact Assessment

### Genes Affected: 266 (8.2% of dataset)

These genes now have potentially higher consistency scores because we:
- Compute consistency for EACH pangenome cluster they belong to
- Take the MAX (best) consistency score across all clusters

**Example:** Gene belongs to clusters A and B
- **Before:** Used cluster A consistency only
- **After:** Computes both, uses MAX(A_cons, B_cons)

### Expected Changes
- **Avg consistency mean:** Was 0.697 (as of regeneration)
- **Tracks affected:** avg_cons, rast_cons, ko_cons, go_cons, ec_cons, bakta_cons
- **Visual change:** Some genes may shift from blue (low consistency) toward orange (high consistency)

### Data Integrity
- ✅ All field ranges remain within biological limits (0-1 for consistency)
- ✅ Pangenome distribution unchanged (91.4% core, 5.4% accessory, 3.2% unknown)
- ✅ No breaking changes to data structure (still 36 fields per gene)

---

## 📝 Commit Messages

### genome-heatmap-viewer (c3b6f2a)
```
Fix multi-cluster gene consistency and add comprehensive documentation

CRITICAL FIX: Multi-cluster gene consistency handling
- 266 genes belong to multiple pangenome clusters (8.2% of dataset)
- Consistency now uses MAX across ALL clusters (was using FIRST only)
- Matches conservation computation approach (both use MAX)
- Affects tracks: RAST, KO, GO, EC, Bakta consistency + average
```

### KBDatalakeDashboard (084fa55)
```
Update heatmap viewer to c3b6f2a with multi-cluster consistency fix

Synced from genome-heatmap-viewer commit c3b6f2a

Key changes:
- Fix multi-cluster gene consistency (266 genes now use MAX across clusters)
- Remove EC_MAP_CONS from UMAP embedding (deprecated field)
- Add comprehensive TRACK_DOCUMENTATION.md and FIXES_APPLIED.md
```

---

## 🎯 Next Actions

1. **Verify GitHub Pages deployment** (wait 2-5 minutes, then test)
2. **Optional: Deploy to KBase AppDev** (if you want to test the viewer in KBase environment)
3. **Update BERDL pipeline** (if you want the fix in production KBase objects)
4. **Share documentation** (TRACK_DOCUMENTATION.md is the authoritative technical reference)

---

## 📚 Documentation Files

All documentation is now in the repo:

- **README.md** - Getting started, quick reference
- **TRACK_DOCUMENTATION.md** - Comprehensive technical reference (all tracks, tabs, formulas)
- **FIXES_APPLIED.md** - Summary of issues and fixes
- **DEPLOYMENT_SUMMARY.md** - This file
- **PROJECT_STATUS.md** - Project status and data sources
- **ACTION_PLAN.md** - Development roadmap

---

## ✅ Deployment Complete!

All changes have been:
- ✅ Committed to genome-heatmap-viewer repo
- ✅ Pushed to GitHub (main branch)
- ✅ Synced to KBDatalakeDashboard repo
- ✅ Pushed to KBase repo (main branch)
- ✅ GitHub Pages auto-deploying

**GitHub Pages URL:** https://jplfaria.github.io/genome-heatmap-viewer/
**KBase AppDev:** Ready for deployment (run `kb-sdk deploy --appdev`)
