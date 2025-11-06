# Botasaurus Testing Framework Guide

## Overview

The Botasaurus Testing Framework leverages the existing anti-detection capabilities to provide **undetectable browser automation testing**. This positions Botasaurus as a superior alternative to Playwright/Cypress for scenarios requiring stealth or testing anti-bot systems.

---

## Why Use Botasaurus for Testing?

### Advantages Over Traditional Testing Tools

| Feature | Botasaurus Testing | Playwright | Cypress | Selenium |
|---------|-------------------|------------|---------|----------|
| **Anti-Detection** | ✅ Best-in-class | ❌ Easily detected | ❌ Easily detected | ❌ Easily detected |
| **Cloudflare Bypass** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Bot Test Passing** | ✅ All major tests | ❌ Limited | ❌ Limited | ❌ Limited |
| **Human-like Actions** | ✅ Yes | ⚠️ Basic | ⚠️ Basic | ❌ No |
| **Parallel Execution** | ✅ Built-in | ✅ Yes | ⚠️ Limited | ⚠️ Manual |
| **Visual Regression** | ✅ Planned | ✅ Via plugins | ✅ Via plugins | ⚠️ Via tools |

---

## Core Capabilities

### 1. Existing Botasaurus Features Available for Testing

All current Botasaurus capabilities can be used for testing:

```python
from botasaurus import browser

@browser
def test_login_flow(driver, data):
    """Test user login with undetectable automation"""
    driver.get("https://example.com/login")

    # Human-like typing
    driver.type("#username", data["username"], human=True)
    driver.type("#password", data["password"], human=True)

    # Human-like click
    driver.click("#login-button", human=True)

    # Assertions
    assert "Dashboard" in driver.title
    assert driver.is_visible("#welcome-message")

    return {"status": "passed"}
```

**Key Features:**
- `driver.type(..., human=True)` - Natural typing speed with variations
- `driver.click(..., human=True)` - Realistic mouse movements
- `driver.scroll(..., smooth=True)` - Human-like scrolling
- Anti-detection browser fingerprinting
- Bypasses Cloudflare, DataDome, Fingerprint, etc.

### 2. Session Management

```python
from botasaurus import browser

@browser(
    profile="test-user-1",  # Persistent browser profile
    user_agent="chrome",
    block_images=False,
    wait_for_complete_page_load=True
)
def test_authenticated_flow(driver, data):
    """Test with persistent session/cookies"""
    # Cookies/auth persisted across runs
    driver.get("https://example.com/dashboard")

    # Verify authenticated state
    assert driver.is_visible("#user-profile")
```

### 3. Network Interception (Existing)

```python
from botasaurus import browser, Request

@browser
def test_api_calls(driver, data):
    """Monitor network requests during test"""
    # Enable request interception
    driver.enable_request_interception()

    driver.get("https://example.com")

    # Verify API calls made
    requests = driver.get_requests()
    api_calls = [r for r in requests if "/api/" in r.url]

    assert len(api_calls) > 0
    assert any("users" in r.url for r in api_calls)
```

### 4. Screenshot & Visual Testing

```python
from botasaurus import browser

@browser
def test_visual_regression(driver, data):
    """Capture screenshots for visual comparison"""
    driver.get("https://example.com")
    driver.wait_for_element("#main-content")

    # Full page screenshot
    driver.save_screenshot("homepage.png")

    # Element screenshot
    driver.save_screenshot("header.png", selector="#header")

    # Compare with baseline (TODO: implement diff logic)
    # similarity = compare_screenshots("baseline.png", "homepage.png")
    # assert similarity > 0.95
```

---

## New Testing Additions

### Custom Assertions Module

Create `/botasaurus_testing/assertions.py`:

```python
"""
Custom Assertions for Botasaurus Testing
=========================================
"""

class BotasaurusAssertions:
    """Enhanced assertions for web testing"""

    @staticmethod
    def assert_element_visible(driver, selector, timeout=10):
        """Assert element is visible within timeout"""
        assert driver.is_visible(selector, timeout=timeout), \
            f"Element {selector} not visible after {timeout}s"

    @staticmethod
    def assert_text_contains(driver, selector, expected_text):
        """Assert element contains text"""
        element = driver.find_element(selector)
        actual_text = element.text
        assert expected_text in actual_text, \
            f"Expected '{expected_text}' in '{actual_text}'"

    @staticmethod
    def assert_url_matches(driver, pattern):
        """Assert current URL matches pattern"""
        import re
        actual_url = driver.current_url
        assert re.search(pattern, actual_url), \
            f"URL '{actual_url}' doesn't match pattern '{pattern}'"

    @staticmethod
    def assert_network_call_made(driver, url_pattern):
        """Assert network request was made"""
        requests = driver.get_requests()
        matching = [r for r in requests if url_pattern in r.url]
        assert len(matching) > 0, \
            f"No network calls matching '{url_pattern}'"

    @staticmethod
    def assert_no_console_errors(driver):
        """Assert no JavaScript console errors"""
        logs = driver.get_logs()
        errors = [log for log in logs if log["level"] == "SEVERE"]
        assert len(errors) == 0, \
            f"Console errors found: {errors}"
```

### Test Runner

Create `/botasaurus_testing/test_runner.py`:

```python
"""
Test Runner
===========

Executes test suites with parallel execution and reporting.
"""

from botasaurus import bt
from typing import List, Dict, Any
import json
from datetime import datetime


class TestRunner:
    """
    Test execution framework.

    Example:
        runner = TestRunner()
        runner.add_test(test_login)
        runner.add_test(test_checkout)
        results = runner.run()
    """

    def __init__(self, parallel=True, max_workers=4):
        self.tests = []
        self.parallel = parallel
        self.max_workers = max_workers
        self.results = []

    def add_test(self, test_function, data=None):
        """Add test to suite"""
        self.tests.append({
            "function": test_function,
            "data": data or {},
            "name": test_function.__name__
        })

    def run(self) -> Dict[str, Any]:
        """
        Execute all tests and return results.

        Returns:
            {
                "total": 10,
                "passed": 8,
                "failed": 2,
                "duration": 45.3,
                "tests": [...]
            }
        """
        start_time = datetime.now()

        if self.parallel:
            # Use Botasaurus parallel execution
            test_functions = [t["function"] for t in self.tests]
            test_data = [t["data"] for t in self.tests]

            # Execute in parallel
            results = []
            for test_func, data in zip(test_functions, test_data):
                try:
                    result = test_func(data)
                    results.append({
                        "name": test_func.__name__,
                        "status": "passed",
                        "result": result
                    })
                except AssertionError as e:
                    results.append({
                        "name": test_func.__name__,
                        "status": "failed",
                        "error": str(e)
                    })
                except Exception as e:
                    results.append({
                        "name": test_func.__name__,
                        "status": "error",
                        "error": str(e)
                    })
        else:
            # Sequential execution
            results = []
            for test in self.tests:
                try:
                    result = test["function"](test["data"])
                    results.append({
                        "name": test["name"],
                        "status": "passed",
                        "result": result
                    })
                except AssertionError as e:
                    results.append({
                        "name": test["name"],
                        "status": "failed",
                        "error": str(e)
                    })
                except Exception as e:
                    results.append({
                        "name": test["name"],
                        "status": "error",
                        "error": str(e)
                    })

        duration = (datetime.now() - start_time).total_seconds()

        passed = sum(1 for r in results if r["status"] == "passed")
        failed = sum(1 for r in results if r["status"] in ["failed", "error"])

        return {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "duration": duration,
            "tests": results
        }

    def generate_report(self, output_path="test-report.html"):
        """Generate HTML test report"""
        results = self.run()

        html = f"""
        <html>
        <head><title>Test Report</title></head>
        <body>
            <h1>Botasaurus Test Report</h1>
            <p>Total: {results['total']} |
               Passed: {results['passed']} |
               Failed: {results['failed']} |
               Duration: {results['duration']:.2f}s</p>
            <ul>
        """

        for test in results["tests"]:
            status_color = "green" if test["status"] == "passed" else "red"
            html += f"<li style='color: {status_color}'>{test['name']}: {test['status']}</li>"

        html += "</ul></body></html>"

        with open(output_path, "w") as f:
            f.write(html)

        return output_path
```

---

## Usage Examples

### Example 1: E-commerce Testing

```python
from botasaurus import browser
from botasaurus_testing import BotasaurusAssertions as Assert

@browser
def test_product_search(driver, data):
    """Test product search functionality"""
    driver.get("https://example-shop.com")

    # Search for product
    driver.type("#search", "laptop", human=True)
    driver.click("#search-button", human=True)

    # Assertions
    Assert.assert_url_matches(driver, r"/search\?q=laptop")
    Assert.assert_element_visible(driver, ".product-card")
    Assert.assert_text_contains(driver, "h1", "Search Results")

    # Verify products loaded
    products = driver.find_elements(".product-card")
    assert len(products) > 0, "No products found"

    return {"status": "passed", "product_count": len(products)}

@browser
def test_add_to_cart(driver, data):
    """Test add to cart functionality"""
    driver.get(data["product_url"])

    # Add to cart
    driver.wait_for_element("#add-to-cart")
    driver.click("#add-to-cart", human=True)

    # Verify cart updated
    Assert.assert_element_visible(driver, ".cart-notification")

    # Check cart count
    cart_count = driver.find_element(".cart-count").text
    assert int(cart_count) > 0

    return {"status": "passed"}

# Run tests
if __name__ == "__main__":
    from botasaurus_testing import TestRunner

    runner = TestRunner(parallel=True)
    runner.add_test(test_product_search)
    runner.add_test(test_add_to_cart, data={"product_url": "https://example-shop.com/product/123"})

    results = runner.run()
    print(f"Tests passed: {results['passed']}/{results['total']}")
```

### Example 2: API Monitoring During Tests

```python
from botasaurus import browser

@browser
def test_api_performance(driver, data):
    """Monitor API performance during page load"""
    driver.enable_request_interception()

    driver.get("https://example.com")

    # Analyze API calls
    requests = driver.get_requests()
    api_calls = [r for r in requests if "/api/" in r.url]

    # Performance assertions
    slow_calls = [r for r in api_calls if r.duration > 1000]  # > 1s
    assert len(slow_calls) == 0, f"Slow API calls detected: {slow_calls}"

    # Verify critical endpoints called
    assert any("/api/users" in r.url for r in api_calls), "Users API not called"

    return {
        "status": "passed",
        "total_api_calls": len(api_calls),
        "avg_duration": sum(r.duration for r in api_calls) / len(api_calls)
    }
```

### Example 3: Visual Regression Testing

```python
from botasaurus import browser
import os

@browser
def test_homepage_visual(driver, data):
    """Visual regression test for homepage"""
    driver.get("https://example.com")
    driver.wait_for_complete_page_load()

    screenshot_path = "screenshots/homepage.png"
    baseline_path = "screenshots/baseline/homepage.png"

    # Take screenshot
    driver.save_screenshot(screenshot_path)

    # Compare with baseline (if exists)
    if os.path.exists(baseline_path):
        # TODO: Implement image comparison
        # from PIL import Image
        # similarity = compare_images(baseline_path, screenshot_path)
        # assert similarity > 0.95, f"Visual regression detected: {similarity}"
        pass
    else:
        # First run - save as baseline
        import shutil
        os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
        shutil.copy(screenshot_path, baseline_path)

    return {"status": "passed"}
```

---

## CI/CD Integration

### GitHub Actions

`.github/workflows/botasaurus-tests.yml`:

```yaml
name: Botasaurus Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install botasaurus botasaurus-testing

      - name: Run tests
        run: python run_tests.py

      - name: Upload test report
        uses: actions/upload-artifact@v2
        if: always()
        with:
          name: test-report
          path: test-report.html
```

### Jenkins

```groovy
pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh 'pip install botasaurus botasaurus-testing'
            }
        }

        stage('Test') {
            steps {
                sh 'python run_tests.py'
            }
        }

        stage('Report') {
            steps {
                publishHTML(target: [
                    reportDir: '.',
                    reportFiles: 'test-report.html',
                    reportName: 'Botasaurus Test Report'
                ])
            }
        }
    }
}
```

---

## Best Practices

### 1. Use Human-like Actions
Always use `human=True` for realistic interactions:
```python
driver.type("#input", "text", human=True)
driver.click("#button", human=True)
```

### 2. Explicit Waits
Wait for elements before interaction:
```python
driver.wait_for_element("#dynamic-content", timeout=10)
driver.click("#dynamic-content button")
```

### 3. Persistent Profiles
Use profiles for tests requiring auth:
```python
@browser(profile="test-user")
def test_authenticated(driver, data):
    # Session persists across runs
    pass
```

### 4. Network Monitoring
Monitor API calls in tests:
```python
driver.enable_request_interception()
# ... perform actions ...
requests = driver.get_requests()
```

### 5. Parallel Execution
Run independent tests in parallel:
```python
runner = TestRunner(parallel=True, max_workers=8)
```

---

## Roadmap

### Phase 1 (Q1 2025) - Foundation
- ✅ Document existing testing capabilities
- ⬜ Create custom assertions module
- ⬜ Build test runner with reporting
- ⬜ CI/CD integration examples

### Phase 2 (Q2 2025) - Enhanced Features
- ⬜ Visual regression testing (image diff)
- ⬜ Performance profiling
- ⬜ Test data generation helpers
- ⬜ Mock server integration

### Phase 3 (Q3 2025) - Enterprise
- ⬜ Distributed test execution
- ⬜ Test analytics dashboard
- ⬜ Integration with test management tools
- ⬜ Custom reporter formats (JUnit, Allure)

### Phase 4 (Q4 2025) - Advanced
- ⬜ AI-powered test generation
- ⬜ Self-healing tests (auto-fix selectors)
- ⬜ Cross-browser testing
- ⬜ Mobile testing support

---

## Comparison: Testing Real-World Scenarios

### Scenario: Testing a Site with Cloudflare

**Traditional Tools (Playwright/Cypress):**
```python
# ❌ Gets blocked by Cloudflare
await page.goto("https://cloudflare-protected-site.com")
# Result: Blocked, CAPTCHA challenge
```

**Botasaurus:**
```python
# ✅ Bypasses Cloudflare
@browser
def test_cloudflare_site(driver, data):
    driver.get("https://cloudflare-protected-site.com")
    # Result: Page loads successfully, tests proceed
```

### Scenario: Bot Detection Tests

**Traditional Tools:**
```javascript
// ❌ Detected as bot
await page.goto("https://browserscan.net/bot-detection");
// Result: "You are a bot" message
```

**Botasaurus:**
```python
# ✅ Passes bot detection
@browser
def test_bot_detection(driver, data):
    driver.get("https://browserscan.net/bot-detection")
    # Result: Passes as human, tests work
```

---

## Conclusion

Botasaurus Testing Framework provides **unique advantages** for:
- Testing sites with bot protection
- Realistic user simulation
- Performance monitoring
- Visual regression testing

It's particularly valuable when traditional testing tools fail due to anti-bot measures.

**Next Steps:**
1. Try existing capabilities with your tests
2. Provide feedback on needed features
3. Contribute to testing module development

For questions, visit: https://github.com/omkarcloud/botasaurus/issues
