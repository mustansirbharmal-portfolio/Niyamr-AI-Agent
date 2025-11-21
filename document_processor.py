import PyPDF2
import pdfplumber
import re
import json
from typing import Dict, List, Any
from azure_services import AzureServices
import uuid
from datetime import datetime

class DocumentProcessor:
    def __init__(self):
        self.azure_services = AzureServices()
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF using pdfplumber for better formatting"""
        try:
            import io
            text = ""
            
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            
            # Clean up the text
            text = self._clean_text(text)
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and structure the extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Fix common PDF extraction issues
        text = text.replace('\x00', '')
        text = text.strip()
        
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better context preservation"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def _analyze_chunk_content(self, chunk: str) -> Dict[str, str]:
        """Analyze chunk content to extract relevant legislative information"""
        try:
            # Quick keyword-based analysis for efficiency
            analysis = {
                "purpose": "",
                "definitions": "",
                "eligibility": "",
                "obligations": "",
                "responsibilities": "",
                "payments": "",
                "penalties": "",
                "enforcement": "",
                "record_keeping": "",
                "rules": ""
            }
            
            chunk_lower = chunk.lower()
            
            # Check for definitions
            if any(word in chunk_lower for word in ["means", "definition", "interpret", "shall mean"]):
                analysis["definitions"] = chunk[:200] + "..." if len(chunk) > 200 else chunk
            
            # Check for eligibility criteria
            if any(word in chunk_lower for word in ["eligible", "qualification", "entitled", "qualify"]):
                analysis["eligibility"] = chunk[:200] + "..." if len(chunk) > 200 else chunk
            
            # Check for obligations
            if any(word in chunk_lower for word in ["shall", "must", "obligation", "duty", "required"]):
                analysis["obligations"] = chunk[:200] + "..." if len(chunk) > 200 else chunk
            
            # Check for responsibilities
            if any(word in chunk_lower for word in ["responsible", "responsibility", "authority", "administer"]):
                analysis["responsibilities"] = chunk[:200] + "..." if len(chunk) > 200 else chunk
            
            # Check for payments
            if any(word in chunk_lower for word in ["payment", "benefit", "amount", "entitlement", "credit"]):
                analysis["payments"] = chunk[:200] + "..." if len(chunk) > 200 else chunk
            
            # Check for penalties
            if any(word in chunk_lower for word in ["penalty", "fine", "sanction", "offence", "prosecution"]):
                analysis["penalties"] = chunk[:200] + "..." if len(chunk) > 200 else chunk
                analysis["enforcement"] = chunk[:200] + "..." if len(chunk) > 200 else chunk
            
            # Check for record keeping
            if any(word in chunk_lower for word in ["record", "report", "information", "data", "maintain"]):
                analysis["record_keeping"] = chunk[:200] + "..." if len(chunk) > 200 else chunk
            
            # Set purpose based on content
            if analysis["definitions"]:
                analysis["purpose"] = "Definitions section"
            elif analysis["eligibility"]:
                analysis["purpose"] = "Eligibility criteria"
            elif analysis["payments"]:
                analysis["purpose"] = "Payment and entitlements"
            elif analysis["penalties"]:
                analysis["purpose"] = "Enforcement and penalties"
            else:
                analysis["purpose"] = "General legislative content"
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing chunk: {e}")
            return {
                "purpose": "Legislative content",
                "definitions": "",
                "eligibility": "",
                "obligations": "",
                "responsibilities": "",
                "payments": "",
                "penalties": "",
                "enforcement": "",
                "record_keeping": "",
                "rules": ""
            }
    
    def process_and_index_document(self, blob_name: str) -> Dict[str, Any]:
        """Download PDF from blob storage, extract text, and index it"""
        try:
            # Download PDF from blob storage
            pdf_content = self.azure_services.download_blob(blob_name)
            if not pdf_content:
                return {"success": False, "error": "Failed to download PDF"}
            
            # Extract text
            full_text = self.extract_text_from_pdf(pdf_content)
            if not full_text:
                return {"success": False, "error": "Failed to extract text from PDF"}
            
            # Chunk the text
            chunks = self.chunk_text(full_text)
            
            # Process each chunk
            indexed_chunks = []
            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self.azure_services.get_embedding(chunk)
                
                # Analyze chunk content for better indexing
                chunk_analysis = self._analyze_chunk_content(chunk)
                
                # Create document for search index - matching your existing index schema
                # Remove invalid characters from blob_name (dots, spaces, etc.)
                clean_blob_name = blob_name.replace('.pdf', '').replace('.', '_').replace(' ', '_')
                doc_id = f"{clean_blob_name}_chunk_{i}"
                search_doc = {
                    "id": doc_id,
                    "content": chunk,
                    "content_vector": embedding,
                    "purpose": chunk_analysis.get("purpose", f"Legislative document chunk from {blob_name}"),
                    "key_definitions": chunk_analysis.get("definitions", ""),
                    "eligibility": chunk_analysis.get("eligibility", ""),
                    "obligations": chunk_analysis.get("obligations", ""),
                    "enforcement_elements": chunk_analysis.get("enforcement", ""),  # Fixed: plural form
                    "legislative_section_definition": chunk_analysis.get("definitions", ""),  # Fixed: singular form
                    "legislative_obligations": chunk_analysis.get("obligations", ""),
                    "legislative_responsibilities": chunk_analysis.get("responsibilities", ""),
                    "legislative_eligibility": chunk_analysis.get("eligibility", ""),
                    "legislative_payments": chunk_analysis.get("payments", ""),
                    "legislative_penalties": chunk_analysis.get("penalties", ""),
                    "legislative_record_keeping": chunk_analysis.get("record_keeping", ""),
                    "rules": chunk_analysis.get("rules", f"Chunk {i} from {blob_name}")
                }
                
                # Store in Cosmos DB
                cosmos_doc = {
                    "id": doc_id,
                    "content": chunk,
                    "embedding": embedding,
                    "source": blob_name,
                    "chunk_index": i,
                    "timestamp": datetime.utcnow().isoformat(),
                    "full_text_length": len(full_text),
                    "chunk_count": len(chunks)
                }
                
                indexed_chunks.append({
                    "search_doc": search_doc,
                    "cosmos_doc": cosmos_doc
                })
            
            # Upload to search index in smaller batches to avoid timeouts
            search_success = True
            batch_size = 10
            
            print(f"Uploading {len(indexed_chunks)} documents in batches of {batch_size}...")
            
            for i in range(0, len(indexed_chunks), batch_size):
                batch = indexed_chunks[i:i + batch_size]
                search_docs = [chunk["search_doc"] for chunk in batch]
                
                try:
                    batch_success = self.azure_services.upload_to_search_index(search_docs)
                    if not batch_success:
                        print(f"❌ Batch {i//batch_size + 1} failed")
                        search_success = False
                    else:
                        print(f"✅ Batch {i//batch_size + 1} uploaded successfully")
                except Exception as e:
                    print(f"❌ Batch {i//batch_size + 1} error: {e}")
                    search_success = False
            
            # Store in Cosmos DB with better error handling
            cosmos_success = True
            print(f"Storing {len(indexed_chunks)} documents in Cosmos DB...")
            
            for i, chunk in enumerate(indexed_chunks):
                try:
                    if not self.azure_services.store_in_cosmos(chunk["cosmos_doc"]):
                        print(f"❌ Cosmos DB storage failed for chunk {i}")
                        cosmos_success = False
                except Exception as e:
                    print(f"❌ Cosmos DB error for chunk {i}: {e}")
                    cosmos_success = False
            
            # Store extracted text in actSummary container
            extracted_text_data = {
                "source_document": blob_name,
                "extracted_text": full_text,
                "text_length": len(full_text),
                "chunks_count": len(chunks),
                "extraction_method": "pdfplumber",
                "embedding": self.azure_services.get_embedding(full_text[:2000])  # First 2000 chars for embedding
            }
            
            self.azure_services.store_act_summary("extracted_text", extracted_text_data)
            
            return {
                "success": True,
                "full_text": full_text,
                "chunks_processed": len(chunks),
                "indexed": search_success and cosmos_success
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def summarize_act(self, text: str) -> Dict[str, Any]:
        """Summarize the Act in 5-10 bullet points"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert legal analyst. Summarize the given Act in 5-10 bullet points focusing on: Purpose, Key definitions, Eligibility, Obligations, and Enforcement elements."
                },
                {
                    "role": "user",
                    "content": f"Please summarize this Act:\n\n{text[:8000]}"  # Limit text length
                }
            ]
            
            summary = self.azure_services.chat_completion(messages, temperature=0.3)
            
            # Store summary in actSummary container
            summary_data = {
                "summary_text": summary,
                "original_text_length": len(text),
                "summary_method": "AI_bullet_points",
                "embedding": self.azure_services.get_embedding(summary)
            }
            self.azure_services.store_act_summary("act_summary", summary_data)
            
            return {"success": True, "summary": summary}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_legislative_sections(self, text: str) -> Dict[str, Any]:
        """Extract key legislative sections in JSON format"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert legal analyst. Extract the following sections from the given Act and return them in JSON format:
                    - definitions
                    - obligations
                    - responsibilities
                    - eligibility
                    - payments (entitlements)
                    - penalties (enforcement)
                    - record_keeping (reporting)
                    
                    Return only valid JSON with these exact keys."""
                },
                {
                    "role": "user",
                    "content": f"Extract legislative sections from this Act:\n\n{text[:8000]}"
                }
            ]
            
            response = self.azure_services.chat_completion(messages, temperature=0.2)
            
            # Try to parse as JSON
            try:
                sections = json.loads(response)
                
                # Store legislative sections in actSummary container
                sections_data = {
                    "legislative_sections": sections,
                    "extraction_method": "AI_JSON_extraction",
                    "original_text_length": len(text),
                    "embedding": self.azure_services.get_embedding(str(sections))
                }
                self.azure_services.store_act_summary("legislative_sections", sections_data)
                
                return {"success": True, "sections": sections}
            except json.JSONDecodeError:
                # If not valid JSON, return as text
                sections_data = {
                    "legislative_sections": {"raw_response": response},
                    "extraction_method": "AI_text_extraction",
                    "original_text_length": len(text),
                    "embedding": self.azure_services.get_embedding(response)
                }
                self.azure_services.store_act_summary("legislative_sections", sections_data)
                
                return {"success": True, "sections": {"raw_response": response}}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_rules(self, text: str) -> List[Dict[str, Any]]:
        """Apply the 6 rule checks to the Act"""
        rules = [
            "Act must define key terms",
            "Act must specify eligibility criteria", 
            "Act must specify responsibilities of the administering authority",
            "Act must include enforcement or penalties",
            "Act must include payment calculation or entitlement structure",
            "Act must include record-keeping or reporting requirements"
        ]
        
        results = []
        
        for rule in rules:
            try:
                messages = [
                    {
                        "role": "system",
                        "content": f"""You are an expert legal compliance checker. Check if the given Act satisfies this rule: "{rule}"
                        
                        Respond with a JSON object containing:
                        - rule: the rule being checked
                        - status: "pass" or "fail"
                        - evidence: specific section or text that supports your decision
                        - confidence: confidence score from 0-100
                        
                        Be thorough and accurate in your analysis."""
                    },
                    {
                        "role": "user",
                        "content": f"Check this rule against the Act:\n\nRule: {rule}\n\nAct text:\n{text[:6000]}"
                    }
                ]
                
                response = self.azure_services.chat_completion(messages, temperature=0.1)
                
                try:
                    # Try to parse as JSON first
                    rule_result = json.loads(response)
                    
                    # Apply confidence-based pass rule: if confidence >= 90%, mark as pass
                    if rule_result.get('confidence', 0) >= 90:
                        rule_result['status'] = 'pass'
                    
                    results.append(rule_result)
                except json.JSONDecodeError:
                    # Try to extract JSON from the response if it's embedded in text
                    try:
                        import re
                        # Look for JSON pattern in the response
                        json_match = re.search(r'\{.*\}', response, re.DOTALL)
                        if json_match:
                            json_str = json_match.group()
                            rule_result = json.loads(json_str)
                            
                            # Apply confidence-based pass rule: if confidence >= 90%, mark as pass
                            if rule_result.get('confidence', 0) >= 90:
                                rule_result['status'] = 'pass'
                            
                            results.append(rule_result)
                        else:
                            # If no JSON found, create a structured response from the text
                            # Try to extract status and confidence from text
                            status = "unknown"
                            confidence = 0
                            
                            if "pass" in response.lower():
                                status = "pass"
                            elif "fail" in response.lower():
                                status = "fail"
                            
                            # Try to extract confidence number
                            conf_match = re.search(r'confidence["\s:]*(\d+)', response, re.IGNORECASE)
                            if conf_match:
                                confidence = int(conf_match.group(1))
                            
                            # Apply confidence-based pass rule: if confidence >= 90%, mark as pass
                            if confidence >= 90:
                                status = 'pass'
                            
                            results.append({
                                "rule": rule,
                                "status": status,
                                "evidence": response,
                                "confidence": confidence
                            })
                    except Exception:
                        # Final fallback
                        results.append({
                            "rule": rule,
                            "status": "unknown",
                            "evidence": response,
                            "confidence": 0
                        })
                    
            except Exception as e:
                results.append({
                    "rule": rule,
                    "status": "error",
                    "evidence": str(e),
                    "confidence": 0
                })
        
        # Store rule check results in actSummary container
        rule_check_data = {
            "rule_check_results": results,
            "total_rules": len(rules),
            "passed_rules": sum(1 for r in results if r.get('status') == 'pass'),
            "average_confidence": sum(r.get('confidence', 0) for r in results) / len(results) if results else 0,
            "original_text_length": len(text),
            "embedding": self.azure_services.get_embedding(str(results))
        }
        self.azure_services.store_act_summary("rule_checker", rule_check_data)
        
        return results
