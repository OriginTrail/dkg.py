# tests/mainnet/conftest.py

import os
import json
import pytest
import time
from datetime import datetime
from tests.mainnet.stats_tracker import global_stats, error_stats

def pytest_configure(config):
    """Configure pytest to collect custom markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")

def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their names"""
    for item in items:
        if "testnet" in item.nodeid.lower():
            item.add_marker(pytest.mark.testnet)
        if "mainnet" in item.nodeid.lower():
            item.add_marker(pytest.mark.mainnet)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests"""
    # Create test_output directory if it doesn't exist
    os.makedirs("test_output", exist_ok=True)
    
    # Clear global dictionaries to prevent errors from previous runs
    global_stats.clear()
    error_stats.clear()
    
    # Clear error files at the start of each test run to show only current run errors
    error_files_to_clear = [
        "test_output/error_stats.json",
        "test_output/global_stats.json"
    ]
    
    for error_file in error_files_to_clear:
        if os.path.exists(error_file):
            try:
                os.remove(error_file)
            except Exception:
                pass
    
    # Also clear individual node error files
    import glob
    for node_error_file in glob.glob("test_output/errors_*.json"):
        try:
            os.remove(node_error_file)
        except Exception:
            pass

def get_error_breakdown(node_name):
    """Get error breakdown for a specific node from multiple sources"""
    all_errors = {}
    
    # Source 1: Aggregated error file
    aggregated_file = "test_output/error_stats.json"
    if os.path.exists(aggregated_file):
        try:
            with open(aggregated_file, 'r') as f:
                aggregated_errors = json.load(f)
                if node_name in aggregated_errors:
                    all_errors.update(aggregated_errors[node_name])
        except Exception:
            pass
    
    # Source 2: Individual node error file
    node_file = f"test_output/errors_{node_name.replace(' ', '_')}.json"
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
    
    # Source 3: In-memory error stats (if available)
    try:
        if node_name in error_stats:
            all_errors.update(error_stats[node_name])
    except ImportError:
        pass
    
    return all_errors

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Generate a comprehensive test summary at the end"""
    print("\n" + "="*80)
    print("📊 Global Publish Summary:")
    print("="*80)
    
    # Wait a moment for any pending file writes
    time.sleep(1)
    
    # Get all test nodes from the environment
    node_to_test = os.getenv("NODE_TO_TEST")
    
    if node_to_test:
        # Test specific nodes
        nodes_to_check = [node.strip() for node in node_to_test.split(",")]
    else:
        # Check all possible nodes
        nodes_to_check = [
            "Node 25", "Node 26", "Node 27", "Node 28", "Node 29", "Node 30"
        ]
    
    # Get global stats
    global_stats_file = "test_output/global_stats.json"
    global_stats = {}
    if os.path.exists(global_stats_file):
        try:
            with open(global_stats_file, 'r') as f:
                global_stats = json.load(f)
        except Exception:
            pass
    
    # Display blockchain summaries only for the tested nodes
    for blockchain, nodes in global_stats.items():
        print(f"\n🔗 Blockchain: {blockchain}")
        for node_name, node_stats in nodes.items():
            # Only show stats for nodes that were actually tested
            if node_name in nodes_to_check:
                print(f"  • {node_name}:")
                
                # Publish stats
                p_success = node_stats.get('publish_success', 0)
                p_failed = node_stats.get('publish_failed', 0)
                p_rate = round(p_success / (p_success + p_failed) * 100, 2) if (p_success + p_failed) > 0 else 0.0
                print(f"    🔸 Publish: ✅ {p_success} / ❌ {p_failed} -> {p_rate}%")
                
                # Query stats
                q_success = node_stats.get('query_success', 0)
                q_failed = node_stats.get('query_failed', 0)
                q_rate = round(q_success / (q_success + q_failed) * 100, 2) if (q_success + q_failed) > 0 else 0.0
                print(f"    🔸 Query:   ✅ {q_success} / ❌ {q_failed} -> {q_rate}%")
                
                # Local Get stats
                lg_success = node_stats.get('local_get_success', 0)
                lg_failed = node_stats.get('local_get_failed', 0)
                lg_rate = round(lg_success / (lg_success + lg_failed) * 100, 2) if (lg_success + lg_failed) > 0 else 0.0
                print(f"    🔸 Local Get: ✅ {lg_success} / ❌ {lg_failed} -> {lg_rate}%")
                
                # Remote Get stats
                rg_success = node_stats.get('remote_get_success', 0)
                rg_failed = node_stats.get('remote_get_failed', 0)
                rg_rate = round(rg_success / (rg_success + rg_failed) * 100, 2) if (rg_success + rg_failed) > 0 else 0.0
                print(f"    🔸 Get: ✅ {rg_success} / ❌ {rg_failed} -> {rg_rate}%")
                
                # Timing stats
                def format_time(seconds):
                    return f"{int(seconds // 60)} min {seconds % 60:.2f} sec" if seconds >= 60 else f"{seconds:.2f} seconds"
                
                def avg_time(times):
                    return sum(times) / len(times) if times else 0.0
                
                print(f"    ⏱️ Avg Publish Time: {format_time(avg_time(node_stats.get('publish_times', [])))}")
                print(f"    ⏱️ Avg Query Time: {format_time(avg_time(node_stats.get('query_times', [])))}")
                print(f"    ⏱️ Avg Local Get Time: {format_time(avg_time(node_stats.get('local_get_times', [])))}")
                print(f"    ⏱️ Avg Get Time: {format_time(avg_time(node_stats.get('remote_get_times', [])))}")
    
    print("\n📊 Error Breakdown by Node:")
    
    # Process each node for errors
    for node_name in nodes_to_check:
        print(f"\n🔧 {node_name}")
        
        # Get errors for this node
        errors = get_error_breakdown(node_name)
        
        if errors:
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
                    
                    # Show actual error messages for each error type
                    error_lines = []
                    if publish_error:
                        error_lines.append(f"    • publishing — {publish_error}")
                    if query_error:
                        error_lines.append(f"    • querying — {query_error}")
                    if publisher_get_error:
                        error_lines.append(f"    • local get — {publisher_get_error}")
                    if non_publisher_get_error:
                        error_lines.append(f"    • remote get — {non_publisher_get_error}")
                    
                    if error_lines:
                        print(f"  • {ka_label} (attempt {attempt_number}):")
                        for line in error_lines:
                            print(line)
                    else:
                        print(f"  • {ka_label} (attempt {attempt_number}): no errors")
                else:
                    # Old format - simple count
                    count = attempt_data if isinstance(attempt_data, int) else 1
                    print(f"  • {count}x {attempt_key}")
        else:
            print("  • No errors")
    
    print(f"\n⏰ Summary generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)