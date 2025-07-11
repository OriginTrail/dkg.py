import os
import sys
import json
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

network_config = {
    'base:mainnet':     {'blockchain_id': 'base:8453',      'table': 'error_messages_mainnet_py', 'host': os.getenv('DB_HOST_PUBLISH_MAINNET')},
    'base:testnet':     {'blockchain_id': 'base:84531',     'table': 'error_messages_testnet_py', 'host': os.getenv('DB_HOST_PUBLISH_TESTNET')},
    'gnosis:mainnet':   {'blockchain_id': 'gnosis:100',     'table': 'error_messages_mainnet_py', 'host': os.getenv('DB_HOST_PUBLISH_MAINNET')},
    'gnosis:testnet':   {'blockchain_id': 'gnosis:10200',   'table': 'error_messages_testnet_py', 'host': os.getenv('DB_HOST_PUBLISH_TESTNET')},
    'neuroweb:mainnet': {'blockchain_id': 'neuroweb:2043',  'table': 'error_messages_mainnet_py', 'host': os.getenv('DB_HOST_PUBLISH_MAINNET')},
    'neuroweb:testnet': {'blockchain_id': 'neuroweb:20432', 'table': 'error_messages_testnet_py', 'host': os.getenv('DB_HOST_PUBLISH_TESTNET')},
}

files = sys.argv[1:]

for file in files:
    print(f"📁 Processing error file: {file}")
    try:
        with open(file, 'r') as f:
            errors = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read or parse {file}: {e}")
        continue

    match = file.lower().split('errors_')
    if len(match) < 2:
        print(f"❌ Filename format incorrect for {file}. Expected: errors_Node_XX.json")
        continue

    node_name = match[1].replace('_', ' ').replace('.json', '').strip()
    is_mainnet = 'mainnet' in file.lower()

    matched_key = next(
        (key for key in network_config if key.startswith(tuple(file.lower().split('_'))) and key.endswith('mainnet') == is_mainnet),
        None
    )

    if not matched_key:
        print(f"❌ Could not determine network config for file: {file}")
        continue

    config = network_config[matched_key]
    blockchain_id = config['blockchain_id']
    table_name = config['table']
    db_host = config['host']

    try:
        conn = psycopg2.connect(
            host=db_host,
            user=os.getenv('DB_USER_PUBLISH'),
            password=os.getenv('DB_PASSWORD_PUBLISH'),
            dbname=os.getenv('DB_NAME_PUBLISH'),
            port=5432
        )
        cursor = conn.cursor()
        print(f"✅ Connected to DB ({table_name})")
    except Exception as e:
        print(f"❌ Failed to connect to DB: {e}")
        continue

    for ka_label in errors:
        row = {
            'node_name': node_name,
            'blockchain_id': blockchain_id,
            'ka_label': ka_label,
            'publish_error': None,
            'query_error': None,
            'publisher_get_error': None,
            'non_publisher_get_error': None,
            'time_stamp': errors[ka_label].get('time_stamp') or None,
        }

        label = ka_label.lower()
        if 'publish' in label:
            row['publish_error'] = ka_label
        elif 'query' in label:
            row['query_error'] = ka_label
        elif 'local get' in label:
            row['publisher_get_error'] = ka_label
        elif 'get' in label:
            row['non_publisher_get_error'] = ka_label

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
            print(f"✅ Inserted KA {ka_label} for {node_name}")
        except Exception as e:
            print(f"❌ Failed to insert KA {ka_label}: {e}")

    try:
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ DB connection closed")
    except Exception as e:
        print(f"❌ Failed to close DB connection: {e}")