#!/usr/bin/env python3
"""Generate ../data/metadata.json for the Genome Heatmap Viewer.

Extracts genome-specific metadata from the database dynamically.
This allows the viewer to work with any genome database without hardcoding.
"""

import json
import re
import sqlite3
import sys

DB_PATH = "/Users/jplfaria/repos/genome-heatmap-viewer/berdl_tables.db"
OUTPUT_PATH = "/Users/jplfaria/repos/genome-heatmap-viewer/../data/metadata.json"


def parse_organism_name(genome_id):
    """Extract organism name from user genome ID.

    Examples:
        user_Acinetobacter_baylyi_ADP1_RAST -> Acinetobacter baylyi ADP1
        user_Escherichia_coli_K12_MG1655_RAST -> Escherichia coli K-12 MG1655
    """
    # Remove 'user_' prefix and '_RAST' suffix
    name = genome_id.replace("user_", "").replace("_RAST", "")

    # Replace underscores with spaces
    name = name.replace("_", " ")

    # Handle special cases like K12 -> K-12
    name = re.sub(r'\bK12\b', 'K-12', name)

    return name


def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    print("Extracting genome metadata from database...")

    # --- Step 1: Identify user genome ---
    user_row = conn.execute(
        "SELECT id, gtdb_taxonomy, ncbi_taxonomy, n_contigs, n_features FROM genome WHERE id LIKE 'user_%' LIMIT 1"
    ).fetchone()

    if not user_row:
        print("ERROR: No user genome found in database")
        sys.exit(1)

    user_genome_id = user_row["id"]
    organism_name = parse_organism_name(user_genome_id)

    print(f"  User genome: {user_genome_id}")
    print(f"  Organism: {organism_name}")

    # --- Step 2: Count reference genomes ---
    n_ref_genomes = conn.execute(
        "SELECT COUNT(*) as count FROM genome WHERE id NOT LIKE 'user_%'"
    ).fetchone()["count"]

    print(f"  Reference genomes: {n_ref_genomes}")

    # --- Step 3: Count genes ---
    n_genes = conn.execute(
        "SELECT COUNT(*) as count FROM genome_features WHERE genome_id = ?",
        (user_genome_id,)
    ).fetchone()["count"]

    print(f"  Genes: {n_genes}")

    # --- Step 4: Get taxonomy ---
    taxonomy = user_row["gtdb_taxonomy"] or user_row["ncbi_taxonomy"] or "Unknown"

    # --- Step 5: Try to get genome assembly ID ---
    # Look for common patterns in genome_id or try to extract from taxonomy
    assembly_id = None

    # Check if there's a GCF/GCA pattern we can extract
    # For now, use a placeholder or try to find it in related tables
    if "GCF" in user_genome_id or "GCA" in user_genome_id:
        match = re.search(r'(GC[AF]_\d+\.\d+)', user_genome_id)
        if match:
            assembly_id = match.group(1)

    # If not found, leave as None - frontend can handle this
    if not assembly_id:
        assembly_id = "Unknown"

    print(f"  Assembly: {assembly_id}")

    # --- Step 6: Build metadata object ---
    metadata = {
        "organism": organism_name,
        "genome_id": user_genome_id,
        "genome_assembly": assembly_id,
        "n_ref_genomes": n_ref_genomes,
        "n_genes": n_genes,
        "n_contigs": user_row["n_contigs"],
        "taxonomy": taxonomy,
        "database_type": "BERDL",
    }

    conn.close()

    # --- Step 7: Write output ---
    with open(OUTPUT_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nWrote {OUTPUT_PATH}")
    print(f"  {organism_name}")
    print(f"  {n_genes} genes, {n_ref_genomes} reference genomes")
    print("Done!")


if __name__ == "__main__":
    main()
