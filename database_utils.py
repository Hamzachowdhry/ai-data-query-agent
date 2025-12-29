import psycopg2
from psycopg2 import Error
import pandas as pd
from typing import Optional

class DatabaseConnection:
    def __init__(self, host: str, user: str, password: str, database: str, port: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
    
    def connect(self):
        try:
            if self.connection and not self.connection.closed:
                return True
                
            print("Attempting to establish database connection...")
            # Try first with verify-full
            try:
                self.connection = psycopg2.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port,
                    sslmode='verify-full',
                    connect_timeout=30,
                    application_name='data_bot'
                )
            except:
                # If verify-full fails, try with require
                self.connection = psycopg2.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port,
                    sslmode='require',
                    connect_timeout=30,
                    application_name='data_bot'
                )
            
            self.connection.autocommit = True
            print("Database connection established successfully")
            return True
            
        except psycopg2.OperationalError as e:
            print(f"Database connection error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error while connecting: {e}")
            return False
    
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        try:
            if not self.connection or self.connection.closed:
                if not self.connect():
                    return None
            
            print(f"Executing query: {query[:100]}...")  # Print first 100 chars of query
            df = pd.read_sql_query(query, self.connection)
            print("Query executed successfully")
            return df
            
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during query execution: {e}")
            return None
        
    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close() 