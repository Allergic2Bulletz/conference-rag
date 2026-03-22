"""
Step 6: Add Custom Database Function
====================================
Creates the match_sentences_by_speaker() function to filter vector search
results by a specific speaker (e.g., "Dallin H. Oaks").

Usage:
    python scripts/06_custom_db_function.py

Prerequisites:
    - config.public.json with Supabase URL and anon key
    - config.secret.json with Supabase service key, access token, and project ref
    - Existing sentence_embeddings table with data
"""

import json
import sys

# Load configuration from both config files
with open('config.public.json', 'r') as f:
    public_config = json.load(f)
with open('config.secret.json', 'r') as f:
    secrets = json.load(f)

SUPABASE_URL = public_config['SUPABASE_URL']
SUPABASE_ACCESS_TOKEN = secrets['SUPABASE_ACCESS_TOKEN']
SUPABASE_PROJECT_REF = secrets['SUPABASE_PROJECT_REF']


def create_speaker_function():
    import requests

    print("=" * 60)
    print("Creating match_sentences_by_speaker Function")
    print("=" * 60)

    function_sql = """
-- Create function for similarity search filtered by speaker
CREATE OR REPLACE FUNCTION match_sentences_by_speaker(
  query_embedding vector(1536),
  speaker_name text,
  match_count int DEFAULT 20
)
RETURNS TABLE (
  id uuid,
  talk_id uuid,
  title text,
  speaker text,
  text text,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    sentence_embeddings.id,
    sentence_embeddings.talk_id,
    sentence_embeddings.title,
    sentence_embeddings.speaker,
    sentence_embeddings.text,
    1 - (sentence_embeddings.embedding <=> query_embedding) as similarity
  FROM sentence_embeddings
  WHERE sentence_embeddings.speaker ILIKE '%' || speaker_name || '%'
  ORDER BY sentence_embeddings.embedding <=> query_embedding
  LIMIT match_count;
$$;
"""

    url = f"https://api.supabase.com/v1/projects/{SUPABASE_PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {SUPABASE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    resp = requests.post(url, headers=headers, json={"query": function_sql})
    if resp.status_code in (200, 201):
        print("✅ Function match_sentences_by_speaker created successfully!")
        return True
    else:
        print(f"❌ Function creation failed: {resp.status_code}")
        print(resp.text[:500])
        return False


if __name__ == '__main__':
    if not create_speaker_function():
        sys.exit(1)
    print("\n✅ Custom function ready!")
    print("   You can now use match_sentences_by_speaker(embedding, 'Oaks', 20)")
    print("   Function uses partial matching, so 'Oaks' will match 'By President Dallin H. Oaks'")
    print("   in your frontend code.")
