# Niyamr AI - Legislative Document Analyzer

A comprehensive AI-powered system for analyzing legislative documents using Azure services, built with Python, Streamlit, Flask, and LangChain.

## 🏗️ Architecture

- **Frontend**: Streamlit web application with 4 main pages
- **Backend**: Flask REST API
- **AI Services**: Azure OpenAI for text processing and embeddings
- **Search**: Azure Cognitive Search with vector embeddings
- **Storage**: Azure Blob Storage for document storage
- **Database**: Azure Cosmos DB for storing processed data

## 📋 Features

### 1. Text Extractor
- Extract full text from PDF documents stored in Azure Blob Storage
- Clean and structure extracted text
- Chunk text for better processing
- Generate vector embeddings and store in Azure Search and Cosmos DB

### 2. Act Summarizer
- Generate comprehensive summaries of legislative acts
- Focus on purpose, key definitions, eligibility, obligations, and enforcement
- 5-10 bullet point format for easy consumption

### 3. Key Legislative Section Extractor
- Extract structured sections from legislative documents
- Categories: Definitions, Obligations, Responsibilities, Eligibility, Payments, Penalties, Record-keeping
- Output in JSON format for easy integration

### 4. Rule Checker
- Apply 6 compliance rules to legislative documents
- Automated compliance checking with confidence scores
- Evidence-based results with specific section references

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Azure account with the following services configured:
  - Azure OpenAI
  - Azure Cognitive Search
  - Azure Cosmos DB
  - Azure Blob Storage

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   - Ensure your `.env` file contains all required Azure credentials
   - The file should include:
     - Azure Cosmos DB configuration
     - Azure Blob Storage connection string
     - Azure Cognitive Search credentials
     - Azure OpenAI API keys and endpoints

4. **Upload your PDF document**:
   - Upload `ukpga_20250022_en.pdf` to your Azure Blob Storage container named "files"

5. **Create Azure Search Index**:
   - Ensure the index "niyamr-ai-index" is created in your Azure Cognitive Search service
   - The index should support vector search with the following fields:
     - `id` (Edm.String, key)
     - `content` (Edm.String, searchable)
     - `content_vector` (Collection(Edm.Single), searchable, vector)
     - `source` (Edm.String, filterable)
     - `chunk_index` (Edm.Int32, filterable)
     - `timestamp` (Edm.DateTimeOffset, filterable)

## 🚀 Running the Application

### Option 1: Using the startup script (Recommended)
```bash
python run_app.py
```

This will automatically start both Flask backend and Streamlit frontend.

### Option 2: Manual startup

1. **Start Flask backend**:
   ```bash
   python app.py
   ```

2. **Start Streamlit frontend** (in a new terminal):
   ```bash
   streamlit run streamlit_app.py
   ```

### Access the Application
- **Streamlit UI**: http://localhost:8501
- **Flask API**: http://localhost:5000

## 📖 Usage Guide

### 1. Text Extraction
1. Navigate to the "Text Extractor" page
2. Ensure the PDF blob name is correct (default: `ukpga_20250022_en.pdf`)
3. Click "Extract Text" to process the document
4. The system will:
   - Download the PDF from Azure Blob Storage
   - Extract and clean the text
   - Create text chunks with embeddings
   - Store in Azure Search and Cosmos DB

### 2. Act Summarization
1. Go to the "Act Summarizer" page
2. Choose to use previously extracted text or specify a new document
3. Click "Generate Summary"
4. Review the generated bullet-point summary

### 3. Legislative Section Extraction
1. Visit the "Key Legislative Section Extractor" page
2. Select your text source
3. Click "Extract Sections"
4. Review the structured JSON output with all key sections

### 4. Rule Compliance Checking
1. Navigate to the "Rule Checker" page
2. Choose your text source
3. Click "Check Rules"
4. Review the compliance results for all 6 rules with confidence scores

## 🔧 API Endpoints

- `GET /api/health` - Health check
- `POST /api/extract-text` - Extract text from PDF
- `POST /api/summarize` - Generate act summary
- `POST /api/extract-sections` - Extract legislative sections
- `POST /api/check-rules` - Run rule compliance checks
- `POST /api/search` - Search documents (text or vector)

## 📁 Project Structure

```
Niyamr AI/
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── config.py              # Configuration management
├── azure_services.py      # Azure services integration
├── document_processor.py  # Document processing logic
├── app.py                 # Flask backend API
├── streamlit_app.py       # Streamlit frontend
├── run_app.py            # Startup script
├── README.md             # This file
└── ukpga_20250022_en.pdf # Source document
```

## 🔍 The 6 Compliance Rules

1. **Act must define key terms**
2. **Act must specify eligibility criteria**
3. **Act must specify responsibilities of the administering authority**
4. **Act must include enforcement or penalties**
5. **Act must include payment calculation or entitlement structure**
6. **Act must include record-keeping or reporting requirements**

## 🛡️ Security Notes

- All Azure credentials are stored in environment variables
- API keys are not exposed in the codebase
- Use HTTPS in production environments
- Regularly rotate API keys and access tokens

## 🐛 Troubleshooting

### Common Issues

1. **Connection errors**: Ensure all Azure services are properly configured and accessible
2. **API timeouts**: Large documents may take time to process; consider increasing timeout values
3. **Memory issues**: For very large documents, consider implementing streaming or batch processing
4. **Authentication errors**: Verify all API keys and endpoints in the `.env` file

### Logs and Debugging

- Flask runs in debug mode by default for development
- Check console output for detailed error messages
- Use the health check endpoint to verify API connectivity

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all Azure services are properly configured
3. Ensure all dependencies are installed correctly
4. Check that the PDF document is uploaded to the correct Azure Blob Storage container

## 🔄 Future Enhancements

- Batch processing for multiple documents
- Advanced search and filtering capabilities
- Export functionality for various formats
- Integration with additional AI models
- Enhanced error handling and logging
- Performance optimizations for large documents
