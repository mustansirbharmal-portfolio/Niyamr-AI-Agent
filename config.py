import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Azure Cosmos DB Configuration
    COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT')
    COSMOS_KEY = os.getenv('COSMOS_KEY')
    COSMOS_DATABASE_NAME = os.getenv('COSMOS_DATABASE_NAME')
    COSMOS_CONTAINER_NAME = os.getenv('COSMOS_CONTAINER_NAME')
    
    # Azure Blob Storage Configuration
    AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
    
    # Azure Cognitive Search Configuration
    AZURE_SEARCH_SERVICE_NAME = os.getenv('AZURE_SEARCH_SERVICE_NAME')
    AZURE_SEARCH_ADMIN_KEY = os.getenv('AZURE_SEARCH_ADMIN_KEY')
    AZURE_SEARCH_KEY = os.getenv('AZURE_SEARCH_KEY')
    AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
    AZURE_SEARCH_INDEX_NAME = os.getenv('AZURE_SEARCH_INDEX_NAME')
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
    AZURE_OPENAI_EMBEDDING_MODEL = os.getenv('AZURE_OPENAI_EMBEDDING_MODEL')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY')
    FLASK_ENV = os.getenv('FLASK_ENV')
