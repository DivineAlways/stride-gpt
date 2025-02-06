import re
import requests
import streamlit as st
from anthropic import Anthropic
from mistralai import Mistral
from openai import OpenAI, AzureOpenAI
from groq import Groq
from utils import process_groq_response

# Function to create a prompt to generate an attack tree
def create_attack_tree_prompt(app_type, authentication, internet_facing, sensitive_data, app_input):
    prompt = f"""
APPLICATION TYPE: {app_type}
AUTHENTICATION METHODS: {authentication}
INTERNET FACING: {internet_facing}
SENSITIVE DATA: {sensitive_data}
APPLICATION DESCRIPTION: {app_input}
"""
    return prompt


# Function to get attack tree from the GPT response.
def get_attack_tree(api_key, model_name, prompt):
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": """
Act as a cyber security expert with more than 20 years experience of using the STRIDE threat modelling methodology to produce comprehensive threat models for a wide range of applications. Your task is to use the application description provided to you to produce an attack tree in Mermaid syntax. The attack tree should reflect the potential threats for the application based on the details given.

You MUST only respond with the Mermaid code block. See below for a simple example of the required format and syntax for your output.

```mermaid
graph TD
    A[Enter Chart Definition] --> B(Preview)
    B --> C{{decide}}
    C --> D["Keep"]
    C --> E["Edit Definition (Edit)"]
    E --> B
    D --> F["Save Image and Code"]
    F --> B
```

IMPORTANT: Round brackets are special characters in Mermaid syntax. If you want to use round brackets inside a node label you MUST wrap the label in double quotes. For example, ["Example Node Label (ENL)"].
"""},
            {"role": "user", "content": prompt}
        ]
    )

    # Access the 'content' attribute of the 'message' object directly
    attack_tree_code = response.choices[0].message.content
    
    # Remove Markdown code block delimiters using regular expression
    attack_tree_code = re.sub(r'^```mermaid\s*|\s*```$', '', attack_tree_code, flags=re.MULTILINE)

    return attack_tree_code

# Function to get attack tree from the Azure OpenAI response.
def get_attack_tree_azure(azure_api_endpoint, azure_api_key, azure_api_version, azure_deployment_name, prompt):
    client = AzureOpenAI(
        azure_endpoint = azure_api_endpoint,
        api_key = azure_api_key,
        api_version = azure_api_version,
    )

    response = client.chat.completions.create(
        model = azure_deployment_name,
        messages=[
            {"role": "system", "content": """
Act as a cyber security expert with more than 20 years experience of using the STRIDE threat modelling methodology to produce comprehensive threat models for a wide range of applications. Your task is to use the application description provided to you to produce an attack tree in Mermaid syntax. The attack tree should reflect the potential threats for the application based on the details given.

You MUST only respond with the Mermaid code block. See below for a simple example of the required format and syntax for your output.

```mermaid
graph TD
    A[Enter Chart Definition] --> B(Preview)
    B --> C{{decide}}
    C --> D["Keep"]
    C --> E["Edit Definition (Edit)"]
    E --> B
    D --> F["Save Image and Code"]
    F --> B
```

IMPORTANT: Round brackets are special characters in Mermaid syntax. If you want to use round brackets inside a node label you MUST wrap the label in double quotes. For example, ["Example Node Label (ENL)"].
"""},
            {"role": "user", "content": prompt}
        ]
    )

    # Access the 'content' attribute of the 'message' object directly
    attack_tree_code = response.choices[0].message.content
    
    # Remove Markdown code block delimiters using regular expression
    attack_tree_code = re.sub(r'^```mermaid\s*|\s*```$', '', attack_tree_code, flags=re.MULTILINE)

    return attack_tree_code

# Function to get attack tree from the Mistral model's response.
def get_attack_tree_mistral(mistral_api_key, mistral_model, prompt):
    client = Mistral(api_key=mistral_api_key)

    response = client.chat.complete(
        model=mistral_model,
        messages=[
            {"role": "system", "content": """
Act as a cyber security expert with more than 20 years experience of using the STRIDE threat modelling methodology to produce comprehensive threat models for a wide range of applications. Your task is to use the application description provided to you to produce an attack tree in Mermaid syntax. The attack tree should reflect the potential threats for the application based on the details given.

You MUST only respond with the Mermaid code block. See below for a simple example of the required format and syntax for your output.

```mermaid
graph TD
    A[Enter Chart Definition] --> B(Preview)
    B --> C{{decide}}
    C --> D["Keep"]
    C --> E["Edit Definition (Edit)"]
    E --> B
    D --> F["Save Image and Code"]
    F --> B
```

IMPORTANT: Round brackets are special characters in Mermaid syntax. If you want to use round brackets inside a node label you MUST wrap the label in double quotes. For example, ["Example Node Label (ENL)"].
"""},
            {"role": "user", "content": prompt}
        ]
    )

    # Access the 'content' attribute of the 'message' object directly
    attack_tree_code = response.choices[0].message.content
    
    # Remove Markdown code block delimiters using regular expression
    attack_tree_code = re.sub(r'^```mermaid\s*|\s*```$', '', attack_tree_code, flags=re.MULTILINE)

    return attack_tree_code

# Function to get attack tree from Ollama hosted LLM.
def get_attack_tree_ollama(ollama_endpoint, ollama_model, prompt):
    """
    Get attack tree from Ollama hosted LLM.
    
    Args:
        ollama_endpoint (str): The URL of the Ollama endpoint (e.g., 'http://localhost:11434')
        ollama_model (str): The name of the model to use
        prompt (str): The prompt to send to the model
        
    Returns:
        str: The generated attack tree code in Mermaid syntax
        
    Raises:
        requests.exceptions.RequestException: If there's an error communicating with the Ollama endpoint
        KeyError: If the response doesn't contain the expected fields
    """
    if not ollama_endpoint.endswith('/'):
        ollama_endpoint = ollama_endpoint + '/'
    
    url = ollama_endpoint + "api/chat"

    data = {
        "model": ollama_model,
        "stream": False,
        "messages": [
            {
                "role": "system", 
                "content": """
Act as a cyber security expert with more than 20 years experience of using the STRIDE threat modelling methodology to produce comprehensive threat models for a wide range of applications. Your task is to use the application description provided to you to produce an attack tree in Mermaid syntax. The attack tree should reflect the potential threats for the application based on the details given.

You MUST only respond with the Mermaid code block. See below for a simple example of the required format and syntax for your output.

```mermaid
graph TD
    A[Enter Chart Definition] --> B(Preview)
    B --> C{{decide}}
    C --> D["Keep"]
    C --> E["Edit Definition (Edit)"]
    E --> B
    D --> F["Save Image and Code"]
    F --> B
```

IMPORTANT: Round brackets are special characters in Mermaid syntax. If you want to use round brackets inside a node label you MUST wrap the label in double quotes. For example, ["Example Node Label (ENL)"].
"""},
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(url, json=data, timeout=60)  # Add timeout
        response.raise_for_status()  # Raise exception for bad status codes
        outer_json = response.json()
        
        try:
            # Access the 'content' attribute of the 'message' dictionary
            attack_tree_code = outer_json["message"]["content"]
            
            # Remove Markdown code block delimiters using regular expression
            attack_tree_code = re.sub(r'^```mermaid\s*|\s*```$', '', attack_tree_code, flags=re.MULTILINE)
            
            return attack_tree_code
            
        except KeyError as e:
            print(f"Error accessing response fields: {str(e)}")
            print("Raw response:", outer_json)
            raise
            
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama endpoint: {str(e)}")
        raise

# Function to get attack tree from Anthropic's Claude model.
def get_attack_tree_anthropic(anthropic_api_key, anthropic_model, prompt):
    client = Anthropic(api_key=anthropic_api_key)

    response = client.messages.create(
        model=anthropic_model,
        max_tokens=1024,
        system="""
Act as a cyber security expert with more than 20 years experience of using the STRIDE threat modelling methodology to produce comprehensive threat models for a wide range of applications. Your task is to use the application description provided to you to produce an attack tree in Mermaid syntax. The attack tree should reflect the potential threats for the application based on the details given.
You MUST only respond with the Mermaid code block. See below for a simple example of the required format and syntax for your output.
```mermaid
graph TD
    A[Enter Chart Definition] --> B(Preview)
    B --> C{{decide}}
    C --> D["Keep"]
    C --> E["Edit Definition (Edit)"]
    E --> B
    D --> F["Save Image and Code"]
    F --> B
```
IMPORTANT: Round brackets are special characters in Mermaid syntax. If you want to use round brackets inside a node label you MUST wrap the label in double quotes. For example, ["Example Node Label (ENL)"].
""",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Access the 'content' attribute of the 'message' object directly
    attack_tree_code = response.content[0].text

    # Remove Markdown code block delimiters using regular expression
    attack_tree_code = re.sub(r'^```mermaid\s*|\s*```$', '', attack_tree_code, flags=re.MULTILINE)

    return attack_tree_code

# Function to get attack tree from LM Studio Server response.
def get_attack_tree_lm_studio(lm_studio_endpoint, model_name, prompt):
    client = OpenAI(
        base_url=f"{lm_studio_endpoint}/v1",
        api_key="not-needed"  # LM Studio Server doesn't require an API key
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides attack trees in Mermaid format."},
            {"role": "user", "content": prompt}
        ]
    )

    # Access the content directly as the response will be in text format
    mermaid_code = response.choices[0].message.content

    return mermaid_code

# Function to get attack tree from the Groq model's response.
def get_attack_tree_groq(groq_api_key, groq_model, prompt):
    client = Groq(api_key=groq_api_key)
    response = client.chat.completions.create(
        model=groq_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides attack trees in Mermaid diagram format."},
            {"role": "user", "content": prompt}
        ]
    )

    # Process the response using our utility function
    reasoning, mermaid_code = process_groq_response(
        response.choices[0].message.content,
        groq_model,
        expect_json=False
    )
    
    # If we got reasoning, display it in an expander in the UI
    if reasoning:
        with st.expander("View model's reasoning process", expanded=False):
            st.write(reasoning)

    # Clean up the response by removing any markdown code block markers
    mermaid_code = mermaid_code.replace('```mermaid', '').replace('```', '').strip()

    return mermaid_code