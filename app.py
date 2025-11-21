from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from document_processor import DocumentProcessor
from azure_services import AzureServices
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize services
document_processor = DocumentProcessor()
azure_services = AzureServices()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Niyamr AI API is running"})

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """Extract text from the PDF"""
    try:
        data = request.get_json()
        blob_name = data.get('blob_name', 'ukpga_20250022_en.pdf')
        
        print(f"📄 Processing document: {blob_name}")
        
        # Process and index the document
        result = document_processor.process_and_index_document(blob_name)
        
        print(f"📊 Processing result: {result.get('success', False)}")
        if not result.get('success', False):
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        if result['success']:
            return jsonify({
                "success": True,
                "text": result['full_text'],
                "chunks_processed": result['chunks_processed'],
                "indexed": result.get('indexed', False)  # Use the indexed key from document processor
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/summarize', methods=['POST'])
def summarize_act():
    """Summarize the Act"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            # Try to get text from blob if not provided
            blob_name = data.get('blob_name', 'ukpga_20250022_en.pdf')
            pdf_content = azure_services.download_blob(blob_name)
            text = document_processor.extract_text_from_pdf(pdf_content)
        
        result = document_processor.summarize_act(text)
        
        if result['success']:
            return jsonify({
                "success": True,
                "summary": result['summary']
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/extract-sections', methods=['POST'])
def extract_sections():
    """Extract key legislative sections"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            # Try to get text from blob if not provided
            blob_name = data.get('blob_name', 'ukpga_20250022_en.pdf')
            pdf_content = azure_services.download_blob(blob_name)
            text = document_processor.extract_text_from_pdf(pdf_content)
        
        result = document_processor.extract_legislative_sections(text)
        
        if result['success']:
            return jsonify({
                "success": True,
                "sections": result['sections']
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/check-rules', methods=['POST'])
def check_rules():
    """Check the 6 rules against the Act"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            # Try to get text from blob if not provided
            blob_name = data.get('blob_name', 'ukpga_20250022_en.pdf')
            pdf_content = azure_services.download_blob(blob_name)
            text = document_processor.extract_text_from_pdf(pdf_content)
        
        results = document_processor.check_rules(text)
        
        return jsonify({
            "success": True,
            "rule_checks": results
        })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/search', methods=['POST'])
def search_documents():
    """Search documents using Azure Cognitive Search"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        search_type = data.get('type', 'text')  # 'text' or 'vector'
        top = data.get('top', 5)
        
        if search_type == 'vector':
            # Generate embedding for the query
            query_vector = azure_services.get_embedding(query)
            results = azure_services.vector_search(query_vector, top)
        else:
            results = azure_services.search_documents(query, top)
        
        return jsonify({
            "success": True,
            "results": results,
            "query": query,
            "search_type": search_type
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
