#!/usr/bin/env python3
"""Generate ../data/reactions_data.json for the Genome Heatmap Viewer metabolic map tab.

NEW IN v2.0: Reads from genome_reactions table in BERDL SQLite database instead
of TSV file. Expands flux classes from 3 to 6 categories.

Produces per-reaction data for the user genome including conservation across
reference genomes, flux values, and 6-category flux classes.
"""

import json
import sqlite3
import sys

DB_PATH = "/Users/jplfaria/repos/genome-heatmap-viewer/berdl_tables.db"
GENES_DATA_PATH = "/Users/jplfaria/repos/genome-heatmap-viewer/../data/genes_data.json"
OUTPUT_PATH = "/Users/jplfaria/repos/genome-heatmap-viewer/../data/reactions_data.json"


def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # --- Identify user genome ---
    print("Identifying user genome...")
    user_genome_row = conn.execute(
        "SELECT id FROM genome WHERE id LIKE 'user_%' LIMIT 1"
    ).fetchone()
    if not user_genome_row:
        print("ERROR: No user genome found (genome.id LIKE 'user_%')")
        sys.exit(1)
    user_genome = user_genome_row["id"]
    print(f"  User genome: {user_genome}")

    # --- Count total genomes ---
    n_genomes = conn.execute(
        "SELECT COUNT(DISTINCT genome_id) FROM genome_reactions"
    ).fetchone()[0]
    print(f"  {n_genomes} genomes in comparison")

    # --- Build per-reaction data ---
    # First pass: count genomes per reaction (for conservation)
    print("Counting genomes per reaction...")
    rxn_genomes = {}
    for row in conn.execute("SELECT reaction_id, genome_id FROM genome_reactions"):
        rxn_id = row["reaction_id"]
        if rxn_id not in rxn_genomes:
            rxn_genomes[rxn_id] = set()
        rxn_genomes[rxn_id].add(row["genome_id"])

    # Second pass: extract user genome reaction data
    print(f"Loading reactions for {user_genome}...")
    reactions = {}
    for row in conn.execute("""
        SELECT reaction_id, genes, equation_names, equation_ids, directionality,
               gapfilling_status, rich_media_flux, rich_media_class,
               minimal_media_flux, minimal_media_class
        FROM genome_reactions
        WHERE genome_id = ?
    """, (user_genome,)):
        rxn_id = row["reaction_id"]
        n_with = len(rxn_genomes.get(rxn_id, set()))
        conservation = round(n_with / n_genomes, 4) if n_genomes > 0 else 0

        # Get flux values
        flux_rich = row["rich_media_flux"] if row["rich_media_flux"] is not None else 0
        flux_min = row["minimal_media_flux"] if row["minimal_media_flux"] is not None else 0

        # Get flux classes (NEW: keep as string, UI will handle 6 categories)
        class_rich = row["rich_media_class"] or "blocked"
        class_min = row["minimal_media_class"] or "blocked"

        reactions[rxn_id] = {
            "genes": row["genes"] or "",
            "equation": row["equation_names"] or "",
            "equation_ids": row["equation_ids"] or "",
            "directionality": row["directionality"] or "reversible",
            "gapfilling": row["gapfilling_status"] or "none",
            "conservation": conservation,
            "flux_rich": round(flux_rich, 6),
            "flux_min": round(flux_min, 6),
            "class_rich": class_rich,
            "class_min": class_min,
        }

    print(f"  {len(reactions)} reactions loaded")

    conn.close()

    # --- Build gene index from ../data/genes_data.json ---
    # Map locus tags (from reaction.genes field) to gene indices
    print("Building gene index...")
    gene_index = {}
    try:
        with open(GENES_DATA_PATH) as f:
            genes = json.load(f)

        # Build FID lookup: feature_id -> gene index
        fid_to_idx = {}
        for i, gene in enumerate(genes):
            fid = str(gene[1])  # FID is field index 1
            fid_to_idx[fid] = i

        # Extract all unique locus tags from reaction gene assignments
        import re
        all_locus_tags = set()
        for rxn in reactions.values():
            gene_str = rxn["genes"]
            if gene_str:
                # Extract tokens that look like locus tags (alphanumeric + underscore)
                tags = re.findall(r"[A-Za-z][A-Za-z0-9_]+", gene_str)
                # Filter out boolean operators
                tags = [t for t in tags if t not in ("or", "and", "OR", "AND")]
                all_locus_tags.update(tags)

        # Try to match locus tags to gene FIDs
        matched = 0
        for tag in all_locus_tags:
            # Try exact match first
            if tag in fid_to_idx:
                gene_index[tag] = [fid_to_idx[tag]]
                matched += 1
            else:
                # Try partial match (locus tag might be part of the FID)
                matches = [
                    idx for fid, idx in fid_to_idx.items() if tag in fid
                ]
                if matches:
                    gene_index[tag] = matches
                    matched += 1

        print(
            f"  {matched}/{len(all_locus_tags)} locus tags mapped to gene indices"
        )
    except Exception as e:
        print(f"  Warning: Could not build gene index: {e}")

    # --- Compute stats ---
    # Count active/blocked/essential for BOTH rich and minimal media
    # Active = any flux class except "blocked"
    # Essential = flux class contains "essential"
    active_rich = sum(
        1 for r in reactions.values() if r["class_rich"] != "blocked"
    )
    active_min = sum(
        1 for r in reactions.values() if r["class_min"] != "blocked"
    )
    essential_rich = sum(
        1 for r in reactions.values() if "essential" in r["class_rich"]
    )
    essential_min = sum(
        1 for r in reactions.values() if "essential" in r["class_min"]
    )

    stats = {
        "total_reactions": len(reactions),
        "active_rich": active_rich,
        "active_min": active_min,
        "essential_rich": essential_rich,
        "essential_min": essential_min,
        "blocked_rich": len(reactions) - active_rich,
        "blocked_min": len(reactions) - active_min,
    }

    # --- Write output ---
    output = {
        "user_genome": user_genome,
        "n_genomes": n_genomes,
        "reactions": reactions,
        "gene_index": gene_index,
        "stats": stats,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, separators=(",", ":"))

    size_kb = len(json.dumps(output, separators=(",", ":"))) / 1024
    print(f"\nWrote {OUTPUT_PATH} ({size_kb:.0f} KB)")
    print(f"  Stats: {stats}")
    print("Done!")


if __name__ == "__main__":
    main()
