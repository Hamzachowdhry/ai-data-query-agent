import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv
import names  # pip install names
import urllib.parse  # Add this for URL encoding

# Load environment variables
load_dotenv()

# Create connection string with properly encoded password
password = urllib.parse.quote_plus("wkYhGWq7ANE64MAj%")  # URL encode the password
conn_string = (
    f"postgresql://analytics:{password}@"
    "spotii-production-uae-flex.postgres.database.azure.com:5432/hydra"
    "?sslmode=prefer&application_name=data_generator"
)

def create_tables(conn, cursor):
    try:
        # Create ENUM types if they don't exist
        types_sql = """
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'account_status') THEN
                CREATE TYPE account_status AS ENUM ('active', 'inactive', 'suspended');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'trade_type') THEN
                CREATE TYPE trade_type AS ENUM ('buy', 'sell');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'trade_status') THEN
                CREATE TYPE trade_status AS ENUM ('completed', 'cancelled', 'pending');
            END IF;
        END $$;
        """
        
        cursor.execute(types_sql)
        
        # Create tables if they don't exist
        tables_sql = """
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            registration_date TIMESTAMP,
            last_login TIMESTAMP,
            wallet_balance DECIMAL(15, 2),
            account_status account_status,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS trades_real (
            trade_id SERIAL PRIMARY KEY,
            user_id INTEGER,
            symbol VARCHAR(20),
            trade_type trade_type,
            amount DECIMAL(15, 2),
            price DECIMAL(15, 2),
            trade_date TIMESTAMP,
            status trade_status,
            FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
        );

        CREATE TABLE IF NOT EXISTS trades_demo (
            trade_id SERIAL PRIMARY KEY,
            user_id INTEGER,
            symbol VARCHAR(20),
            trade_type trade_type,
            amount DECIMAL(15, 2),
            price DECIMAL(15, 2),
            trade_date TIMESTAMP,
            status trade_status,
            FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
        );
        """
        
        cursor.execute(tables_sql)
        conn.commit()
        print("Tables created successfully")
    except psycopg2.Error as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
        raise

def generate_dummy_data(conn, cursor):
    # Sample data
    symbols = ['BTC/USD', 'ETH/USD', 'EUR/USD', 'GBP/USD', 'JPY/USD', 'AUD/USD']
    statuses = ['active', 'inactive', 'suspended']
    trade_statuses = ['completed', 'cancelled', 'pending']
    
    try:
        # Generate 100 users
        for i in range(100):
            name = names.get_full_name()
            email = f"{name.lower().replace(' ', '.')}@example.com"
            reg_date = datetime.now() - timedelta(days=random.randint(1, 365))
            last_login = reg_date + timedelta(days=random.randint(0, (datetime.now() - reg_date).days))
            wallet_balance = round(random.uniform(0, 10000), 2)
            account_status = random.choice(statuses)
            
            try:
                cursor.execute("""
                    INSERT INTO user_profiles (name, email, registration_date, last_login, wallet_balance, account_status)
                    VALUES (%s, %s, %s, %s, %s, %s::account_status)
                    RETURNING user_id
                    """, (name, email, reg_date, last_login, wallet_balance, account_status))
                user_id = cursor.fetchone()[0]
                
                # Generate trades for this user immediately after creation
                # Generate 5-20 real trades
                num_real_trades = random.randint(5, 20)
                for _ in range(num_real_trades):
                    symbol = random.choice(symbols)
                    trade_type = random.choice(['buy', 'sell'])
                    amount = round(random.uniform(0.1, 5), 2)
                    price = round(random.uniform(100, 50000), 2)
                    trade_date = datetime.now() - timedelta(days=random.randint(1, 180))
                    status = random.choice(trade_statuses)
                    
                    cursor.execute("""
                        INSERT INTO trades_real (user_id, symbol, trade_type, amount, price, trade_date, status)
                        VALUES (%s, %s, %s::trade_type, %s, %s, %s, %s::trade_status)
                        """, (user_id, symbol, trade_type, amount, price, trade_date, status))
                
                # Generate 10-30 demo trades
                num_demo_trades = random.randint(10, 30)
                for _ in range(num_demo_trades):
                    symbol = random.choice(symbols)
                    trade_type = random.choice(['buy', 'sell'])
                    amount = round(random.uniform(0.1, 10), 2)
                    price = round(random.uniform(100, 50000), 2)
                    trade_date = datetime.now() - timedelta(days=random.randint(1, 180))
                    status = random.choice(trade_statuses)
                    
                    cursor.execute("""
                        INSERT INTO trades_demo (user_id, symbol, trade_type, amount, price, trade_date, status)
                        VALUES (%s, %s, %s::trade_type, %s, %s, %s, %s::trade_status)
                        """, (user_id, symbol, trade_type, amount, price, trade_date, status))
                
                # Commit after each user and their trades
                conn.commit()
                print(f"Successfully created user {name} with ID {user_id} and their trades")
                
            except psycopg2.Error as e:
                print(f"Error inserting user {name}: {e}")
                conn.rollback()  # Rollback on error
                continue
        
        print("Dummy data generation completed!")
        
    except Exception as e:
        print(f"Error during dummy data generation: {e}")
        conn.rollback()
        raise  # Re-raise the exception to be caught by the main function

def main():
    conn = None
    cursor = None
    try:
        print("Attempting to connect to database...")
        conn = psycopg2.connect(conn_string)
        
        print("Creating cursor...")
        cursor = conn.cursor()
        
        print("Creating tables...")
        create_tables(conn, cursor)
        
        # Check if any of the tables are empty
        cursor.execute("SELECT COUNT(*) FROM user_profiles")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM trades_real")
        real_trades_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM trades_demo")
        demo_trades_count = cursor.fetchone()[0]
        
        if user_count == 0 or real_trades_count == 0 or demo_trades_count == 0:
            print("One or more tables are empty. Generating dummy data...")
            generate_dummy_data(conn, cursor)
            print("Dummy data generated successfully!")
        else:
            print("All tables contain data. Skipping dummy data generation.")
        
        # Print some statistics
        cursor.execute("SELECT COUNT(*) FROM user_profiles")
        print(f"Total users: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM trades_real")
        print(f"Total real trades: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM trades_demo")
        print(f"Total demo trades: {cursor.fetchone()[0]}")
        
    except psycopg2.OperationalError as e:
        print(f"Connection Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main() 