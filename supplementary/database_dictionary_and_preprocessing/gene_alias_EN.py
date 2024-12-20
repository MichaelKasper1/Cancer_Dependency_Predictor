import requests
import csv
from tqdm import tqdm

def fetch_gene_info(gene_list):
    """
    Fetch alias names and Ensembl IDs for a list of gene symbols using MyGene.info.
    """
    base_url = "https://mygene.info/v3/query"
    gene_info_data = []
    max_aliases = 0

    for gene in tqdm(gene_list, desc="Fetching gene info"):
        params = {
            "q": gene,           # Query gene
            "fields": "alias,ensembl",  # Fields to retrieve
            "species": "human"   # Specify human genes
        }
        response = requests.get(base_url, params=params)
        if response.ok:
            data = response.json()
            if "hits" in data and len(data["hits"]) > 0:
                hit = data["hits"][0]
                # Safely handle the "ensembl" field
                if isinstance(hit.get("ensembl"), list):
                    ensembl_ids = [ens.get("gene", "Unknown") for ens in hit["ensembl"]]
                elif isinstance(hit.get("ensembl"), dict):
                    ensembl_ids = [hit["ensembl"].get("gene", "Unknown")]
                else:
                    ensembl_ids = []

                # Handle "alias" field safely
                aliases = hit.get("alias", [])
                if isinstance(aliases, list):
                    aliases = aliases
                else:
                    aliases = [aliases]

                max_aliases = max(max_aliases, len(aliases))
                gene_info_data.append([gene, ", ".join(ensembl_ids)] + aliases)
            else:
                # No data found
                gene_info_data.append([gene, "No Ensembl ID"])
        else:
            # API error
            gene_info_data.append([gene, "API Error"])
    
    return gene_info_data, max_aliases


def save_to_csv(output_file, gene_info_data, max_aliases):
    """
    Save the gene information to a CSV file.
    """
    header = ["Gene", "Ensembl_ID"] + [f"gene_alias{i+1}" for i in range(max_aliases)]

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for row in gene_info_data:
            # Fill the row with "NA" if there are fewer aliases than max_aliases
            row += ["NA"] * (max_aliases - (len(row) - 2))
            writer.writerow(row)

    print(f"Gene information saved to {output_file}")


# usage
if __name__ == "__main__":
    # Step 1: Read gene list from CSV
    input_file = "median_scores_depmap_EN.csv"
    gene_list = []
    with open(input_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            gene_list.append(row["Gene"])  # Adjust column name as needed

    # Step 2: Fetch gene information
    gene_info_data, max_aliases = fetch_gene_info(gene_list)

    # Step 3: Save to output CSV
    output_file = "gene_alias_ensembl.csv"
    save_to_csv(output_file, gene_info_data, max_aliases)