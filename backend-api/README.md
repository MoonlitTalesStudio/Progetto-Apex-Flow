
# B2B Micro-Service Sandbox: Logic & Resilience

**Developed by: Moonlit Tales Studio**

## Project Objective

This repository is the result of market research into the needs of top-tier tech companies, where **scalability** and **service resilience** are non-negotiable. The goal is to explore, both theoretically and practically, the use of **Docker**, asynchronous architectures, and data management between relational (PostgreSQL) and NoSQL (Redis) databases.

## AI-Assisted Development (Human-AI Collaboration)

The entire development and learning process was enhanced through the strategic use of **Gemini AI**. Artificial Intelligence was integrated to facilitate:

* **Brainstorming & Technology Discovery**: Exploring and selecting the most appropriate technologies and libraries for specific architectural challenges (e.g., choosing Redis Stack for JSON/Search capabilities).
* **Learning & Development (L&D)**: Accelerating the learning curve regarding advanced containerization concepts and Python asyncio patterns.
* **Technical Documentation**: Refining and optimizing this README to ensure concise, professional, and results-oriented communication.

## Infrastructure & Security (Docker-First)

The project was built from the ground up starting with container design, optimizing both communication and security:

* **Image Selection**: Chose `redis/redis-stack-server` to enable **RedisJSON** and **RedisSearch**, providing superior capabilities for structured data and complex querying compared to the standard Alpine version.
* **Resilient Message Broker**: Implemented a queuing system using `LPUSH` and `BRPOP` instead of standard Pub/Sub. This ensures no load events are lost even if the worker is temporarily offline.
* **Security & Least Privilege**:
* **Isolation**: Service communication is restricted to a private internal network with no unnecessary port exposure.
* **Multi-stage Build**: Separated the build environment from the runtime environment to exclude build tools from the final image, significantly reducing the attack surface.
* **User Security**: The application runs under a non-root user (`appuser`) to prevent potential privilege escalation.



## Service Logic & Data Management

### 1. Asynchronous Synchronization (Postgres → Redis)

The system utilizes **SQLModel** with the `asyncpg` driver to ensure that heavy database queries do not block the event loop.

* **Relational Integrity**: Explicit use of `Relationship` mapping ensures Postgres correctly handles constraints between tables (Products, Orders, Users), preventing orphaned data.
* **Data Transformation**: The worker manages type conversion (e.g., Postgres Decimal to Redis-compatible floats), ensuring cross-system compatibility.

### 2. RedisSearch Dialect 2

An advanced search index (`idx:catalogo`) was implemented to allow granular filtering on JSON documents:

* **Search Engine**: Leveraged TagFields, NumericFields, and TextFields for SKU-based lookups, category filtering, and price range queries.
* **Sync Logic**: Integrated a debounce mechanism (`asyncio.sleep(1)`) to ensure Redis completes document indexing before making them available for querying.

## Critical Analysis & Scalability

The codebase identifies its own architectural limits for future evolution:

* **Bottleneck**: The full reload approach (`dropindex`) is identified as a breaking point for massive datasets, suggesting a future transition toward batch processing or incremental updates.
* **Resilience**: The use of asynchronous sessions allows for the implementation of fail-safe logic to handle connection errors without compromising service integrity.