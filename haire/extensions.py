import os
from dotenv import load_dotenv
from google import genai
from supabase import create_client, Client

load_dotenv()

ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)