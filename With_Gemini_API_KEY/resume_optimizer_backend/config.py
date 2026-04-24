# import os
# from pydantic_settings import BaseSettings
# from dotenv import load_dotenv

# load_dotenv()

# class Settings(BaseSettings):
#     GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
#     SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
#     SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
#     class Config:
#         env_file = ".env"

# settings = Settings()

#######################################
from dotenv import load_dotenv
import os

load_dotenv(override=True)

GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY")
SUPABASE_URL      = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true" or not GEMINI_API_KEY

CATEGORIES = [
    "ML Engineer",
    "Data Scientist",
    "AI Engineer",
    "Computer Vision",
    "Software Engineer",
    "Biomedical Science",
    "Arts & Literature",
    "Others",
]

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set. Running in MOCK_MODE.")
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("WARNING: Supabase credentials are not set. Database features will be disabled.")