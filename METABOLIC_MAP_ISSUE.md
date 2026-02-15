# CRITICAL ISSUE: Metabolic Map Coverage

**Date**: 2026-02-14
**Status**: 🚨 **MAJOR DATA VISUALIZATION GAP**

---

## Problem Summary

The Escher metabolic maps display only **38.8% of user genome reactions** (496/1279). The remaining **783 reactions (61.2%)** have data but are not visualized on any map.

---

## Data Analysis

### User Genome Reactions (from database)
- **Total reactions**: 1,279
- **Active in rich media**: 759
- **Active in minimal media**: 696
- **Essential (rich)**: 248
- **Essential (minimal)**: 225
- **Blocked**: 520

### Escher Map Coverage
| Map | Reactions on Map | Our Data Overlap | Coverage |
|-----|-----------------|------------------|----------|
| **Full** (metabolic_map_full.json) | 759 (744 unique base IDs) | 496 | **38.8%** |
| **Core** (metabolic_map_core.json) | 201 | Not calculated | Lower |

### Gap Analysis
- **496 reactions** (38.8%): ✅ Can be visualized on Full map
- **783 reactions** (61.2%): ❌ NOT on any Escher map

---

## Why This Happens

### Reaction ID Format Mismatch
**Our data**: `rxn00225` (ModelSEED ID without compartment)
**Escher map**: `rxn00225_c0` (with compartment suffix `_c0`, `_e0`, etc.)

Solution: Already handled by stripping compartment suffix for matching.

### Map Contains Only Subset of Metabolism
The Escher maps are **manually curated pathway visualizations**, not comprehensive genome reaction lists.

**Full map** focuses on:
- Central carbon metabolism
- Energy metabolism
- Amino acid biosynthesis
- Core biosynthetic pathways

**Not included** on maps:
- Transport reactions (EX_* exchange reactions)
- Peripheral metabolism
- Species-specific pathways
- Gapfilled reactions
- Many secondary metabolic pathways

---

## Reactions Missing from Map

### Sample of Unmapped Reactions (with gene assignments)

```
rxn08806: ACIAD_RS10330 or ACIAD_RS08945 or ACIAD_... (Multi-gene)
rxn02483: ACIAD_RS10425 or ACIAD_RS07880 or ACIAD_... (Multi-gene)
rxn05301: ACIAD_RS06180 or ACIAD_RS13410 (2 genes)
rxn05450: ACIAD_RS14075 (1 gene)
rxn10260: ACIAD_RS01600 (1 gene)
EX_cpd01947: (Exchange reaction - no gene)
rxn01678: ACIAD_RS02530 (1 gene)
rxn09003: ACIAD_RS08790 (1 gene)
EX_cpd00034: (Exchange reaction - no gene)
rxn00295: ACIAD_RS00410 (1 gene)
```

**Note**: Many missing reactions have gene assignments, meaning they represent real metabolic capacity not shown on the map.

---

## Impact on Scientific Use

### What Users See
- 🟢 **Correctly colored**: 496 reactions based on conservation, flux, class
- 🔘 **Gray/no data**: Reactions on map but not in user genome (normal)
- ❌ **Not shown at all**: 783 reactions that user has but aren't on map

### What Users DON'T See
- 61.2% of genome's metabolic capacity
- Many transport reactions
- Peripheral pathways
- Organism-specific metabolism

### Is This Scientifically Valid?
**Partially**:
- ✅ The 496 reactions shown ARE correctly colored
- ✅ Central metabolism is well-represented
- ❌ Users don't know 783 reactions exist
- ❌ No way to visualize unmapped reactions

---

## Recommendations

### Short-term (Documentation)
1. ✅ Add stats panel showing coverage:
   ```
   "X of Y user reactions shown on map.
    Z reactions not mapped (see table below)"
   ```

2. ✅ List unmapped reactions in expandable section

3. ✅ Clarify map shows "core pathways" not "all reactions"

### Long-term (Feature Enhancement)
1. Create a **Reaction Coverage** table/list view showing ALL reactions
2. Allow filtering: "Show only reactions on map" vs "Show all"
3. Integrate with KEGG/MetaCyc pathway assignments
4. Generate custom Escher maps for species-specific pathways
5. Add heatmap view: reactions × genomes (like BERDL dashboard)

---

## Current User Experience

### Metabolic Map Tab
**What works**:
- Escher loads correctly
- 496 reactions colored by conservation/flux/class
- Clicking reactions shows gene details
- Map selection (Full vs Core) works

**What's misleading**:
- No indication that 783 reactions aren't shown
- Users might think map represents full metabolism
- Stats show "759 active in rich" but only 496 visualized

### Recommendation Display
Add to Metabolic Map sidebar:

```
┌─────────────────────────────┐
│ MAP COVERAGE                │
├─────────────────────────────┤
│ 496 of 1,279 reactions      │
│ shown on this map (38.8%)   │
│                             │
│ 783 reactions not mapped    │
│ (exchange, transport,       │
│  peripheral metabolism)     │
│                             │
│ [View unmapped reactions]   │
└─────────────────────────────┘
```

---

## Verification

### Test Performed
```python
# Counted unique base IDs (without compartment)
Map reactions: 744
Our reactions: 1,279
Overlap: 496 (38.8%)
```

### Spot Check
- ✅ `rxn00225` (acetate kinase): ON map, correctly shown
- ✅ `rxn00173` (phosphate acetyltransferase): ON map, correctly shown
- ❌ `rxn08806`: NOT on map, invisible to user
- ❌ `EX_cpd01947` (exchange): NOT on map, expected

---

## Conclusion

**The metabolic map visualization is PARTIALLY FUNCTIONAL**:
- ✅ Data for 496 reactions is scientifically accurate
- ✅ Colors/flux/conservation correct for displayed reactions
- ❌ 61.2% of metabolic capacity hidden from view
- ⚠️ Users not informed about incomplete coverage

**Action Required**:
1. Add coverage statistics to UI
2. Provide way to view unmapped reactions
3. Document limitation clearly
4. Consider adding comprehensive reaction table view

**Scientific Impact**: MEDIUM
- Central metabolism well-covered
- Peripheral/transport metabolism invisible
- Users need to know this limitation exists
