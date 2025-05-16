import pandas as pd
import warnings
from scipy.stats import zscore
from kestra import Kestra
import os
import argparse

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

parser = argparse.ArgumentParser(description="Process final merged wine data.")
parser.add_argument("--input_file", required=True, help="Path to the input CSV file")
args = parser.parse_args()
input_file = args.input_file

logging = Kestra.logger()

logging.info("Starting the script.")

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

try:
    logging.info(f"Loading data from {input_file}")
    final_df = pd.read_csv(input_file)
    logging.info(f"Data loaded with {len(final_df)} rows and {len(final_df.columns)} columns.")
    logging.info(f"Columns: {final_df.columns.tolist()}")
    
    # Example processing (replace with actual logic as needed)
    total_revenue = final_df['CA'].sum()
    logging.info(f"Total global revenue: {total_revenue}")
    
except Exception as e:
    logging.warning(f"An unexpected error occurred: {e}")

    logging.info("DuckDB seemed to have failed, running the data preparation with Python instead")
    # Chargement des fichiers Excel
    web = pd.read_excel("data/Fichier_web.xlsx", engine='openpyxl')
    erp = pd.read_excel("data/Fichier_erp.xlsx", engine='openpyxl')
    liaison = pd.read_excel("data/fichier_liaison.xlsx", engine='openpyxl')

    logging.info("Inports completed")

    logging.info("")
    logging.info("BEFORE PROCESSING")
    logging.info("----------------------------")
    logging.info(f"the length of web is {len(web)}")
    logging.info(f"the length of erp is {len(erp)}")
    logging.info(f"the length of liaison is {len(liaison)}")

    logging.info("")
    logging.info("INITIAL PROCESSING")
    logging.info("----------------------------")


    erp = erp.drop_duplicates(subset="product_id")
    logging.info(f"the length of erp after deduplication is {len(erp)}")
    liaison = liaison.drop_duplicates()
    logging.info(f"the length of liaison after deduplication is {len(liaison)}")

    # Nettoyage : suppression des lignes vides
    web = web.dropna(subset=["sku", "post_title"])
    logging.info(f"the length of web after NA cleaning is {len(web)}")

    # Supprimer les doublons
    web = web.drop_duplicates(subset="sku")
    logging.info(f"the length of web after deduplication is {len(web)}")

    logging.info("")
    logging.info("EXPORTING FILES FOR TESTING")
    logging.info("----------------------------")

    erp.to_csv(f"{output_dir}/erp.csv", index=False)
    logging.info("rapport_chiffres_affaires.xlsx exported successfully")

    liaison.to_csv(f"{output_dir}/liaison.csv", index=False)
    logging.info("vins_millesimes.csv exported successfully")

    web.to_csv(f"{output_dir}/web.csv", index=False)
    logging.info("web.csv exported successfully")


    logging.info("")
    logging.info("MERGING DATAFRAMES")
    # Merge web and liaison using the 'sku' and 'id_web' columns
    merged_df = pd.merge(web, liaison, left_on='sku', right_on='id_web', how='left')

    # Merge the result with erp using the 'product_id' column
    final_df = pd.merge(merged_df, erp, on='product_id', how='left')

    # Drop the 'id_web' column if you don't need it anymore
    final_df.drop(columns=['id_web'], inplace=True)

    logging.info("MERGING COMPLETED")
    logging.info("")

    logging.info(f"the length of final df is {len(final_df)}")

    logging.info("")
    logging.info("CALCULATING TOTAL SALES")
    logging.info("----------------------------")
    final_df["CA"] = final_df["price"] * final_df["total_sales"]
    final_df["CA"].sum()
    logging.info(f"the total sales is {final_df['CA'].sum()}")

    logging.info("EXPORTING MERGED FILE FOR TESTING")
    logging.info("----------------------------")
    final_df.to_csv(f"{output_dir}/final_merge.csv", index=False)
    logging.info("web.csv exported successfully")

logging.info("")
logging.info("FINDING OUT WHICH WINES ARE MILLÉSIME")
logging.info("----------------------------")
mean_price = final_df["price"].mean()
std_price = final_df["price"].std()

# Calculate the z-score for each wine
final_df["z_score"] = (final_df["price"] - mean_price) / std_price

# Identify millésime and ordinary wines
final_df["type_vin"] = final_df["z_score"].apply(lambda z: "millésime" if z > 2 else "ordinaire")

millésime_count = final_df[final_df["type_vin"] == "millésime"].shape[0]
logging.info(f"{millésime_count} wines are millésime")


logging.info("")
logging.info("EXPORTING FILES")
logging.info("----------------------------")

# Select only the relevant columns for the first sheet
wine_details = final_df[[
    "sku", "post_title", "price", "total_sales", "post_date", "CA"
]].sort_values("CA", ascending=False)
# Create a one-row DataFrame for the summary sheet
total_ca_df = pd.DataFrame({
    "Total Chiffre d'Affaires (€)": [final_df["CA"].sum()]
})
with pd.ExcelWriter(f"{output_dir}/rapport_chiffres_affaires.xlsx") as writer:
    wine_details.to_excel(writer, sheet_name="Détails des Vins", index=False)
    total_ca_df.to_excel(writer, sheet_name="Total CA", index=False)
logging.info("rapport_chiffres_affaires.xlsx exported successfully")

premium_wines = final_df[final_df["type_vin"] == "millésime"][[
    "sku", "post_title", "post_excerpt","price", "post_date"]]
premium_wines.to_csv(f"{output_dir}/vins_millesimes.csv", index=False)
logging.info("vins_millesimes.csv exported successfully")

ordinary_wines = final_df[final_df["type_vin"] == "ordinaire"][[
    "sku", "post_title", "post_excerpt","price", "post_date"]]
ordinary_wines.to_csv(f"{output_dir}/vins_ordinaire.csv", index=False)
logging.info("vins_ordinaire.csv exported successfully")

