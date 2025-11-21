import streamlit as st
import requests
import json
from typing import Dict, Any

# Configure the page
st.set_page_config(
    page_title="Niyamr AI - Legislative Document Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:5000/api"

def make_api_request(endpoint: str, data: Dict = None) -> Dict[str, Any]:
    """Make API request to Flask backend"""
    try:
        if data:
            response = requests.post(f"{API_BASE_URL}/{endpoint}", json=data)
        else:
            response = requests.get(f"{API_BASE_URL}/{endpoint}")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"API Error: {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to API. Please ensure Flask backend is running."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    # Sidebar navigation
    st.sidebar.title("⚖️ Niyamr AI")
    st.sidebar.markdown("Legislative Document Analyzer")
    
    page = st.sidebar.selectbox(
        "Select Page",
        ["Text Extractor", "Act Summarizer", "Key Legislative Section Extractor", "Rule Checker"]
    )
    
    # Main content area
    if page == "Text Extractor":
        text_extractor_page()
    elif page == "Act Summarizer":
        act_summarizer_page()
    elif page == "Key Legislative Section Extractor":
        legislative_sections_page()
    elif page == "Rule Checker":
        rule_checker_page()

def text_extractor_page():
    """Text Extractor Page"""
    st.title("📄 Text Extractor")
    st.markdown("Extract full text from the Universal Credit Act 2025 PDF")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Configuration")
        blob_name = st.text_input("PDF Blob Name", value="ukpga_20250022_en.pdf")
        
        if st.button("Extract Text", type="primary"):
            with st.spinner("Extracting text from PDF..."):
                result = make_api_request("extract-text", {"blob_name": blob_name})
                
                if result.get("success"):
                    st.session_state.extracted_text = result.get("text", "")
                    st.session_state.chunks_processed = result.get("chunks_processed", 0)
                    st.session_state.indexed = result.get("indexed", False)
                    st.success("Text extracted successfully!")
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")
    
    with col2:
        st.subheader("Extracted Text")
        
        if hasattr(st.session_state, 'extracted_text'):
            # Show extraction stats
            col2a, col2b, col2c = st.columns(3)
            with col2a:
                st.metric("Text Length", f"{len(st.session_state.extracted_text):,} chars")
            with col2b:
                st.metric("Chunks Processed", st.session_state.chunks_processed)
            with col2c:
                indexed_status = "✅ Yes" if st.session_state.indexed else "❌ No"
                st.metric("Indexed", indexed_status)
            
            # Show text content
            st.text_area(
                "Full Text Content",
                value=st.session_state.extracted_text,
                height=400,
                disabled=True
            )
            
            # Download button
            st.download_button(
                label="Download Text",
                data=st.session_state.extracted_text,
                file_name="extracted_text.txt",
                mime="text/plain"
            )
        else:
            st.info("Click 'Extract Text' to begin extraction process.")

def act_summarizer_page():
    """Act Summarizer Page"""
    st.title("📋 Act Summarizer")
    st.markdown("Generate a comprehensive summary of the Universal Credit Act 2025")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Options")
        
        use_extracted = st.checkbox("Use previously extracted text", value=True)
        
        if not use_extracted:
            blob_name = st.text_input("PDF Blob Name", value="ukpga_20250022_en.pdf")
        
        if st.button("Generate Summary", type="primary"):
            with st.spinner("Generating summary..."):
                data = {}
                if use_extracted and hasattr(st.session_state, 'extracted_text'):
                    data["text"] = st.session_state.extracted_text
                elif not use_extracted:
                    data["blob_name"] = blob_name
                
                result = make_api_request("summarize", data)
                
                if result.get("success"):
                    st.session_state.summary = result.get("summary", "")
                    st.success("Summary generated successfully!")
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")
    
    with col2:
        st.subheader("Act Summary")
        
        if hasattr(st.session_state, 'summary'):
            st.markdown(st.session_state.summary)
            
            # Download button
            st.download_button(
                label="Download Summary",
                data=st.session_state.summary,
                file_name="act_summary.md",
                mime="text/markdown"
            )
        else:
            st.info("Click 'Generate Summary' to create a summary of the Act.")
            
            # Show expected format
            st.markdown("""
            **Expected Summary Format:**
            - Purpose of the Act
            - Key definitions
            - Eligibility criteria
            - Obligations and responsibilities
            - Enforcement elements
            """)

def legislative_sections_page():
    """Key Legislative Section Extractor Page"""
    st.title("🏛️ Key Legislative Section Extractor")
    st.markdown("Extract structured legislative sections from the Act")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Options")
        
        use_extracted = st.checkbox("Use previously extracted text", value=True)
        
        if not use_extracted:
            blob_name = st.text_input("PDF Blob Name", value="ukpga_20250022_en.pdf")
        
        if st.button("Extract Sections", type="primary"):
            with st.spinner("Extracting legislative sections..."):
                data = {}
                if use_extracted and hasattr(st.session_state, 'extracted_text'):
                    data["text"] = st.session_state.extracted_text
                elif not use_extracted:
                    data["blob_name"] = blob_name
                
                result = make_api_request("extract-sections", data)
                
                if result.get("success"):
                    st.session_state.sections = result.get("sections", {})
                    st.success("Sections extracted successfully!")
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")
    
    with col2:
        st.subheader("Legislative Sections")
        
        if hasattr(st.session_state, 'sections'):
            sections = st.session_state.sections
            
            # Display sections in tabs
            if isinstance(sections, dict) and len(sections) > 1:
                tabs = st.tabs(list(sections.keys()))
                
                for i, (key, value) in enumerate(sections.items()):
                    with tabs[i]:
                        st.markdown(f"**{key.replace('_', ' ').title()}**")
                        st.write(value)
            else:
                st.json(sections)
            
            # Download button
            st.download_button(
                label="Download Sections (JSON)",
                data=json.dumps(sections, indent=2),
                file_name="legislative_sections.json",
                mime="application/json"
            )
        else:
            st.info("Click 'Extract Sections' to extract key legislative sections.")
            
            # Show expected format
            st.markdown("""
            **Expected Sections:**
            - **Definitions**: Key terms and their meanings
            - **Obligations**: Legal obligations imposed by the Act
            - **Responsibilities**: Assigned responsibilities
            - **Eligibility**: Criteria for eligibility
            - **Payments**: Payment structures and entitlements
            - **Penalties**: Enforcement and penalty provisions
            - **Record Keeping**: Reporting and record-keeping requirements
            """)

def rule_checker_page():
    """Rule Checker Page"""
    st.title("✅ Rule Checker")
    st.markdown("Apply compliance checks against the 6 legislative rules")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Options")
        
        use_extracted = st.checkbox("Use previously extracted text", value=True)
        
        if not use_extracted:
            blob_name = st.text_input("PDF Blob Name", value="ukpga_20250022_en.pdf")
        
        if st.button("Check Rules", type="primary"):
            with st.spinner("Checking compliance rules..."):
                data = {}
                if use_extracted and hasattr(st.session_state, 'extracted_text'):
                    data["text"] = st.session_state.extracted_text
                elif not use_extracted:
                    data["blob_name"] = blob_name
                
                result = make_api_request("check-rules", data)
                
                if result.get("success"):
                    st.session_state.rule_checks = result.get("rule_checks", [])
                    st.success("Rule checks completed!")
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")
        
        # Show rules being checked
        st.subheader("Rules Being Checked")
        rules = [
            "Act must define key terms",
            "Act must specify eligibility criteria",
            "Act must specify responsibilities of the administering authority",
            "Act must include enforcement or penalties",
            "Act must include payment calculation or entitlement structure",
            "Act must include record-keeping or reporting requirements"
        ]
        
        for i, rule in enumerate(rules, 1):
            st.write(f"{i}. {rule}")
    
    with col2:
        st.subheader("Rule Check Results")
        
        if hasattr(st.session_state, 'rule_checks'):
            rule_checks = st.session_state.rule_checks
            
            # Summary metrics
            total_rules = len(rule_checks)
            passed_rules = sum(1 for check in rule_checks if check.get('status') == 'pass')
            avg_confidence = sum(check.get('confidence', 0) for check in rule_checks) / total_rules if total_rules > 0 else 0
            
            col2a, col2b, col2c = st.columns(3)
            with col2a:
                st.metric("Total Rules", total_rules)
            with col2b:
                st.metric("Passed", f"{passed_rules}/{total_rules}")
            with col2c:
                st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
            
            # Detailed results
            for i, check in enumerate(rule_checks):
                status = check.get('status', 'unknown')
                confidence = check.get('confidence', 0)
                
                # Status indicator
                if status == 'pass':
                    status_icon = "✅"
                    status_color = "green"
                elif status == 'fail':
                    status_icon = "❌"
                    status_color = "red"
                else:
                    status_icon = "❓"
                    status_color = "orange"
                
                with st.expander(f"{status_icon} Rule {i+1}: {check.get('rule', 'Unknown rule')} (Confidence: {confidence}%)"):
                    st.markdown(f"**Status:** :{status_color}[{status.upper()}]")
                    st.markdown(f"**Confidence:** {confidence}%")
                    st.markdown(f"**Evidence:**")
                    st.write(check.get('evidence', 'No evidence provided'))
            
            # Download button
            st.download_button(
                label="Download Rule Check Results (JSON)",
                data=json.dumps(rule_checks, indent=2),
                file_name="rule_check_results.json",
                mime="application/json"
            )
        else:
            st.info("Click 'Check Rules' to run compliance checks.")

if __name__ == "__main__":
    main()
