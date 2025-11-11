"""
Prompt Engineering for AI Copilot
==================================

Carefully crafted prompts for generating high-quality scraper code.
"""

SYSTEM_PROMPT = """You are an expert at generating Botasaurus web scraping code.

Botasaurus is a Python framework with three main decorators:

1. @browser - For browser-based scraping (Selenium-like)
   - Use for JavaScript-heavy sites
   - Supports human-like interactions
   - Has anti-detection capabilities
   - Example:
   ```python
   from botasaurus import browser

   @browser
   def scrape_page(driver, data):
       driver.get(data['url'])
       title = driver.find_element('#title').text
       price = driver.find_element('.price').text
       return {'title': title, 'price': price}
   ```

2. @request - For HTTP request-based scraping
   - Use for static sites, APIs
   - Faster than browser
   - Good for simple pages
   - Example:
   ```python
   from botasaurus import request
   from bs4 import BeautifulSoup

   @request
   def scrape_api(request, data):
       response = request.get(data['url'])
       soup = BeautifulSoup(response.text, 'html.parser')
       title = soup.select_one('#title').text
       return {'title': title}
   ```

3. @task - For parallel processing without web
   - Use for data transformation
   - No web scraping, just processing
   - Example:
   ```python
   from botasaurus import task

   @task
   def process_data(data):
       return data['value'] * 2
   ```

IMPORTANT BEST PRACTICES:
1. Always use try/except for error handling
2. Use explicit waits (driver.wait_for_element) instead of sleep()
3. Return structured data (dict or list of dicts)
4. Include clear comments explaining logic
5. Use human=True for clicks and typing to avoid detection
6. Check if elements exist before accessing them
7. Use CSS selectors when possible (more stable than XPath)

Generate clean, production-ready Python code following these best practices.
"""

USER_PROMPT_TEMPLATE = """Generate a Botasaurus scraper for the following task:

**Task:** {task_description}

{page_analysis}

{additional_context}

{examples}

Generate complete, working Python code that:
1. Uses the appropriate decorator (@browser, @request, or @task)
2. Includes proper error handling with try/except
3. Returns structured data (dict or list of dicts)
4. Has clear variable names and comments
5. Follows Botasaurus best practices
6. Uses human=True for interactions to avoid bot detection

Return ONLY the Python code with no markdown formatting or explanations.
Start directly with the imports.
"""

REFINEMENT_PROMPT_TEMPLATE = """Current code:
```python
{current_code}
```

User request: {refinement_request}

Generate the updated code incorporating the requested changes.
Maintain all existing functionality unless explicitly asked to change it.

Return ONLY the complete updated Python code with no markdown formatting or explanations.
"""

EXPLANATION_PROMPT_TEMPLATE = """Explain what this code does in 2-3 simple sentences:

```python
{code}
```

Original request: {original_prompt}

Keep it concise and non-technical. Focus on what data is being extracted and from where.
"""

SELECTOR_FINDER_PROMPT_TEMPLATE = """Given this HTML snippet and description, suggest the best CSS selector:

Description: {description}

HTML:
{html}

Provide 3 selector suggestions ranked by reliability:
1. Most specific and stable
2. Alternative if first fails
3. Fallback selector

Format as JSON:
{
  "selectors": [
    {"selector": "...", "confidence": 0.9, "reasoning": "..."},
    {"selector": "...", "confidence": 0.7, "reasoning": "..."},
    {"selector": "...", "confidence": 0.5, "reasoning": "..."}
  ]
}
"""

def build_code_generation_prompt(
    task: str,
    page_analysis: dict = None,
    context: dict = None,
    examples: list = None
) -> list:
    """
    Build prompt for code generation.

    Args:
        task: User's task description
        page_analysis: Optional page structure analysis
        context: Optional additional context
        examples: Optional example scrapers

    Returns:
        List of messages for LLM
    """

    page_info = ""
    if page_analysis:
        page_info = f"""
**Page Analysis:**
- Page Type: {page_analysis.get('page_type', 'unknown')}
- Complexity: {page_analysis.get('complexity', 'medium')}
- Main Content Areas: {', '.join(page_analysis.get('main_content', []))}
- Recommended Approach: {'@browser' if page_analysis.get('complexity') == 'high' else '@request'}
- Suggested Selectors:
{_format_selectors(page_analysis.get('recommended_selectors', []))}
"""

    additional = ""
    if context:
        additional = f"""
**Additional Context:**
{context.get('notes', '')}
{_format_constraints(context.get('constraints', []))}
"""

    examples_text = ""
    if examples:
        examples_text = f"""
**Similar Examples:**
{_format_examples(examples)}
"""

    user_prompt = USER_PROMPT_TEMPLATE.format(
        task_description=task,
        page_analysis=page_info,
        additional_context=additional,
        examples=examples_text
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]


def build_refinement_prompt(
    current_code: str,
    refinement_request: str,
    conversation_history: list = None
) -> list:
    """Build prompt for code refinement"""

    messages = conversation_history or [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    refinement = REFINEMENT_PROMPT_TEMPLATE.format(
        current_code=current_code,
        refinement_request=refinement_request
    )

    messages.append({"role": "user", "content": refinement})

    return messages


def build_explanation_prompt(code: str, original_prompt: str) -> list:
    """Build prompt for code explanation"""

    explanation = EXPLANATION_PROMPT_TEMPLATE.format(
        code=code,
        original_prompt=original_prompt
    )

    return [
        {"role": "system", "content": "You explain code in simple, non-technical terms."},
        {"role": "user", "content": explanation}
    ]


def build_selector_finder_prompt(description: str, html: str) -> list:
    """Build prompt for selector finding"""

    # Truncate HTML if too long
    if len(html) > 5000:
        html = html[:5000] + "\n... (truncated)"

    prompt = SELECTOR_FINDER_PROMPT_TEMPLATE.format(
        description=description,
        html=html,
        selector=""
    )

    return [
        {"role": "system", "content": "You are an expert at finding CSS selectors."},
        {"role": "user", "content": prompt}
    ]


def _format_selectors(selectors: list) -> str:
    """Format selectors for display"""
    if not selectors:
        return "  (None identified)"

    formatted = []
    for sel in selectors[:5]:  # Top 5
        formatted.append(f"  - {sel.get('type', 'element')}: {sel.get('selector', 'N/A')}")

    return "\n".join(formatted)


def _format_constraints(constraints: list) -> str:
    """Format constraints for display"""
    if not constraints:
        return ""

    return "Constraints:\n" + "\n".join(f"- {c}" for c in constraints)


def _format_examples(examples: list) -> str:
    """Format example scrapers"""
    if not examples:
        return ""

    formatted = []
    for i, example in enumerate(examples[:2], 1):  # Top 2 examples
        formatted.append(f"""
Example {i}: {example.get('title', 'Untitled')}
```python
{example.get('code', '# No code')}
```
""")

    return "\n".join(formatted)
