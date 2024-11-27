import requests
import json

# Replace this with your actual GroQ API key
API_KEY = ""  # Get this from https://console.groq.com/keys

def generate_use_cases_with_groq(snippets):
    """
    This function uses the GroQ API to generate AI/ML use cases based on the provided company data.
    """
    
    # Combine the snippets into a single string prompt
    combined_snippets = ""
    for key, values in snippets.items():
        combined_snippets += f"{key}:\n" + "\n".join(values) + "\n\n"
    
    # Prepare the payload for the GroQ API request
    payload = {
        "model": "groq-model-v1",  # Replace with the actual GroQ model name (check GroQ documentation)
        "prompt": f"Based on the following company and industry information, generate relevant use cases for AI/ML technologies (Generative AI, LLMs, Machine Learning) that can improve processes, customer satisfaction, and operational efficiency.\n\nInformation:\n{combined_snippets}\n\nPlease generate 5 use cases.",
        "max_tokens": 500,  # Adjust as necessary
        "temperature": 0.7,  # Adjust for creativity
    }

    # Define the API endpoint for GroQ
    api_url = "https://api.groq.com/v1/generate"  # Replace with actual GroQ API URL
    headers = {
        "Authorization": f"Bearer {API_KEY}",  # Include your GroQ API key
        "Content-Type": "application/json",
    }

    # Send the request to the GroQ API
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json().get("use_cases", [])
    else:
        return {"error": f"Error: {response.status_code}, {response.text}"}

def save_use_cases_to_file(use_cases, file_name="generated_use_cases.json"):
    """
    Save the generated use cases to a JSON file.
    """
    with open(file_name, "w") as file:
        json.dump({"use_cases": use_cases}, file, indent=4)
    print(f"Use cases saved to {file_name}")

# Example Usage
snippets = {
    "infosys industry analysis": ["The IT services industry is highly competitive...", "Infosys focuses on innovation...", "Infosys' market capitalization is 6.2 trillion INR."],
    "infosys business model": ["Infosys provides IT services, consulting, outsourcing..."],
    "infosys AI adoption trends": ["Generative AI spending is growing in 2024...", "AI adoption is predicted to increase by 15% productivity..."],
    "infosys supply chain strategy": ["Infosys accelerates transformation with custom models for supply chain..."]
}

# Generate use cases with GroQ
use_cases = generate_use_cases_with_groq(snippets)

# Save the generated use cases to a file
save_use_cases_to_file(use_cases, "generated_use_cases.json")  # Save to file

# Print out the results for review
print(f"Generated Use Cases: \n{use_cases}")