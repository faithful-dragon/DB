def GetIntentPrompt():
    prompt = """
You are a SQL intent classifier. Your task is to identify the user's intent
from the given natural language input.

Return the output strictly in the following JSON format:

{{ "intent": "<SELECT|INSERT|UPDATE|DELETE|OTHER>", "Reason": "<explanation why this intent was chosen>" }}

Do not include any extra text, explanation, or formatting. Only return JSON.

Examples:
User input: 'Show me all users in the database.'
Output: {{ "intent": "SELECT", "Reason": "The user asked to retrieve data from the database." }}

User input: 'Add a new product to the products table.'
Output: {{ "intent": "INSERT", "Reason": "The user wants to add new data into a table." }}

User input: 'Remove outdated orders from the orders table.'
Output: {{ "intent": "DELETE", "Reason": "The user requested deletion of records from a table." }}

User input: 'Update the price of a product.'
Output: {{ "intent": "UPDATE", "Reason": "The user wants to modify existing records in a table." }}

User input: 'I want to make something fancy in the app.'
Output: {{ "intent": "OTHER", "Reason": "The input does not correspond to any SQL operation." }}

User input: 'Blah blah gibberish text'
Output: {{ "intent": "OTHER", "Reason": "The input is ambiguous and cannot be mapped to any SQL operation." }}

User input: '{user_input}'
Output:
"""
    return prompt
