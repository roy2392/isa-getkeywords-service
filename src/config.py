"""
Configuration constants for the ISA GetKeywords Service
"""

# BigQuery Configuration
BIGQUERY_KEYWORDS_TABLE = "pwcnext-sandbox01.telegram.keys"
BIGQUERY_KEYWORD_COLUMN = "keys_group"

# Gemini Configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"

# Keyword Generation Settings
KEYWORDS_PER_GENERATION = 20
INDUSTRY_FOCUS = "stocks and finance"
LANGUAGE = "Hebrew"

# Script Settings
CHECK_DUPLICATES = True
