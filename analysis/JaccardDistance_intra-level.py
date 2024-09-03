import os
import pandas as pd
from micom import load_pickle
import numpy as np
from cobra.io import load_json_model


def jaccard_distance(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    jaccard_similarity = intersection / union
    return 1 - jaccard_similarity


def calculate_jaccard_distance(folder_path, dataset_path,output_path, taxonomy_level, model_ext='.json'):
    # Get the list of pickle files
    pickle_files = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if f.endswith('.pickle')]

    # Initialize the result DataFrame
    jacardDistanceResult = pd.DataFrame(columns=[taxonomy_level, 'higher_level', 'sampleId', 'jacardDist'])

    for pick in pickle_files:
        os.chdir(folder_path)
        commodel = load_pickle(pick + ".pickle")
        taxonomy = commodel.taxonomy
        higher_level_info = []

        # Collect relevant higher-level (order) information
        for f in range(len(taxonomy['file'])):
            if isinstance(taxonomy[taxonomy_level][f], list):
                higher_level_info.append(taxonomy['id'][f])
            if isinstance(taxonomy[taxonomy_level][f], float) and math.isnan(taxonomy[taxonomy_level][f]):
                family = [os.path.basename(path) for path in taxonomy['file'][f]]
                taxonomy[taxonomy_level][f] = [x.split('.')[0] for x in family]
                higher_level_info.append(taxonomy['id'][f])

        reactionInfo = commodel.reactions
        reactionId = [x.id for x in reactionInfo]

        # Change directory to where the model files are located
        os.chdir(dataset_path)

        for higher_level in higher_level_info:
            specific_order = [x for x in reactionId if higher_level in x]
            RId_specific_order = [x.split('__')[0] for x in specific_order]
            RId_specific_order_set = set(RId_specific_order)

            specific_taxonomy = taxonomy.loc[taxonomy['id'] == higher_level][taxonomy_level]
            specific_taxonomy = specific_taxonomy.values[0]

            for model_name in specific_taxonomy:
                model = load_json_model(model_name + model_ext)
                modelR = [x.id for x in model.reactions]
                modelR_set = set(modelR)

            # Store the result in a dictionary
                result = {
                    taxonomy_level: model_name if taxonomy_level == "genus" else model_name[:-5],
                    'higher_level': higher_level,
                    'sampleId': commodel.id,
                    'jacardDist': jaccard_distance(modelR_set, RId_specific_order_set)
                }

                # Append the result to the DataFrame
                jacardDistanceResult = pd.concat([jacardDistanceResult, pd.DataFrame([result])], ignore_index=True)
    # Save the result to a CSV file
    jacardDistanceResult.to_csv(output_path, index=False)

# Example usage for genus-level analysis
calculate_jaccard_distance(
    folder_path='D:\\GenusLevel',
    dataset_path='D:\\DrTefagh\\MICOMarticle\\materials\\AgoraGenusDataset',
    output_path='D:\\GenusLevel\\jacardDistanceGenusLevel.csv',
    taxonomy_level='genus',
    model_ext='.json'
)