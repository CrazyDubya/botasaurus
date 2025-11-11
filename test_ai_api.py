"""
AI API Testing Script
======================

Quick script to test the AI Copilot API endpoints.

Usage:
    python test_ai_api.py
"""

import requests
import json
import time
from typing import Optional


class AIAPITester:
    """Test client for AI Copilot API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.conversation_id: Optional[str] = None

    def print_section(self, title: str):
        """Print section header"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60 + "\n")

    def print_result(self, name: str, data: dict, highlight_keys: list = None):
        """Pretty print result"""
        print(f"✓ {name}")
        if highlight_keys:
            for key in highlight_keys:
                if key in data:
                    value = data[key]
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    print(f"  {key}: {value}")
        print()

    def test_health(self):
        """Test health endpoint"""
        self.print_section("1. Testing Health Endpoint")

        response = requests.get(f"{self.base_url}/health")
        data = response.json()

        self.print_result("Health Check", data, ["status", "version"])
        return response.status_code == 200

    def test_auth(self):
        """Test authentication"""
        self.print_section("2. Testing Authentication")

        # Register new user
        email = f"test_{int(time.time())}@example.com"
        password = "test_password_123"

        print(f"Registering user: {email}")
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json={
                "email": email,
                "password": password,
                "name": "Test User"
            }
        )

        if response.status_code != 200:
            print(f"❌ Registration failed: {response.json()}")
            return False

        data = response.json()
        self.token = data["access_token"]

        self.print_result("Registration", data, ["access_token", "token_type"])

        # Verify token works
        response = requests.get(
            f"{self.base_url}/api/auth/me",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        if response.status_code != 200:
            print(f"❌ Token verification failed: {response.json()}")
            return False

        self.print_result("Token Verification", response.json(), ["email", "name"])
        return True

    def test_page_analysis(self):
        """Test page analysis"""
        self.print_section("3. Testing Page Analysis")

        response = requests.post(
            f"{self.base_url}/api/ai/analyze-page",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "url": "https://www.example.com",
                "use_vision": False  # Use False for faster testing
            }
        )

        if response.status_code != 200:
            print(f"❌ Page analysis failed: {response.json()}")
            return False

        data = response.json()
        self.print_result(
            "Page Analysis",
            data,
            ["page_type", "complexity", "recommended_approach"]
        )
        return True

    def test_generate_scraper(self):
        """Test scraper generation"""
        self.print_section("4. Testing Scraper Generation")

        response = requests.post(
            f"{self.base_url}/api/ai/generate",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "prompt": "Create a simple scraper that extracts the title and all paragraph text from a webpage",
                "url": "https://www.example.com",
                "use_vision": False
            }
        )

        if response.status_code != 200:
            print(f"❌ Generation failed: {response.json()}")
            return False

        data = response.json()
        self.conversation_id = data["conversation_id"]

        self.print_result(
            "Scraper Generation",
            data,
            ["conversation_id", "tokens_used", "explanation"]
        )

        # Print generated code
        print("Generated Code Preview:")
        print("-" * 60)
        code_lines = data["code"].split("\n")
        for i, line in enumerate(code_lines[:15], 1):
            print(f"{i:3d} | {line}")
        if len(code_lines) > 15:
            print(f"     | ... ({len(code_lines) - 15} more lines)")
        print("-" * 60 + "\n")

        return True

    def test_validate_code(self):
        """Test code validation"""
        self.print_section("5. Testing Code Validation")

        # Test with invalid code (missing decorator)
        invalid_code = """
def scrape(driver, data):
    driver.get(data)
    return []
"""

        response = requests.post(
            f"{self.base_url}/api/ai/validate",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"code": invalid_code}
        )

        if response.status_code != 200:
            print(f"❌ Validation request failed: {response.json()}")
            return False

        data = response.json()
        self.print_result(
            "Validation (Invalid Code)",
            data,
            ["valid", "error_count", "warning_count"]
        )

        if data["errors"]:
            print("Errors found:")
            for error in data["errors"]:
                print(f"  - {error}")

        # Test with valid code
        valid_code = """
from botasaurus import browser

@browser
def scrape(driver, data):
    try:
        driver.get(data)
        return {"title": driver.title}
    except Exception as e:
        print(f"Error: {e}")
        return []
"""

        response = requests.post(
            f"{self.base_url}/api/ai/validate",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"code": valid_code}
        )

        data = response.json()
        self.print_result(
            "Validation (Valid Code)",
            data,
            ["valid", "error_count", "warning_count"]
        )

        return True

    def test_refine_scraper(self):
        """Test scraper refinement"""
        self.print_section("6. Testing Scraper Refinement")

        if not self.conversation_id:
            print("⚠ Skipping refinement test (no conversation_id)")
            return False

        current_code = """
from botasaurus import browser

@browser
def scrape(driver, data):
    driver.get(data)
    return {"title": driver.title}
"""

        response = requests.post(
            f"{self.base_url}/api/ai/refine",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "current_code": current_code,
                "refinement_prompt": "Add a docstring to the function",
                "conversation_id": self.conversation_id
            }
        )

        if response.status_code != 200:
            print(f"❌ Refinement failed: {response.json()}")
            return False

        data = response.json()
        self.print_result(
            "Scraper Refinement",
            data,
            ["conversation_id", "tokens_used", "explanation"]
        )

        if data["changes"]:
            print("Changes applied:")
            for change in data["changes"][:5]:
                print(f"  - {change}")

        return True

    def test_conversations(self):
        """Test conversation management"""
        self.print_section("7. Testing Conversation Management")

        # Create conversation
        response = requests.post(
            f"{self.base_url}/api/ai/conversations",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "title": "Test Conversation",
                "initial_prompt": "Hello AI!"
            }
        )

        if response.status_code != 200:
            print(f"❌ Create conversation failed: {response.json()}")
            return False

        conv_data = response.json()
        self.print_result(
            "Create Conversation",
            conv_data,
            ["id", "title"]
        )

        # Get all conversations
        response = requests.get(
            f"{self.base_url}/api/ai/conversations",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        if response.status_code != 200:
            print(f"❌ Get conversations failed: {response.json()}")
            return False

        conversations = response.json()
        print(f"✓ Retrieved {len(conversations)} conversation(s)\n")

        return True

    def test_usage_stats(self):
        """Test usage statistics"""
        self.print_section("8. Testing Usage Statistics")

        response = requests.get(
            f"{self.base_url}/api/ai/usage",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        if response.status_code != 200:
            print(f"❌ Usage stats failed: {response.json()}")
            return False

        data = response.json()
        self.print_result(
            "Usage Statistics",
            data,
            ["total_tokens", "total_cost", "requests_count", "successful_generations"]
        )

        print(f"💰 Total cost: ${data['total_cost']:.4f}")
        print(f"📊 Success rate: {data['successful_generations']}/{data['requests_count']}\n")

        return True

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "🚀" * 30)
        print("  Botasaurus AI API Test Suite")
        print("🚀" * 30)

        tests = [
            ("Health Check", self.test_health),
            ("Authentication", self.test_auth),
            ("Page Analysis", self.test_page_analysis),
            ("Generate Scraper", self.test_generate_scraper),
            ("Validate Code", self.test_validate_code),
            ("Refine Scraper", self.test_refine_scraper),
            ("Conversations", self.test_conversations),
            ("Usage Stats", self.test_usage_stats)
        ]

        results = {}
        for name, test_func in tests:
            try:
                results[name] = test_func()
            except Exception as e:
                print(f"\n❌ {name} failed with exception: {e}\n")
                results[name] = False

        # Print summary
        self.print_section("Test Summary")

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        for name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status:8} | {name}")

        print("\n" + "-" * 60)
        print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

        if passed == total:
            print("\n🎉 All tests passed! API is working correctly.\n")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Check logs above.\n")

        return passed == total


def main():
    """Main entry point"""
    tester = AIAPITester()

    print("""
╔══════════════════════════════════════════════════════════════╗
║                  AI API Testing Script                       ║
║                                                              ║
║  This script will test all AI Copilot API endpoints.        ║
║  Make sure the server is running on http://localhost:8000   ║
║                                                              ║
║  NOTE: This requires OPENAI_API_KEY or ANTHROPIC_API_KEY    ║
║        to be set in your environment or .env file           ║
╚══════════════════════════════════════════════════════════════╝
    """)

    try:
        success = tester.run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user.\n")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}\n")
        exit(1)


if __name__ == "__main__":
    main()
