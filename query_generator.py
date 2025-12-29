from openai import OpenAI
import json
from typing import Dict, Any, Optional

class QueryGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.conversation_history = []
        
    def generate_response(self, user_input: str) -> Dict[Any, Any]:
        # Add user input to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # First, assess if we need a database query
        assessment_message = """You are a helpful assistant with access to a trading database. 
        First, determine if the user's question requires querying the database or if it's a general conversation.
        For general conversation (like greetings, how are you, etc.), respond naturally without querying.
        For data-related questions, generate an appropriate SQL query.

        Return a JSON response with the following structure:
        {
            "needs_query": boolean,
            "response": string (for general conversation),
            "query": string (SQL query if needed),
            "explanation": string (explanation of the query or results)
        }
        
        Available database tables:
        - user_profiles (user_id, name, email, registration_date, last_login, wallet_balance, account_status, created_at)
        - trades_real (trade_id, user_id, symbol, trade_type, amount, price, trade_date, status)
        - trades_demo (trade_id, user_id, symbol, trade_type, amount, price, trade_date, status)

        Examples:
        1. User: "Hey, how are you?"
           Response: {"needs_query": false, "response": "Hello! I'm doing well, thank you for asking. How can I help you with your trading data today?"}
        
        2. User: "Show me inactive users with balance > $50"
           Response: {"needs_query": true, "query": "SELECT * FROM user_profiles WHERE account_status = 'inactive' AND wallet_balance > 50", "explanation": "Here are the inactive users with wallet balance greater than $50"}
        
        Note: Use PostgreSQL syntax for queries. For date operations use CURRENT_DATE and INTERVAL syntax.
        """
        
        try:
            messages = [
                {"role": "system", "content": assessment_message},
                *self.conversation_history
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"AI Response: {result}")  # Debug print
            
            # Validate response structure
            if not isinstance(result.get("needs_query"), bool):
                raise ValueError("Invalid response structure: missing or invalid 'needs_query' field")
            
            # Add assistant's response to conversation history
            if result.get("needs_query"):
                if not result.get("query"):
                    raise ValueError("Query required but not provided")
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": f"Let me query the database for that information.\nQuery: {result.get('query')}\nExplanation: {result.get('explanation', 'Processing your request...')}"
                })
            else:
                if not result.get("response"):
                    raise ValueError("Response required but not provided")
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": result.get('response')
                })
            
            return result
            
        except json.JSONDecodeError as e:
            error_response = {
                "needs_query": False,
                "response": "I apologize, but I encountered an error processing your request. Please try again."
            }
            print(f"JSON decode error: {e}")
            return error_response
            
        except Exception as e:
            error_response = {
                "needs_query": False,
                "response": "I apologize, but something went wrong. Please try again or rephrase your question."
            }
            print(f"Error generating response: {e}")
            return error_response

    def format_response(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Format the final response including any data from the database"""
        if not data:

            return {
                "explanation": self.conversation_history[-1]["content"],
                "data": None
            }
        return {
            "explanation": data.get("explanation", "Here's what I found:"),
            "query": data.get("query"),
            "data": data.get("data")
        } 