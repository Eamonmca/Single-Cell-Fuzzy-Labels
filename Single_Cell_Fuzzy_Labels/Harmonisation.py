# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_Label_Set_harmonisation.ipynb.

# %% auto 0
__all__ = ['match_cell_labels', 'map_labels_to_categories']

# %% ../nbs/03_Label_Set_harmonisation.ipynb 3
def match_cell_labels(existing_labels_set:set, # A set of existing cell type labels
                      predicted_labels_set:set, # A set of predicted cell type labels
                      openai_api_key:str=None  # The API key for OpenAI. If not provided, it will be taken from the environment variable 'OPENAI_API_KEY'
                      ) -> dict: # A dictionary representing the JSON object with matched labels.
    
    """
    This function matches cell type labels from two sets using OpenAI's GPT-4 model.
    """
    
    # Import necessary libraries
    from openai import OpenAI
    import os
    import json
    
    # Use the provided API key or get it from the environment variable
    api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
    if api_key is None:
        raise ValueError("An OpenAI API key must be provided either as an argument or as an environment variable 'OPENAI_API_KEY'.")

    # Construct the prompt for the OpenAI model
    prompt = f"First set of labels: {existing_labels_set}. Second set of labels: {predicted_labels_set}. " \
             "Associate each label in the first set with labels in the second set, based on cell type similarity, " \
             "as accurately as possible. Return answer as JSON object"

    # Initialize the OpenAI client with the API key
    client = OpenAI(api_key=api_key)

    # Create a completion request to the OpenAI API
    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "You are a knowledgeable Cell Biologist who is capable of comparing and relating different types of cell classifications. Two lists of cell type labels will be provided to you. Your task is to match each label from the first list with the most appropriate corresponding label(s) from the second list. There might be situations where multiple labels from either list match one label in the other list. Your responses need to showcase the strength of your analysis and reasoning, based on your scientific understanding and the knowledge you have gained from extensive reading on this subject. Submit your answers in the form of a JSON object."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    # Extract the response from the completion object
    bingo = completion.choices[0].message

    # Parse the response as JSON
    try:
        json_data = json.loads(str(bingo.content))
        return json_data
    except json.JSONDecodeError:
        print("The message is not in JSON format.")
        return None


# %% ../nbs/03_Label_Set_harmonisation.ipynb 4
def map_labels_to_categories(label_list: list, # A list of labels that need to be categorized
                             label_dict: dict # A dictionary where keys are categories and values are lists of labels belonging to those categories
                             ) -> list: # Returns a list of categories corresponding to each label in `label_list`.
    
    """
    Maps each label in `label_list` to its corresponding category based on `label_dict`.
    """
    label_to_category = {}

    # Constructing a mapping from label to category
    for category, labels in label_dict.items():
        if isinstance(labels, list):
            for label in labels:
                label_to_category[label] = category
        else:
            label_to_category[labels] = category

    # Mapping each label in the label_list to its category
    mapped_list = [label_to_category.get(label, "unknown") for label in label_list]

    return mapped_list
