import requests
import json
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment

# API keys for SerpAPI and GroQ
SERPAPI_KEY = "9b2db00270fd4fc5506c08d8f4b8c3cd197d005cf8df6c82f43816ddd7f2b71e"
GROQ_API_KEY = "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"


def fetch_datasets_with_serpapi(keywords):
    """
    Use SerpAPI to search for dataset links from Kaggle, GitHub, and HuggingFace.
    Returns a dictionary with platform names as keys and clickable links as values.
    """
    queries = {
        "Kaggle": f"{keywords} site:kaggle.com",
        "GitHub": f"{keywords} site:github.com",
        "HuggingFace": f"{keywords} site:huggingface.co"
    }

    dataset_links = {}

    for platform, query in queries.items():
        search_url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": 5  # Fetch top 5 results
        }

        try:
            response = requests.get(search_url, params=params)
            if response.status_code == 200:
                results = response.json().get("organic_results", [])
                links = [result["link"] for result in results if "link" in result]
                dataset_links[platform] = links
            else:
                dataset_links[platform] = [f"Error fetching datasets from {platform} (status code: {response.status_code})"]
        except Exception as e:
            dataset_links[platform] = [f"Error fetching datasets from {platform}: {e}"]
    print('dataset_links')
    print(dataset_links)
    return dataset_links


def search_with_serpapi(query):
    """
    Perform a web search using SerpAPI.
    """
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 2  # Number of results to fetch
    }
    url = "https://serpapi.com/search"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("organic_results", [])
    else:
        return {"error": f"Error: {response.status_code}, {response.text}"}


def research_industry(company_name):
    """
    Perform market research on the company and its industry.
    """
    queries = [
        f"{company_name} industry analysis",
        f"{company_name} business model",
        f"{company_name} key offerings",
        f"{company_name} strategic focus areas",
        f"{company_name} AI adoption trends",
        f"{company_name} market trends",
        f"{company_name} AI and automation adoption",
        f"{company_name} supply chain strategy",
        f"{company_name} customer experience strategy",
        f"{company_name} vision and product innovations"
    ]
    
    results = {query: search_with_serpapi(query) for query in queries}
    return results


def extract_snippets(data):
    """
    Extract the 'snippet' field from the search results.
    """
    snippets = {}
    print(data)
    for query, results in data.items():
        snippets[query] = [result.get("snippet", "No snippet available") for result in results]
    return snippets


def save_to_file(data, file_name):
    """
    Save data to a JSON file.
    """
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {file_name}")


def generate_use_cases_with_groq(snippets):
    """
    Use GroQ API to generate AI/ML use cases based on the provided snippets.
    """
    combined_snippets = ""
    for key, values in snippets.items():
        combined_snippets += f"{key}:\n" + "\n".join(values) + "\n\n"
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "user",
                "content": f"Based on the following company and industry information, generate 5 actionable use cases where the company can leverage Generative AI (GenAI), Large Language Models (LLMs), and Machine Learning (ML) technologies to improve their processes, enhance customer satisfaction, and boost operational efficiency. For each use case, provide a title and a detailed description of how the technology would be applied:\n\n{combined_snippets}"
            }
        ],
        "max_tokens": 1024,
        "temperature": 1
    }

    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json().get("choices", [])
    else:
        return {"error": f"Error: {response.status_code}, {response.text}"}


def save_use_cases_to_excel_with_links(use_cases, file_name):
    """
    Save the generated use cases to an Excel sheet with three columns: Use Case, Description, Dataset Links.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Use Cases"

    # Add headers
    ws.append(["Use Case", "Description", "Dataset Links"])

    # Add use case data
    for use_case in use_cases:
        if "message" in use_case and "content" in use_case["message"]:
            content = use_case["message"]["content"]
            lines = content.split("\n")
            titles = [line.split(":")[1].strip() for line in lines if line.startswith("Title")]
            descriptions = [line.split(":")[1].strip() for line in lines if line.startswith("Description")]

            for title, description in zip(titles, descriptions):
                # Fetch dataset links for the title
                dataset_links = fetch_datasets_with_serpapi(title)
                links = "\n".join([f"{platform}: {', '.join(links)}" for platform, links in dataset_links.items()])
                ws.append([title, description, links])

    wb.save(file_name)
    print(f"Use cases with dataset links saved to Excel: {file_name}")


def main(company_name, output_path):
    """
    Main function to conduct industry research and generate use cases.
    """
    # Perform research
    print(f"Conducting research for {company_name}...")
    research_data = research_industry(company_name)
    
    # Save raw research data
    save_to_file(research_data, f"{output_path}/{company_name}_responses.json")
    
    # Extract snippets
    snippets = extract_snippets(research_data)
    snippets_file = f"{output_path}/{company_name}_snippets.json"
    save_to_file(snippets, snippets_file)
    
    # Generate use cases using the snippets
    print(f"Generating use cases for {company_name}...")
    use_cases = generate_use_cases_with_groq(snippets)
    
    # Save use cases with dataset links to Excel
    use_cases_excel = f"{output_path}/{company_name}_use_cases_with_links.xlsx"
    save_use_cases_to_excel_with_links(use_cases, use_cases_excel)
    
    print(f"Snippets saved to: {snippets_file}")
    print(f"Use cases with dataset links saved to Excel: {use_cases_excel}")

company_name = "TCS"
output_path = r"D:\MarketLensAI"
main(company_name, output_path)