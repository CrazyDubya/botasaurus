# 🚀 Botasaurus Platform - Backend

**Status:** 🟢 Active Development (Phase 1)
**Version:** 1.0.0

This is the backend API for the Botasaurus intelligent automation platform.

---

## 📋 What's Implemented

### ✅ Phase 1: Foundation (In Progress)

#### Completed:
- [x] Project structure
- [x] Database schema (SQLAlchemy models)
- [x] Authentication system (JWT)
  - User registration
  - Login/logout
  - Token refresh
  - Password management
- [x] Core configuration system
- [x] FastAPI application setup
- [x] Middleware (CORS, logging, error handling)
- [x] Health check endpoints

#### In Progress:
- [ ] AI Copilot API
- [ ] Billing integration (Stripe)
- [ ] Usage tracking
- [ ] API documentation

#### Pending:
- [ ] Scrapers API
- [ ] Workflows API
- [ ] API Marketplace
- [ ] Data Pipelines

---

## 🏗️ Architecture

```
botasaurus_platform/
├── __init__.py
├── main.py                      # FastAPI app entry point
├── core/
│   ├── config.py                # Settings & configuration
│   ├── database.py              # Database connection
│   └── database/
│       └── models.py            # SQLAlchemy models
├── auth/                        # ✅ COMPLETE
│   ├── router.py                # Auth endpoints
│   ├── service.py               # Auth business logic
│   ├── schemas.py               # Pydantic models
│   └── dependencies.py          # Auth dependencies
├── ai/                          # 🚧 IN PROGRESS
│   └── ...
├── scrapers/                    # ⏳ PENDING
├── workflows/                   # ⏳ PENDING
├── marketplace/                 # ⏳ PENDING
└── pipelines/                   # ⏳ PENDING
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements-platform.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Set up database:**
```bash
# Create database
createdb botasaurus

# Run migrations (if using Alembic)
alembic upgrade head

# Or initialize directly
python -c "from botasaurus_platform.core.database import init_db; init_db()"
```

4. **Run the server:**
```bash
# Development mode (with auto-reload)
uvicorn botasaurus_platform.main:app --reload

# Production mode
uvicorn botasaurus_platform.main:app --host 0.0.0.0 --port 8000
```

5. **Access the API:**
- API Docs (Swagger): http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- Health Check: http://localhost:8000/health

---

## 🔧 Development

### Code Quality

```bash
# Run linter
ruff check botasaurus_platform/

# Format code
black botasaurus_platform/

# Sort imports
isort botasaurus_platform/

# Type checking
mypy botasaurus_platform/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=botasaurus_platform --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📚 API Documentation

### Authentication

**POST /api/auth/register**
Register a new user.

```json
Request:
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**POST /api/auth/login**
Login and get tokens.

```json
Request:
{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**GET /api/auth/me**
Get current user information (requires authentication).

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/auth/me
```

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),
  name VARCHAR(255),
  avatar_url TEXT,
  plan VARCHAR(50) DEFAULT 'free',
  is_active BOOLEAN DEFAULT TRUE,
  is_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);
```

### Sessions Table
```sql
CREATE TABLE sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  token VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

[See full schema in `botasaurus_platform/core/database/models.py`]

---

## 🔐 Security

- **Password Hashing:** bcrypt with salt
- **JWT Tokens:** HS256 algorithm
- **Token Expiry:** 30 minutes (access), 7 days (refresh)
- **CORS:** Configured for specified origins
- **Rate Limiting:** 60 requests/minute per IP
- **SQL Injection:** Prevented via SQLAlchemy ORM
- **XSS Prevention:** FastAPI automatic escaping

---

## 📊 Monitoring & Logging

- **Logging:** Structured JSON logs
- **Error Tracking:** Sentry integration
- **Metrics:** DataDog (coming soon)
- **Health Checks:** `/health` endpoint

---

## 🚢 Deployment

### Docker (Coming Soon)

```bash
docker-compose up -d
```

### AWS ECS (Coming Soon)

See `infrastructure/terraform/` for Terraform configuration.

---

## 📈 Roadmap

See [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) for detailed roadmap.

**Current Phase:** Phase 1 - Foundation (Weeks 1-12)
**Next Phase:** Phase 2 - AI Copilot MVP (Weeks 13-20)

---

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Run linters and tests
5. Submit PR

### Commit Convention

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
test: Add tests
refactor: Refactor code
chore: Update dependencies
```

---

## 📞 Support

- **Issues:** https://github.com/omkarcloud/botasaurus/issues
- **Discussions:** https://github.com/omkarcloud/botasaurus/discussions
- **Email:** support@botasaurus.com

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) file.

---

**Built with ❤️ by the Botasaurus team**
