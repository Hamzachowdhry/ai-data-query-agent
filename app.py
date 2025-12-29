import streamlit as st
import pandas as pd
from database_utils import DatabaseConnection
from query_generator import QueryGenerator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize database connection
db = DatabaseConnection(
    host='spotii-production-uae-flex.postgres.database.azure.com',
    user='analytics',
    password="wkYhGWq7ANE64MAj%",
    database='hydra',
    port='5432'  # Note: port should be string for consistency
)

# Test connection immediately
if not db.connect():
    st.error("Failed to connect to database. Please check your connection settings.")

# Initialize query generator
query_generator = QueryGenerator(api_key=os.getenv('OPENAI_API_KEY'))

def main():
    st.title("Deriv Data Bot")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "data" in message:
                st.dataframe(message["data"])
                
                # Download button for data
                if isinstance(message["data"], pd.DataFrame) and not message["data"].empty:
                    csv = message["data"].to_csv(index=False)
                    st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name="data.csv",
                        mime="text/csv"
                    )
    
    # User input
    if prompt := st.chat_input("Ask me anything about the trading data..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Generate response
        response = query_generator.generate_response(prompt)
        
        # Execute query if present and needed
        if response.get("needs_query", False) and response.get("query"):
            data = db.execute_query(response["query"])
            response["data"] = data
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response.get("explanation", response.get("response", "Here's what I found:")),
            "data": response.get("data", None) if response.get("needs_query", False) else None
        })
        
        # Rerun to update the chat interface
        st.rerun()

if __name__ == "__main__":
    main() 