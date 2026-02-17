#!/usr/bin/env python3
"""Generate summary statistics for display in the viewer.

Extracts:
1. Missing functions (pangenome core reactions absent from user genome)
2. Growth phenotype summary (model predictions)
3. Genome comparison stats

Output: ../data/summary_stats.json
"""

import json
import sqlite3
import sys

DB_PATH = "/Users/jplfaria/repos/genome-heatmap-viewer/berdl_tables.db"
OUTPUT_PATH = "/Users/jplfaria/repos/genome-heatmap-viewer/../data/summary_stats.json"


def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    print("Extracting summary statistics from database...")

    # --- Step 1: Identify user genome ---
    user_genome_row = conn.execute(
        "SELECT id FROM genome WHERE id LIKE 'user_%' LIMIT 1"
    ).fetchone()
    if not user_genome_row:
        print("ERROR: No user genome found")
        sys.exit(1)

    user_genome_id = user_genome_row["id"]
    print(f"  User genome: {user_genome_id}")

    summary = {}

    # --- Step 2: Missing functions ---
    print("Extracting missing functions...")

    missing_pangenome = conn.execute(
        "SELECT COUNT(*) as count FROM missing_functions WHERE Pangenome = 1"
    ).fetchone()["count"]

    missing_gapfill = conn.execute(
        "SELECT COUNT(*) as count FROM missing_functions WHERE RichGapfill = 1 OR MinimalGapfill = 1"
    ).fetchone()["count"]

    # Get top missing functions
    missing_functions = []
    for row in conn.execute("""
        SELECT Reaction, RAST_function, Pangenome, RichGapfill, MinimalGapfill
        FROM missing_functions
        WHERE Pangenome = 1
        ORDER BY RAST_function
        LIMIT 20
    """):
        missing_functions.append({
            "reaction": row["Reaction"],
            "function": row["RAST_function"] or "Unknown function",
            "pangenome": bool(row["Pangenome"]),
            "rich_gapfill": bool(row["RichGapfill"]),
            "min_gapfill": bool(row["MinimalGapfill"]),
        })

    summary["missing_functions"] = {
        "pangenome_missing": missing_pangenome,
        "gapfilled": missing_gapfill,
        "top_missing": missing_functions,
    }

    print(f"  {missing_pangenome} core functions missing from user genome")
    print(f"  {missing_gapfill} functions added by gapfilling")

    # --- Step 3: Growth phenotype summary ---
    print("Extracting growth phenotype summary...")

    growth_row = conn.execute("""
        SELECT positive_growth, negative_growth, avg_positive_growth_gaps, avg_negative_growth_gaps
        FROM growth_phenotype_summary
        WHERE genome_id = ?
    """, (user_genome_id,)).fetchone()

    if growth_row:
        summary["growth_phenotypes"] = {
            "positive_growth": growth_row["positive_growth"],
            "negative_growth": growth_row["negative_growth"],
            "avg_positive_gaps": growth_row["avg_positive_growth_gaps"] or 0,
            "avg_negative_gaps": growth_row["avg_negative_growth_gaps"] or 0,
            "total_phenotypes": growth_row["positive_growth"] + growth_row["negative_growth"],
        }
        print(f"  {growth_row['positive_growth']} positive growth phenotypes")
        print(f"  {growth_row['negative_growth']} negative growth phenotypes")
    else:
        summary["growth_phenotypes"] = None
        print("  No growth phenotype data found")

    # --- Step 4: Reference genome stats ---
    print("Extracting reference genome comparison...")

    ref_count = conn.execute(
        "SELECT COUNT(*) as count FROM genome WHERE id NOT LIKE 'user_%'"
    ).fetchone()["count"]

    # ANI to closest genome
    closest_ani = conn.execute("""
        SELECT MAX(ani) as max_ani FROM genome_ani
        WHERE genome1 = ? OR genome2 = ?
    """, (user_genome_id, user_genome_id)).fetchone()

    summary["comparison"] = {
        "n_reference_genomes": ref_count,
        "closest_ani": round(closest_ani["max_ani"], 4) if closest_ani["max_ani"] else None,
    }

    print(f"  {ref_count} reference genomes")
    if closest_ani["max_ani"]:
        print(f"  Closest genome ANI: {closest_ani['max_ani']:.2f}%")

    conn.close()

    # --- Step 5: Write output ---
    print(f"\nWriting {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    size_kb = len(json.dumps(summary, indent=2)) / 1024
    print(f"  File size: {size_kb:.1f} KB")
    print("Done!")


if __name__ == "__main__":
    main()
