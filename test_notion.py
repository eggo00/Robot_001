import os
import json
from dotenv import load_dotenv
from notion_client import Client
from datetime import datetime

load_dotenv()

notion = Client(auth=os.getenv('NOTION_TOKEN'))
database_id = os.getenv('NOTION_DATABASE_ID')

# Try to create a simple page
try:
    print("Trying to create a page...")
    result = notion.pages.create(
        parent={"database_id": database_id},
        properties={}
    )
    print("Success! Page created:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error creating page: {e}")
    import traceback
    traceback.print_exc()
