"""
Workflow Templates
==================

Pre-built workflow templates for common scraping tasks.
"""

from .schemas import (
    WorkflowTemplate, WorkflowDefinition, WorkflowNode, NodeConnection,
    WorkflowSettings, NodePosition, NodeType, BrowserType,
    NavigateNodeConfig, ExtractTextNodeConfig, ExtractMultipleNodeConfig,
    SaveJsonNodeConfig, ClickNodeConfig, WaitNodeConfig, BaseNodeConfig,
    TemplateCategory
)


# ==================== Template Categories ====================

TEMPLATE_CATEGORIES = [
    TemplateCategory(
        id="e-commerce",
        name="E-Commerce",
        description="Templates for scraping online stores",
        icon="shopping-cart",
        template_count=3
    ),
    TemplateCategory(
        id="news",
        name="News & Articles",
        description="Scrape news sites and blogs",
        icon="newspaper",
        template_count=2
    ),
    TemplateCategory(
        id="social",
        name="Social Media",
        description="Extract data from social platforms",
        icon="users",
        template_count=2
    ),
    TemplateCategory(
        id="data",
        name="Data Extraction",
        description="General purpose data scraping",
        icon="database",
        template_count=3
    ),
    TemplateCategory(
        id="monitoring",
        name="Monitoring",
        description="Track changes on websites",
        icon="eye",
        template_count=2
    )
]


# ==================== E-Commerce Templates ====================

def create_product_listing_template() -> WorkflowTemplate:
    """Template for scraping product listings"""

    definition = WorkflowDefinition(
        nodes=[
            WorkflowNode(
                id="start",
                config=BaseNodeConfig(type=NodeType.START, label="Start"),
                position=NodePosition(x=100, y=100)
            ),
            WorkflowNode(
                id="navigate",
                config=NavigateNodeConfig(
                    type=NodeType.NAVIGATE,
                    label="Navigate to Product Page",
                    url="https://example.com/products",
                    wait_until="networkidle"
                ),
                position=NodePosition(x=100, y=200)
            ),
            WorkflowNode(
                id="extract_products",
                config=ExtractMultipleNodeConfig(
                    type=NodeType.EXTRACT_MULTIPLE,
                    label="Extract Product Data",
                    container_selector=".product-item",
                    fields=[
                        {"name": "title", "selector": ".product-title"},
                        {"name": "price", "selector": ".product-price"},
                        {"name": "image", "selector": "img", "attribute": "src"},
                        {"name": "link", "selector": "a", "attribute": "href"}
                    ],
                    output_key="products"
                ),
                position=NodePosition(x=100, y=300)
            ),
            WorkflowNode(
                id="save",
                config=SaveJsonNodeConfig(
                    type=NodeType.SAVE_JSON,
                    label="Save Results",
                    data_key="products"
                ),
                position=NodePosition(x=100, y=400)
            ),
            WorkflowNode(
                id="end",
                config=BaseNodeConfig(type=NodeType.END, label="End"),
                position=NodePosition(x=100, y=500)
            )
        ],
        connections=[
            NodeConnection(source_node_id="start", target_node_id="navigate"),
            NodeConnection(source_node_id="navigate", target_node_id="extract_products"),
            NodeConnection(source_node_id="extract_products", target_node_id="save"),
            NodeConnection(source_node_id="save", target_node_id="end")
        ]
    )

    return WorkflowTemplate(
        id="product-listing",
        name="Product Listing Scraper",
        description="Scrape product information from e-commerce listings",
        category="e-commerce",
        tags=["e-commerce", "products", "listings"],
        difficulty="beginner",
        estimated_time="2 minutes",
        definition=definition,
        settings=WorkflowSettings(),
        example_output={
            "products": [
                {
                    "title": "Laptop XYZ",
                    "price": "$999.99",
                    "image": "https://example.com/img/laptop.jpg",
                    "link": "https://example.com/product/123"
                }
            ]
        }
    )


def create_product_details_template() -> WorkflowTemplate:
    """Template for scraping individual product details"""

    definition = WorkflowDefinition(
        nodes=[
            WorkflowNode(
                id="start",
                config=BaseNodeConfig(type=NodeType.START, label="Start"),
                position=NodePosition(x=100, y=100)
            ),
            WorkflowNode(
                id="navigate",
                config=NavigateNodeConfig(
                    type=NodeType.NAVIGATE,
                    label="Go to Product",
                    url="https://example.com/product/123",
                    wait_until="networkidle"
                ),
                position=NodePosition(x=100, y=200)
            ),
            WorkflowNode(
                id="extract_title",
                config=ExtractTextNodeConfig(
                    type=NodeType.EXTRACT_TEXT,
                    label="Extract Title",
                    selector="h1.product-title",
                    output_key="title"
                ),
                position=NodePosition(x=50, y=300)
            ),
            WorkflowNode(
                id="extract_price",
                config=ExtractTextNodeConfig(
                    type=NodeType.EXTRACT_TEXT,
                    label="Extract Price",
                    selector=".product-price",
                    output_key="price"
                ),
                position=NodePosition(x=150, y=300)
            ),
            WorkflowNode(
                id="extract_description",
                config=ExtractTextNodeConfig(
                    type=NodeType.EXTRACT_TEXT,
                    label="Extract Description",
                    selector=".product-description",
                    output_key="description"
                ),
                position=NodePosition(x=250, y=300)
            ),
            WorkflowNode(
                id="save",
                config=SaveJsonNodeConfig(
                    type=NodeType.SAVE_JSON,
                    label="Save Product Data"
                ),
                position=NodePosition(x=150, y=400)
            ),
            WorkflowNode(
                id="end",
                config=BaseNodeConfig(type=NodeType.END, label="End"),
                position=NodePosition(x=150, y=500)
            )
        ],
        connections=[
            NodeConnection(source_node_id="start", target_node_id="navigate"),
            NodeConnection(source_node_id="navigate", target_node_id="extract_title"),
            NodeConnection(source_node_id="navigate", target_node_id="extract_price"),
            NodeConnection(source_node_id="navigate", target_node_id="extract_description"),
            NodeConnection(source_node_id="extract_title", target_node_id="save"),
            NodeConnection(source_node_id="extract_price", target_node_id="save"),
            NodeConnection(source_node_id="extract_description", target_node_id="save"),
            NodeConnection(source_node_id="save", target_node_id="end")
        ]
    )

    return WorkflowTemplate(
        id="product-details",
        name="Product Details Scraper",
        description="Extract detailed information from a single product page",
        category="e-commerce",
        tags=["e-commerce", "product", "details"],
        difficulty="beginner",
        estimated_time="1 minute",
        definition=definition,
        settings=WorkflowSettings(),
        example_output={
            "title": "Laptop XYZ Pro",
            "price": "$1,299.99",
            "description": "Powerful laptop with 16GB RAM..."
        }
    )


# ==================== News Templates ====================

def create_news_articles_template() -> WorkflowTemplate:
    """Template for scraping news articles"""

    definition = WorkflowDefinition(
        nodes=[
            WorkflowNode(
                id="start",
                config=BaseNodeConfig(type=NodeType.START, label="Start"),
                position=NodePosition(x=100, y=100)
            ),
            WorkflowNode(
                id="navigate",
                config=NavigateNodeConfig(
                    type=NodeType.NAVIGATE,
                    label="Go to News Site",
                    url="https://news.example.com",
                    wait_until="networkidle"
                ),
                position=NodePosition(x=100, y=200)
            ),
            WorkflowNode(
                id="extract_articles",
                config=ExtractMultipleNodeConfig(
                    type=NodeType.EXTRACT_MULTIPLE,
                    label="Extract Articles",
                    container_selector="article",
                    fields=[
                        {"name": "headline", "selector": "h2"},
                        {"name": "summary", "selector": ".summary"},
                        {"name": "author", "selector": ".author"},
                        {"name": "date", "selector": ".date"},
                        {"name": "link", "selector": "a", "attribute": "href"}
                    ],
                    output_key="articles",
                    limit=20
                ),
                position=NodePosition(x=100, y=300)
            ),
            WorkflowNode(
                id="save",
                config=SaveJsonNodeConfig(
                    type=NodeType.SAVE_JSON,
                    label="Save Articles",
                    data_key="articles"
                ),
                position=NodePosition(x=100, y=400)
            ),
            WorkflowNode(
                id="end",
                config=BaseNodeConfig(type=NodeType.END, label="End"),
                position=NodePosition(x=100, y=500)
            )
        ],
        connections=[
            NodeConnection(source_node_id="start", target_node_id="navigate"),
            NodeConnection(source_node_id="navigate", target_node_id="extract_articles"),
            NodeConnection(source_node_id="extract_articles", target_node_id="save"),
            NodeConnection(source_node_id="save", target_node_id="end")
        ]
    )

    return WorkflowTemplate(
        id="news-articles",
        name="News Articles Scraper",
        description="Scrape headlines and articles from news websites",
        category="news",
        tags=["news", "articles", "headlines"],
        difficulty="beginner",
        estimated_time="2 minutes",
        definition=definition,
        settings=WorkflowSettings(),
        example_output={
            "articles": [
                {
                    "headline": "Breaking News Title",
                    "summary": "Article summary...",
                    "author": "John Doe",
                    "date": "2025-01-15",
                    "link": "/article/123"
                }
            ]
        }
    )


# ==================== Social Media Templates ====================

def create_social_profile_template() -> WorkflowTemplate:
    """Template for scraping social media profiles"""

    definition = WorkflowDefinition(
        nodes=[
            WorkflowNode(
                id="start",
                config=BaseNodeConfig(type=NodeType.START, label="Start"),
                position=NodePosition(x=100, y=100)
            ),
            WorkflowNode(
                id="navigate",
                config=NavigateNodeConfig(
                    type=NodeType.NAVIGATE,
                    label="Go to Profile",
                    url="https://social.example.com/username",
                    wait_until="networkidle"
                ),
                position=NodePosition(x=100, y=200)
            ),
            WorkflowNode(
                id="wait_load",
                config=WaitNodeConfig(
                    type=NodeType.WAIT,
                    label="Wait for Content",
                    wait_type="time",
                    duration=2
                ),
                position=NodePosition(x=100, y=300)
            ),
            WorkflowNode(
                id="extract_profile",
                config=ExtractMultipleNodeConfig(
                    type=NodeType.EXTRACT_MULTIPLE,
                    label="Extract Posts",
                    container_selector=".post",
                    fields=[
                        {"name": "text", "selector": ".post-content"},
                        {"name": "likes", "selector": ".likes-count"},
                        {"name": "date", "selector": ".post-date"},
                        {"name": "image", "selector": "img", "attribute": "src"}
                    ],
                    output_key="posts",
                    limit=10
                ),
                position=NodePosition(x=100, y=400)
            ),
            WorkflowNode(
                id="save",
                config=SaveJsonNodeConfig(
                    type=NodeType.SAVE_JSON,
                    label="Save Posts",
                    data_key="posts"
                ),
                position=NodePosition(x=100, y=500)
            ),
            WorkflowNode(
                id="end",
                config=BaseNodeConfig(type=NodeType.END, label="End"),
                position=NodePosition(x=100, y=600)
            )
        ],
        connections=[
            NodeConnection(source_node_id="start", target_node_id="navigate"),
            NodeConnection(source_node_id="navigate", target_node_id="wait_load"),
            NodeConnection(source_node_id="wait_load", target_node_id="extract_profile"),
            NodeConnection(source_node_id="extract_profile", target_node_id="save"),
            NodeConnection(source_node_id="save", target_node_id="end")
        ]
    )

    return WorkflowTemplate(
        id="social-profile",
        name="Social Media Profile Scraper",
        description="Extract posts and content from social media profiles",
        category="social",
        tags=["social-media", "profile", "posts"],
        difficulty="intermediate",
        estimated_time="3 minutes",
        definition=definition,
        settings=WorkflowSettings(),
        example_output={
            "posts": [
                {
                    "text": "Check out my new post!",
                    "likes": "142",
                    "date": "2 hours ago",
                    "image": "https://example.com/img/post.jpg"
                }
            ]
        }
    )


# ==================== Data Extraction Templates ====================

def create_table_scraper_template() -> WorkflowTemplate:
    """Template for scraping HTML tables"""

    definition = WorkflowDefinition(
        nodes=[
            WorkflowNode(
                id="start",
                config=BaseNodeConfig(type=NodeType.START, label="Start"),
                position=NodePosition(x=100, y=100)
            ),
            WorkflowNode(
                id="navigate",
                config=NavigateNodeConfig(
                    type=NodeType.NAVIGATE,
                    label="Navigate to Page",
                    url="https://example.com/data-table",
                    wait_until="networkidle"
                ),
                position=NodePosition(x=100, y=200)
            ),
            WorkflowNode(
                id="extract_table",
                config=ExtractMultipleNodeConfig(
                    type=NodeType.EXTRACT_MULTIPLE,
                    label="Extract Table Rows",
                    container_selector="table tbody tr",
                    fields=[
                        {"name": "col1", "selector": "td:nth-child(1)"},
                        {"name": "col2", "selector": "td:nth-child(2)"},
                        {"name": "col3", "selector": "td:nth-child(3)"},
                        {"name": "col4", "selector": "td:nth-child(4)"}
                    ],
                    output_key="table_data"
                ),
                position=NodePosition(x=100, y=300)
            ),
            WorkflowNode(
                id="save",
                config=SaveJsonNodeConfig(
                    type=NodeType.SAVE_JSON,
                    label="Save Table Data",
                    data_key="table_data"
                ),
                position=NodePosition(x=100, y=400)
            ),
            WorkflowNode(
                id="end",
                config=BaseNodeConfig(type=NodeType.END, label="End"),
                position=NodePosition(x=100, y=500)
            )
        ],
        connections=[
            NodeConnection(source_node_id="start", target_node_id="navigate"),
            NodeConnection(source_node_id="navigate", target_node_id="extract_table"),
            NodeConnection(source_node_id="extract_table", target_node_id="save"),
            NodeConnection(source_node_id="save", target_node_id="end")
        ]
    )

    return WorkflowTemplate(
        id="table-scraper",
        name="HTML Table Scraper",
        description="Extract data from HTML tables",
        category="data",
        tags=["table", "data", "extraction"],
        difficulty="beginner",
        estimated_time="1 minute",
        definition=definition,
        settings=WorkflowSettings(),
        example_output={
            "table_data": [
                {"col1": "Value 1", "col2": "Value 2", "col3": "Value 3", "col4": "Value 4"}
            ]
        }
    )


# ==================== Template Registry ====================

ALL_TEMPLATES = [
    create_product_listing_template(),
    create_product_details_template(),
    create_news_articles_template(),
    create_social_profile_template(),
    create_table_scraper_template(),
]


def get_all_templates() -> list[WorkflowTemplate]:
    """Get all available templates"""
    return ALL_TEMPLATES


def get_template_by_id(template_id: str) -> WorkflowTemplate | None:
    """Get template by ID"""
    return next((t for t in ALL_TEMPLATES if t.id == template_id), None)


def get_templates_by_category(category: str) -> list[WorkflowTemplate]:
    """Get templates in a category"""
    return [t for t in ALL_TEMPLATES if t.category == category]


def get_template_categories() -> list[TemplateCategory]:
    """Get all template categories"""
    return TEMPLATE_CATEGORIES
