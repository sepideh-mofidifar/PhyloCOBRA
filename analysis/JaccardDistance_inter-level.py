import os
import pandas as pd
from micom import load_pickle

def jaccard_distance(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    jaccard_similarity = intersection / union
    return 1 - jaccard_similarity


def calculate_jaccard_distances(folder_path, output_path):
    os.chdir(folder_path)
    # Get the list of pickle files without the extension
    pickle_files = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if f.endswith('.pickle')]

    # Initialize an empty DataFrame to store results
    jacardDistanceResult = pd.DataFrame(columns=['model1', 'model2', 'sampleId', 'jacardDist'])

    for pick in pickle_files:
        # Change directory to the folder containing the pickle files and load the community model
        commodel = load_pickle(pick + ".pickle")

        # Extract taxonomy and reaction information
        taxonomy = commodel.taxonomy
        reactionInfo = commodel.reactions
        reactionId = [x.id for x in reactionInfo]

        # Change directory to the data folder
        orderInfo = taxonomy.id

        # Calculate Jaccard distances between pairs of models
        for i in range(len(orderInfo)):
            for j in range(i + 1, len(orderInfo)):
                orderi = [x for x in reactionId if orderInfo[i] in x]
                RIdorderi = [x.split('__')[0] for x in orderi]
                RIdorderseti = set(RIdorderi)

                orderj = [x for x in reactionId if orderInfo[j] in x]
                RIdorderj = [x.split('__')[0] for x in orderj]
                RIdordersetj = set(RIdorderj)

                x = {
                    'model1': orderInfo[i],
                    'model2': orderInfo[j],
                    'sampleId': commodel.id,
                    'jacardDist': jaccard_distance(RIdorderseti, RIdordersetj)
                }

                jacardDistanceResult = pd.concat([jacardDistanceResult, pd.DataFrame([x])], ignore_index=True)
                

        # Save the results to a CSV file
    jacardDistanceResult.to_csv(output_path, index=False)

# Example usage for genus-level analysis
folder_path = 'D:\\GenusLevel'
output_path = "D:\\GenusLevel\\jacardDistanceGenusLevel.csv"
calculate_jaccard_distances(folder_path, output_path)