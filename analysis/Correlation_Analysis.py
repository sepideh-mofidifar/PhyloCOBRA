import os
import pandas as pd
import matplotlib.pyplot as plt
from micom.workflows import load_results

def preprocess_experimental_data(experimental_data, sample_level):
    """Preprocess the experimental data based on the specified taxonomic level.

    Args:
        experimental_data (pd.DataFrame): The experimental data containing taxonomic rates.
        sample_level (str): The taxonomic level of the sample ('species', 'genus', 'family').

    Returns:
        pd.DataFrame: Processed experimental data with relevant columns.
    """
    if sample_level == 'species':
        experimental_data = experimental_data[['species', 'genus', 'id', 'rate']]
        experimental_data = experimental_data.rename(columns={'species': 'taxon', 'id': 'sample_id'})
        experimental_data['taxon'] = experimental_data['taxon'].str.split().str[1]
    elif sample_level == 'genus':
        experimental_data = experimental_data[['genus', 'family', 'id', 'rate']]
        experimental_data = experimental_data.rename(columns={'genus': 'taxon', 'id': 'sample_id'})
    else:
        experimental_data = experimental_data[['family', 'order', 'id', 'rate']]
        experimental_data = experimental_data.rename(columns={'family': 'taxon', 'id': 'sample_id'})
    
    return experimental_data


def calculate_weighted_mean_rate(experimental_data, estimated_growth, category):
    """Calculate the weighted mean rate based on experimental and estimated growth data.

    Args:
        experimental_data (pd.DataFrame): The experimental data containing taxonomic rates.
        estimated_growth (pd.DataFrame): The estimated growth data for the taxa.
        category (str): The taxonomic category to consider for weighting.

    Returns:
        pd.DataFrame: DataFrame containing the taxon, sample ID, and weighted mean rate.
    """
    estimated_growth = estimated_growth.rename(columns={'taxon': category})
    merged_data = experimental_data.merge(estimated_growth, on=[category, 'sample_id'], how='inner')
    merged_data['weighted_rate'] = merged_data['rate'] * merged_data['abundance']
    
    grouped = merged_data.groupby([category, 'sample_id']).agg({
        'weighted_rate': 'sum',
        'abundance': 'sum'
    }).reset_index()
    
    grouped['weighted_mean_rate'] = grouped['weighted_rate'] / grouped['abundance']
    
    return grouped.rename(columns={category: 'taxon', 'weighted_mean_rate': 'rate'})


def correlation_plot(experimental_data, estimated_growth, sample_level):
    """Generate a correlation plot between experimental rates and estimated growth rates.

    Args:
        experimental_data (pd.DataFrame): The experimental data containing taxonomic rates.
        estimated_growth (pd.DataFrame): The estimated growth data for the taxa.
        sample_level (str): The taxonomic level of the sample ('species', 'genus', 'family').

    Returns:
        pd.DataFrame: Merged DataFrame containing the correlation data.
    """
    experimental_data = preprocess_experimental_data(experimental_data, sample_level)
    merged_data = experimental_data.merge(estimated_growth, on=['taxon', 'sample_id'], how='inner')
    
    taxon_grouped = merged_data.groupby(['taxon', 'sample_id'])['rate'].mean().reset_index()
    
    if sample_level == 'species':
        category = 'genus'
    elif sample_level == 'genus':
        category = 'family'
    else:
        category = 'order'
    
    weighted_mean_rate = calculate_weighted_mean_rate(experimental_data, estimated_growth, category)
    
    total_data = pd.concat([weighted_mean_rate, taxon_grouped], ignore_index=True)
    
    return total_data


def plot_correlation(correlation_df, output_file):
    """Plot and save the correlation between rate and growth rate.

    Args:
        correlation_df (pd.DataFrame): The DataFrame containing correlation data.
        output_file (str): The path to save the output plot.
    """
    merged = correlation_df.dropna(subset=['correlation'])
    grouped = merged.groupby('tradeoff')['correlation'].apply(list).reset_index()
    
    plt.figure(figsize=(10, 7))
    plt.axhline(y=0, color='red', linestyle='--')
    plt.boxplot(grouped['correlation'])
    plt.xlabel('Tradeoff')
    plt.ylabel('Correlation')
    plt.title('Correlation between Rate and Growth Rate')
    plt.savefig(output_file)
    plt.show()


# Example usage

# Assuming `rate` and `data` are your input DataFrames
correlation_data = correlation_plot(rate, data, 'genus')

# Merging and calculating correlation
merged_df = correlation_data.merge(data, on=['taxon', 'sample_id'], how='inner')
correlation_df = merged_df.groupby(['tradeoff', 'sample_id']).apply(
    lambda x: x['rate'].corr(x['growth_rate'])
).reset_index(name='correlation')

# Plotting the correlation
output_file = "correlation_plot.png"
plot_correlation(correlation_df, output_file)