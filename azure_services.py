import os
import json
from typing import List, Dict, Any
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, PartitionKey
from openai import AzureOpenAI
from config import Config

class AzureServices:
    def __init__(self):
        self.config = Config()
        self._setup_openai()
        self._setup_search_client()
        self._setup_blob_client()
        self._setup_cosmos_client()
    
    def _setup_openai(self):
        """Setup Azure OpenAI client"""
        self.openai_client = AzureOpenAI(
            api_key=self.config.AZURE_OPENAI_API_KEY,
            api_version=self.config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=self.config.AZURE_OPENAI_ENDPOINT
        )
    
    def _setup_search_client(self):
        """Setup Azure Cognitive Search client"""
        credential = AzureKeyCredential(self.config.AZURE_SEARCH_ADMIN_KEY)
        self.search_client = SearchClient(
            endpoint=self.config.AZURE_SEARCH_ENDPOINT,
            index_name=self.config.AZURE_SEARCH_INDEX_NAME,
            credential=credential
        )
        self.search_index_client = SearchIndexClient(
            endpoint=self.config.AZURE_SEARCH_ENDPOINT,
            credential=credential
        )
    
    def _setup_blob_client(self):
        """Setup Azure Blob Storage client"""
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.config.AZURE_STORAGE_CONNECTION_STRING
        )
    
    def _setup_cosmos_client(self):
        """Setup Azure Cosmos DB client"""
        self.cosmos_client = CosmosClient(
            self.config.COSMOS_ENDPOINT,
            self.config.COSMOS_KEY
        )
        self.database = self.cosmos_client.get_database_client(self.config.COSMOS_DATABASE_NAME)
        self.container = self.database.get_container_client(self.config.COSMOS_CONTAINER_NAME)
        
        # Setup actSummary container with better error handling
        self.act_summary_container = None
        try:
            # First try to get existing container
            self.act_summary_container = self.database.get_container_client("actSummary")
            print("✅ actSummary container found")
        except Exception:
            # Container doesn't exist, try to create it
            try:
                print("📋 Creating actSummary container...")
                container = self.database.create_container(
                    id="actSummary",
                    partition_key=PartitionKey(path="/document_type"),
                    offer_throughput=400  # Minimum throughput
                )
                self.act_summary_container = self.database.get_container_client("actSummary")
                print("✅ Created actSummary container successfully")
            except Exception as e:
                print(f"⚠️ Could not create actSummary container: {e}")
                print("Please create the container manually in Azure Portal")
                self.act_summary_container = None
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embeddings using Azure OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.config.AZURE_OPENAI_EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def chat_completion(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """Generate chat completion using Azure OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in chat completion: {e}")
            return ""
    
    def download_blob(self, blob_name: str) -> bytes:
        """Download blob from Azure Storage"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.config.AZURE_STORAGE_CONTAINER_NAME,
                blob=blob_name
            )
            return blob_client.download_blob().readall()
        except Exception as e:
            print(f"Error downloading blob: {e}")
            return b""
    
    def search_documents(self, query: str, top: int = 5) -> List[Dict]:
        """Search documents in Azure Cognitive Search"""
        try:
            results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            return [dict(result) for result in results]
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def vector_search(self, query_vector: List[float], top: int = 5) -> List[Dict]:
        """Perform vector search in Azure Cognitive Search"""
        try:
            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=top,
                fields="content_vector"
            )
            results = self.search_client.search(
                vector_queries=[vector_query],
                top=top
            )
            return [dict(result) for result in results]
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []
    
    def upload_to_search_index(self, documents: List[Dict]) -> bool:
        """Upload documents to Azure Search index"""
        try:
            result = self.search_client.upload_documents(documents)
            return all(r.succeeded for r in result)
        except Exception as e:
            print(f"Error uploading to search index: {e}")
            return False
    
    def store_in_cosmos(self, document: Dict) -> bool:
        """Store document in Cosmos DB"""
        try:
            self.container.upsert_item(body=document)  # Use upsert instead of create
            return True
        except Exception as e:
            print(f"Error storing in Cosmos DB: {e}")
            return False
    
    def query_cosmos(self, query: str, parameters: List = None) -> List[Dict]:
        """Query Cosmos DB"""
        try:
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            return items
        except Exception as e:
            print(f"Error querying Cosmos DB: {e}")
            return []
    
    def store_act_summary(self, document_type: str, data: Dict) -> bool:
        """Store data in actSummary container"""
        try:
            if not self.act_summary_container:
                print("⚠️ actSummary container not available")
                return False
            
            # Add required fields
            data["document_type"] = document_type
            if "id" not in data:
                import uuid
                data["id"] = str(uuid.uuid4())
            
            # Add timestamp if not present
            if "timestamp" not in data:
                from datetime import datetime
                data["timestamp"] = datetime.utcnow().isoformat()
            
            self.act_summary_container.upsert_item(body=data)  # Use upsert instead of create
            return True
        except Exception as e:
            print(f"Error storing in actSummary: {e}")
            return False
    
    def get_act_summary(self, document_type: str = None) -> List[Dict]:
        """Retrieve data from actSummary container"""
        try:
            if not self.act_summary_container:
                return []
            
            if document_type:
                query = "SELECT * FROM c WHERE c.document_type = @doc_type"
                parameters = [{"name": "@doc_type", "value": document_type}]
            else:
                query = "SELECT * FROM c"
                parameters = None
            
            items = list(self.act_summary_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            return items
        except Exception as e:
            print(f"Error querying actSummary: {e}")
            return []
