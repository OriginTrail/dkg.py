# scripts/print_aggregated_errors.py

import os
import json

ERROR_DIR = "test_output"

def safe_rate(success, fail):
    total = success + fail
    return round((success / total) * 100, 2) if total > 0 else 0.0

def avg(times):
    return round(sum(times) / len(times), 2) if times else 0.0

def create_aggregated_error_file():
    """Create aggregated error_stats.json from individual node files"""
    aggregated_errors = {}
    
    # Determine which nodes to check based on environment
    # Check if we're in a mainnet or testnet context by looking at existing files
    testnet_nodes = [
        "Node 01", "Node 04", "Node 05", "Node 06", "Node 07", "Node 08", 
        "Node 09", "Node 10", "Node 13", "Node 14", "Node 21", "Node 23", "Node 37"
    ]
    
    mainnet_nodes = [
        "Node 25", "Node 26", "Node 27", "Node 28", "Node 29", "Node 30"
    ]
    
    # Check which type of nodes have error files to determine context
    testnet_files_exist = any(os.path.exists(os.path.join(ERROR_DIR, f"errors_{node.replace(' ', '_')}.json")) for node in testnet_nodes)
    mainnet_files_exist = any(os.path.exists(os.path.join(ERROR_DIR, f"errors_{node.replace(' ', '_')}.json")) for node in mainnet_nodes)
    
    # Determine which nodes to process
    if mainnet_files_exist and not testnet_files_exist:
        # Mainnet context
        nodes_to_check = mainnet_nodes
    elif testnet_files_exist and not mainnet_files_exist:
        # Testnet context
        nodes_to_check = testnet_nodes
    else:
        # Mixed context or no files - check all
        nodes_to_check = testnet_nodes + mainnet_nodes
    
    # Read each individual node error file
    for node_name in nodes_to_check:
        node_file = os.path.join(ERROR_DIR, f"errors_{node_name.replace(' ', '_')}.json")
        if os.path.exists(node_file):
            try:
                with open(node_file, 'r') as f:
                    node_data = json.load(f)
                    # Handle both old and new format
                    if isinstance(node_data, dict) and 'errors' in node_data:
                        # New format with blockchain information
                        node_errors = node_data.get('errors', {})
                    else:
                        # Old format - direct error data
                        node_errors = node_data
                    
                    if node_errors:  # Only add if there are errors
                        aggregated_errors[node_name] = node_errors
            except Exception as e:
                print(f"⚠️ Warning: Could not read {node_file}: {e}")
    
    # Write aggregated file
    aggregated_file = os.path.join(ERROR_DIR, "error_stats.json")
    with open(aggregated_file, 'w') as f:
        json.dump(aggregated_errors, f, indent=2)
    
    return aggregated_errors

def get_all_errors_for_node(node_name):
    """Get all errors for a specific node from multiple sources"""
    all_errors = {}
    
    # Source 1: Aggregated error file
    aggregated_file = os.path.join(ERROR_DIR, "error_stats.json")
    if os.path.exists(aggregated_file):
        try:
            with open(aggregated_file, 'r') as f:
                aggregated_errors = json.load(f)
                if node_name in aggregated_errors:
                    all_errors.update(aggregated_errors[node_name])
        except Exception:
            pass
    
    # Source 2: Individual node error file
    node_file = os.path.join(ERROR_DIR, f"errors_{node_name.replace(' ', '_')}.json")
    if os.path.exists(node_file):
        try:
            with open(node_file, 'r') as f:
                node_data = json.load(f)
                # Handle both old and new format
                if isinstance(node_data, dict) and 'errors' in node_data:
                    # New format with blockchain information
                    node_errors = node_data.get('errors', {})
                else:
                    # Old format - direct error data
                    node_errors = node_data
                all_errors.update(node_errors)
        except Exception:
            pass
    
    # Source 3: Check for any other error files that might contain this node's errors
    # This handles cases where errors might be stored in different formats
    for filename in os.listdir(ERROR_DIR):
        if filename.endswith('.json') and 'error' in filename.lower():
            file_path = os.path.join(ERROR_DIR, filename)
            try:
                with open(file_path, 'r') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, dict) and node_name in file_data:
                        if isinstance(file_data[node_name], dict):
                            all_errors.update(file_data[node_name])
            except Exception:
                pass
    
    return all_errors

def print_all_errors():
    print("\n📊 Error Breakdown by Node:\n")
    
    # Create aggregated error file from individual files
    aggregated_errors = create_aggregated_error_file()
    
    # Determine which nodes to show based on context
    testnet_nodes = [
        "Node 01", "Node 04", "Node 05", "Node 06", "Node 07", "Node 08", 
        "Node 09", "Node 10", "Node 13", "Node 14", "Node 21", "Node 23", "Node 37"
    ]
    
    mainnet_nodes = [
        "Node 25", "Node 26", "Node 27", "Node 28", "Node 29", "Node 30"
    ]
    
    # Check which type of nodes have error files to determine context
    testnet_files_exist = any(os.path.exists(os.path.join(ERROR_DIR, f"errors_{node.replace(' ', '_')}.json")) for node in testnet_nodes)
    mainnet_files_exist = any(os.path.exists(os.path.join(ERROR_DIR, f"errors_{node.replace(' ', '_')}.json")) for node in mainnet_nodes)
    
    # Determine which nodes to process
    if mainnet_files_exist and not testnet_files_exist:
        # Mainnet context
        nodes_to_show = mainnet_nodes
    elif testnet_files_exist and not mainnet_files_exist:
        # Testnet context
        nodes_to_show = testnet_nodes
    else:
        # Mixed context or no files - check all
        nodes_to_show = testnet_nodes + mainnet_nodes
    
    # Get nodes that have errors
    nodes_with_errors = list(aggregated_errors.keys())
    
    # If no aggregated errors, check individual files
    if not nodes_with_errors:
        for node_name in nodes_to_show:
            node_file = os.path.join(ERROR_DIR, f"errors_{node_name.replace(' ', '_')}.json")
            if os.path.exists(node_file):
                try:
                    with open(node_file, 'r') as f:
                        node_data = json.load(f)
                        # Handle both old and new format
                        if isinstance(node_data, dict) and 'errors' in node_data:
                            # New format with blockchain information
                            node_errors = node_data.get('errors', {})
                        else:
                            # Old format - direct error data
                            node_errors = node_data
                        
                        if node_errors:
                            nodes_with_errors.append(node_name)
                except Exception:
                    pass
    
    # If still no nodes with errors, check all nodes anyway
    if not nodes_with_errors:
        nodes_with_errors = nodes_to_show
    
    # Process each node
    for node_name in nodes_to_show:
        errors = get_all_errors_for_node(node_name)
        
        if errors:
            print(f"🔧 {node_name}")
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
                    
                    # Show which errors occurred for this attempt
                    error_types = []
                    if publish_error:
                        error_types.append("publish")
                    if query_error:
                        error_types.append("query")
                    if publisher_get_error:
                        error_types.append("local get")
                    if non_publisher_get_error:
                        error_types.append("remote get")
                    
                    if error_types:
                        print(f"  • {ka_label} (attempt {attempt_number}): {', '.join(error_types)} errors")
                    else:
                        print(f"  • {ka_label} (attempt {attempt_number}): no errors")
                else:
                    # Old format - simple count
                    count = attempt_data if isinstance(attempt_data, int) else 1
                    print(f"  • {count}x {attempt_key}")
            print()
        else:
            print(f"✅ {node_name}: No errors\n")

def print_error_for_node():
    node_to_test = os.getenv("NODE_TO_TEST")
    if not node_to_test:
        return  # Skip if not running in per-node context

    print("\n📊 Error Breakdown by Node:\n")

    errors = get_all_errors_for_node(node_to_test)
    
    print(f"🔧 {node_to_test}")
    if not errors:
        print("  ✅ No errors\n")
    else:
        for error_key, count in errors.items():
            print(f"  • {count}x {error_key}")
        print()

if __name__ == "__main__":
    if os.getenv("AGGREGATE_MODE") == "true":
        print_all_errors()
    else:
        print_error_for_node()
