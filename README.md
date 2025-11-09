<div align="center">

# 🧠 ReasonOS

**AI Agent Operating System with Governance**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [5 Layers](#-the-5-layers)

</div>

---

## 📖 Overview

**ReasonOS** is an Operating System for autonomous AI agents that prevents hallucinations, enforces policies, and provides complete audit trails. Think of it as a safety layer between AI agents and your production systems.

### The Problem We Solve

- ❌ AI agents make mistakes and hallucinate code
- ❌ No governance over what AI can do
- ❌ No audit trail of AI actions
- ❌ Companies lose millions from AI errors

### The Solution

ReasonOS provides **5 layers of protection** between AI agents and your codebase:

1. **Semantic Graph** - Understands your entire codebase
2. **Hallucination Detector** - Validates AI-generated code
3. **Policy Engine** - Enforces approval workflows
4. **Sandbox Executor** - Tests changes safely
5. **Audit Logger** - Complete accountability

### 🎯 Key Features

- **🔍 Semantic Code Understanding** - Tree-sitter parsing + Neo4j graph database
- **�️ Hallucination Detection** - LLM-as-Judge validation (Claude/GPT-4)
- **� Policy Enforcement** - YAML-based approval workflows
- **🧪 Safe Execution** - Docker sandbox for isolated testing
- **� Complete Audit Trail** - Immutable event logging
- **⚡ Real-time UI** - React dashboard with WebSocket updates
- **� Enterprise Ready** - OAuth, JWT, RBAC security
- **🐳 Containerized** - Full Docker Compose setup

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (Backend)
- **Node.js 20+** (Frontend)
- **Docker & Docker Compose** (Containerization)
- **PostgreSQL 15+** (Database)
- **Redis 7+** (Caching)
- **Git** (Version control)

### Installation

```bash
# Clone the repository
git clone https://github.com/Motupallisailohith/ReasonOS.git
cd ReasonOS

# Run automated setup
make setup

# Start development environment
make run
```

### Manual Setup

```bash
# 1. Install Python dependencies
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Install Node dependencies
cd ../frontend
npm install

# 3. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 4. Initialize database
make db-migrate

# 5. Start services
# Terminal 1 - Backend
cd backend && python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Using Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🏗️ The 5 Layers

### Layer 1: Semantic Code Graph
**Tech:** Tree-sitter + Neo4j + Pinecone  
**Purpose:** Parse code, build dependency graphs, enable semantic search  
**Output:** Complete understanding of codebase structure and relationships

### Layer 2: Hallucination Detector
**Tech:** Claude API + AST validators + Type checkers  
**Purpose:** Validate AI-generated code for safety  
**Output:** Confidence score (0-100) indicating if code is safe

### Layer 3: Policy Engine
**Tech:** YAML policies + Python evaluator  
**Purpose:** Enforce approval workflows based on rules  
**Output:** APPROVE, REJECT, or REQUIRE_APPROVAL decisions

### Layer 4: Sandbox Executor
**Tech:** Docker + pytest/jest runners  
**Purpose:** Execute code changes in isolated environment  
**Output:** Test results, execution logs, resource usage

### Layer 5: Audit Logger
**Tech:** PostgreSQL + Merkle trees  
**Purpose:** Immutable logging of all events  
**Output:** Complete audit trail for compliance

---

## 🏗️ Architecture

```
ReasonOS/
├── backend/               # Python FastAPI backend
│   ├── app/
│   │   ├── api/          # API routes and endpoints
│   │   ├── core/         # Core business logic
│   │   ├── models/       # Database models
│   │   ├── services/     # Business services
│   │   └── utils/        # Utilities
│   └── tests/            # Backend tests
│
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── services/     # API services
│   │   └── utils/        # Utilities
│   └── tests/            # Frontend tests
│
├── infrastructure/       # Infrastructure as Code
│   ├── terraform/        # Terraform configs
│   └── kubernetes/       # K8s manifests
│
├── scripts/              # Automation scripts
├── docs/                 # Documentation
└── .github/              # CI/CD workflows
```

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- Alembic (Database migrations)
- Celery (Task queue)
- Redis (Caching)
- PostgreSQL (Database)

**Frontend:**
- React 18 with TypeScript
- Vite (Build tool)
- TanStack Query (Data fetching)
- Tailwind CSS (Styling)
- Zustand (State management)

**Infrastructure:**
- Azure Cloud Platform
- Docker & Kubernetes
- Terraform (IaC)
- GitHub Actions (CI/CD)
- Azure Monitor (Observability)

---

## 🧪 Testing

```bash
# Run all tests
make test

# Backend tests
make test-backend

# Frontend tests
make test-frontend

# E2E tests
make test-e2e

# Generate coverage report
make coverage
```

---

## � Example Flow

```
Developer: "ReasonOS, refactor this repo"
    ↓
┌─────────────────────────────────────┐
│ Layer 1: Semantic Graph             │
│ "Found 5 files to update"           │
│ ✅ PASS                              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Layer 2: Hallucination Check        │
│ "Code looks valid"                  │
│ ✅ PASS (92% confidence)            │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Layer 3: Policy Check               │
│ "Requires tech lead approval"       │
│ ⏸️ REQUIRES_APPROVAL                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Human Approval                      │
│ Tech lead clicks "APPROVE"          │
│ ✅ APPROVED                          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Layer 4: Sandbox Test               │
│ "All 45 tests passed"               │
│ ✅ TESTS_PASS                        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Layer 5: Audit Log                  │
│ "Event logged immutably"            │
│ ✅ LOGGED                            │
└─────────────────────────────────────┘
    ↓
✅ CHANGES MERGED TO PRODUCTION
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Maintainer:** [@Motupallisailohith](https://github.com/Motupallisailohith)

---

## 🙏 Acknowledgments

- Azure OpenAI for AI capabilities
- Open-source community for amazing tools
- Contributors and supporters

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Motupallisailohith/ReasonOS/issues)
- **Questions**: Open a discussion or issue

---

<div align="center">

**Built with ❤️ by the ReasonOS Team**

[⭐ Star us on GitHub](https://github.com/Motupallisailohith/ReasonOS) | [🐛 Report Bug](https://github.com/Motupallisailohith/ReasonOS/issues) | [✨ Request Feature](https://github.com/Motupallisailohith/ReasonOS/issues)

</div>
