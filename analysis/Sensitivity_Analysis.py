import os
import pandas as pd
import numpy as np
from micom.workflows import build, grow, save_results
from micom.qiime_formats import load_qiime_medium

def sensitivity_analysis(taxonomy, model_db, medium_file, output_folder, n, sigma, type, threads=2, solver="cplex"):
    # Load the CSV file and process it
    df = pd.read_csv(taxonomy)
    df = df.rename(columns={'samples': 'sample_id', 'reads': 'abundance'})
    df['id'] = df['family']
    df = df[['sample_id', 'family', 'id', 'abundance']]

    # Get a list of unique sample IDs
    samples = list(df['sample_id'].unique())

    # Iterate over each sample ID and perform the simulation and growth
    for ids in samples:
        for i in range(n):
        # Generate random values and modify the abundance
            df_ids = df.loc[df['sample_id'] == ids]
            random_values = np.random.normal(0, sigma, len(df_ids))
            random_values = random_values * df_ids['abundance']
            df_ids['abundance'] += random_values

            # Build the community model
            manifest = build(df_ids, model_db, output_folder, solver=solver, threads=threads)

            # Load the medium and grow the community model
            medium = load_qiime_medium(medium_file)
            growth_results = grow(manifest, output_folder, medium, tradeoff=0.1, threads=threads)

            # Save the results with a unique filename
            os.chdir(output_folder)
            name = f"{ids}_{sigma}_{type}_{i}.zip"
            save_results(growth_results, name)

            # Clean up the output folder
            for filename in os.listdir(output_folder):
                if filename.endswith(".pickle"):
                    file_path = os.path.join(output_folder, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                       os.unlink(file_path)
# Example usage
taxonomy = r"D:\family.csv"
model_db = r"D:\agora103_family.qza"
medium_file = "D:\western_diet_gut.qza"
n = 2
sigma = 1
type = 'merged'
threads = 2
output_folder = r"D:\SensitivityAnalysis"

sensitivity_analysis(taxonomy, model_db, medium_file, output_folder, n, sigma, type, threads=threads, solver="cplex")