import os
import sys
import json
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

MAINNET_PORTS = [':8453', ':100', ':2043']

def is_mainnet(blockchain_name):
    return any(blockchain_name.endswith(port) for port in MAINNET_PORTS)

def get_db_connection(mainnet=False):
    host = os.getenv('DB_HOST_PUBLISH_MAINNET') if mainnet else os.getenv('DB_HOST_PUBLISH_TESTNET')
    return psycopg2.connect(
        host=host,
        user=os.getenv('DB_USER_PUBLISH'),
        password=os.getenv('DB_PASSWORD_PUBLISH'),
        dbname=os.getenv('DB_NAME_PUBLISH'),
        port=5432
    )

files = sys.argv[1:]

for file in files:
    print(f"📁 Processing error file: {file}")
    try:
        with open(file, 'r') as f:
            error_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read or parse {file}: {e}")
        continue

    # Handle both old and new format
    if isinstance(error_data, dict) and 'blockchain_name' in error_data:
        # New format with blockchain information
        blockchain_name = error_data.get('blockchain_name', '')
        node_name = error_data.get('node_name', '')
        errors = error_data.get('errors', {})
    else:
        # Old format - try to determine from filename
        errors = error_data
        node_name = file.split('errors_')[1].replace('_', ' ').replace('.json', '').strip()
        blockchain_name = ''  # Will be determined by network config

    mainnet = is_mainnet(blockchain_name)
    table_name = 'error_messages_mainnet_py' if mainnet else 'error_messages_testnet_py'

    try:
        conn = get_db_connection(mainnet)
        cursor = conn.cursor()
        print(f"✅ Connected to DB ({'mainnet' if mainnet else 'testnet'})")
    except Exception as e:
        print(f"❌ Failed to connect to DB: {e}")
        continue

    for attempt_key, attempt_data in errors.items():
        # Handle both old and new error formats
        if isinstance(attempt_data, dict) and 'ka_label' in attempt_data:
            # New format with structured error data per attempt
            ka_label = attempt_data.get('ka_label', 'Unknown KA')
            attempt_number = attempt_data.get('attempt', 1)
            publish_error = attempt_data.get('publish_error')
            query_error = attempt_data.get('query_error')
            publisher_get_error = attempt_data.get('publisher_get_error')
            non_publisher_get_error = attempt_data.get('non_publisher_get_error')
            time_stamp = attempt_data.get('time_stamp')
            
            # Only insert if there's at least one error
            if any([publish_error, query_error, publisher_get_error, non_publisher_get_error]):
                row = {
                    'node_name': node_name,
                    'blockchain_id': blockchain_name,
                    'ka_label': ka_label,
                    'publish_error': publish_error,
                    'query_error': query_error,
                    'publisher_get_error': publisher_get_error,
                    'non_publisher_get_error': non_publisher_get_error,
                    'time_stamp': time_stamp,
                }

                insert_query = sql.SQL(f"""
                    INSERT INTO {sql.Identifier(table_name).string} (
                        node_name, blockchain_id, ka_label,
                        publish_error, query_error,
                        publisher_get_error, non_publisher_get_error,
                        time_stamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """)

                try:
                    cursor.execute(insert_query, (
                        row['node_name'], row['blockchain_id'], row['ka_label'],
                        row['publish_error'], row['query_error'],
                        row['publisher_get_error'], row['non_publisher_get_error'],
                        row['time_stamp']
                    ))
                    print(f"✅ Inserted {ka_label} (attempt {attempt_number}) for {node_name}")
                except Exception as e:
                    print(f"❌ Failed to insert {ka_label} (attempt {attempt_number}): {e}")
        else:
            # Old format - simple count (backward compatibility)
            ka_label = attempt_key
            error_message = attempt_data if isinstance(attempt_data, str) else str(attempt_data)
            
            row = {
                'node_name': node_name,
                'blockchain_id': blockchain_name,
                'ka_label': ka_label,
                'publish_error': None,
                'query_error': None,
                'publisher_get_error': None,
                'non_publisher_get_error': None,
                'time_stamp': None,
            }

            # Try to determine error type from the key or message
            label = attempt_key.lower()
            if 'publish' in label:
                row['publish_error'] = error_message
            elif 'query' in label:
                row['query_error'] = error_message
            elif 'local get' in label:
                row['publisher_get_error'] = error_message
            elif 'get' in label:
                row['non_publisher_get_error'] = error_message

            insert_query = sql.SQL(f"""
                INSERT INTO {sql.Identifier(table_name).string} (
                    node_name, blockchain_id, ka_label,
                    publish_error, query_error,
                    publisher_get_error, non_publisher_get_error,
                    time_stamp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """)

            try:
                cursor.execute(insert_query, (
                    row['node_name'], row['blockchain_id'], row['ka_label'],
                    row['publish_error'], row['query_error'],
                    row['publisher_get_error'], row['non_publisher_get_error'],
                    row['time_stamp']
                ))
                print(f"✅ Inserted {ka_label} for {node_name} (old format)")
            except Exception as e:
                print(f"❌ Failed to insert {ka_label}: {e}")

    try:
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ DB connection closed")
    except Exception as e:
        print(f"❌ Failed to close DB connection: {e}")