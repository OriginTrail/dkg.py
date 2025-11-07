import os
import json
import urllib3
from dotenv import load_dotenv

# Load webhook URL from environment
load_dotenv()
TEAMS_HOOK_URL = os.getenv("TEAMS_HOOK")

if not TEAMS_HOOK_URL:
    print("Error: TEAMS_HOOK environment variable is not set!")
    exit(1)

# Verify webhook URL format
if not TEAMS_HOOK_URL.startswith(("https://outlook.office.com/webhook/", "https://outlook.office365.com/webhook/")):
    print("Warning: Webhook URL doesn't match expected Teams format")
    print(f"URL starts with: {TEAMS_HOOK_URL[:30]}...")

print(f"Using webhook URL: {TEAMS_HOOK_URL[:20]}...")

# Read test results
try:
    with open(".report/mainnet_base.json", "r") as f:
        report = json.load(f)
except Exception as e:
    print(f"Error reading test results: {str(e)}")
    exit(1)

# Get test results
summary = report.get("summary", {})
total = summary.get("total", 0)
passed = summary.get("passed", 0)
failed = summary.get("failed", 0)

def create_adaptive_card(header_text, message_body, report_url):
    '''
    create and return an adaptive card with a link to the HTML report
    '''
    adaptive_card = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.2",
        "body": [
            {
                "type": "TextBlock",
                "text": header_text,
                "style": "heading",
                "size": "Large",
                "weight": "bolder",
                "wrap": True,
                "color": "good"                
            },
            {
                "type": "TextBlock",
                "weight": "default",
                "wrap": True,
                "size": "default",
                "text": message_body
            },
            {
                "type": "ActionSet",
                "actions": [
                    {
                        "type": "Action.OpenUrl",
                        "title": "View HTML Report",
                        "url": report_url
                    }
                ]
            }
        ]
    }
    return adaptive_card

def send_adaptive_card_to_ms_teams(webhook, adaptive_card):
    '''
    send an adaptive card to an MS Teams channel using a webhook
    '''
    http = urllib3.PoolManager()
    payload = json.dumps(
        {
            "type": "message",
            "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive", "content": adaptive_card}]
        }
    )
    headers = {"Content-Type": "application/json"}
    response = http.request("POST", webhook, body=payload, headers=headers)
    print("Response status:", response.status)
    if response.status >= 300:
        print("Error response:", response.data.decode('utf-8'))

def send_message_to_ms_teams(webhook, message_body, report_url):
    '''
    send a simple text message to an MS Teams channel using a webhook
    '''
    http = urllib3.PoolManager()
    payload = json.dumps(
        {
            "@context": "http://schema.org/extensions",
            "type": "MessageCard",
            "title": "DKG Test Results",
            "summary": "Test execution results",
            "text": message_body,
            "themeColor": "2DC72D",
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "View HTML Report",
                    "targets": [
                        {
                            "os": "default",
                            "uri": report_url
                        }
                    ]
                }
            ]
        }
    )
    headers = {"Content-Type": "application/json"}
    response = http.request("POST", webhook, body=payload, headers=headers)
    print("Response status:", response.status)
    if response.status >= 300:
        print("Error response:", response.data.decode('utf-8'))

# Only send notifications if there are failed tests
if failed > 0:
    # Prepare message content
    header_text = "DKG Python Mainnet Base Tests Failed"
    message_body = f"""
    Test Results Summary:
    - Total Tests: {total}
    - Passed: {passed}
    - Failed: {failed}
    """
    
    # Use the remote report URL
    report_url =""

    print("\nSending direct message...")
    send_message_to_ms_teams(TEAMS_HOOK_URL, message_body, report_url)

    print("\nSending adaptive card...")
    adaptive_card = create_adaptive_card(header_text, message_body, report_url)
    send_adaptive_card_to_ms_teams(TEAMS_HOOK_URL, adaptive_card)
else:
    print("All tests passed, no notification needed.")


