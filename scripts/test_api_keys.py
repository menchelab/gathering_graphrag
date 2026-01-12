import os
from dotenv import load_dotenv
from google import genai
from neo4j import GraphDatabase, exceptions


# 1. Load Environment Variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


def test_google_genai():
    print("--- Testing Google GenAI Connection ---")
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY not found in environment variables.")
        return

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Explain first knowledge graphs and then GraphRAG in a few words.",
        )
        print(f"✅ Google GenAI Connection Successful.")
        print(f"\nResponse received:\n{response.text}...")
    except Exception as e:
        print(f"❌ Google GenAI Connection Failed: {e}")


def test_neo4j():
    print("\n--- Testing Neo4j Connection ---")
    if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
        print("❌ Neo4j credentials (URI, USERNAME, or PASSWORD) missing.")
        return

    driver = None
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print(f"✅ Neo4j Connection Successful to {NEO4J_URI}")
    except exceptions.ServiceUnavailable as e:
        print(
            f"❌ Neo4j Connection Failed: Service Unavailable. Check your URI and network."
        )
        print(f"   Error: {e}")
    except exceptions.AuthError as e:
        print(f"❌ Neo4j Authentication Failed. Check your username/password.")
    except Exception as e:
        print(f"❌ Neo4j Connection Failed: {e}")
    finally:
        if driver:
            driver.close()


if __name__ == "__main__":
    test_google_genai()
    test_neo4j()
