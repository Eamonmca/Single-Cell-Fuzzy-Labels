# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_Label_Set_harmonisation.ipynb.

# %% auto 0
__all__ = ['match_cell_labels']

# %% ../nbs/03_Label_Set_harmonisation.ipynb 3
def match_cell_labels(existing_labels_set, predicted_labels_set, openai_api_key=None):
    """
    This function matches cell type labels from two sets using OpenAI's GPT-4 model.
    
    Args:
    existing_labels_set (set): A set of existing cell type labels.
    predicted_labels_set (set): A set of predicted cell type labels.
    openai_api_key (str, optional): The API key for OpenAI. If not provided, it will be taken from the environment variable 'OPENAI_API_KEY'.

    Returns:
    dict: A dictionary representing the JSON object with matched labels.
    """
    
    from openai import OpenAI
    import os
    import json
    
    # Use the provided API key or get it from the environment variable
    api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
    if api_key is None:
        raise ValueError("An OpenAI API key must be provided either as an argument or as an environment variable 'OPENAI_API_KEY'.")

    # Construct the prompt
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

    # Extract the response
    bingo = completion.choices[0].message

    # Parse the response as JSON
    try:
        json_data = json.loads(str(bingo.content))
        return json_data
    except json.JSONDecodeError:
        print("The message is not in JSON format.")
        return None


