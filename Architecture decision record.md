
---

## Architecture Decision Record (ADR-001)

### Oggetto: Scelta del Data Layer e del Framework Backend

#### 1. Framework: FastAPI + SQLAlchemy vs Django
**Decisione:** Utilizzo di **FastAPI** accoppiato a **SQLAlchemy** (libreria ORM esterna).

**Motivazione (Leggerezza e Containerizzazione):**
*   **Modularità vs Monolito:** Django è un framework "batteries-included" che porta con sé una struttura rigida e un peso considerevole in termini di dipendenze e memoria. In un'ottica di microservizi containerizzati, abbiamo optato per FastAPI per mantenere l'immagine Docker **lean** (leggera), installando solo ciò che è strettamente necessario.
*   **Efficienza delle Risorse:** FastAPI permette di gestire operazioni asincrone (`asyncio`) in modo nativo e ultra-performante, riducendo l'overhead del container e ottimizzando il consumo di CPU/RAM sotto carico.

#### 2. Data Access: ORM (SQLAlchemy) vs SQL Puro
**Decisione:** Implementazione di un **ORM (Object-Relational Mapping)** nonostante la potenziale perdita marginale di performance rispetto a query SQL manuali.

**Motivazione (Sicurezza, Velocità e Scalabilità):**
*   **Agnosticismo del Database:** L'uso di un ORM rende il sistema **DB-Agnostic**. Sebbene attualmente utilizziamo PostgreSQL, la logica di business rimane isolata dal dialetto SQL specifico. Questo permette di migrare o testare il sistema su motori diversi (es. SQLite per i test, CockroachDB per la scalabilità) senza riscrivere il codice.
*   **Sicurezza (SQL Sanitization):** L'ORM gestisce nativamente la parametrizzazione delle query, eliminando il rischio di **SQL Injection**. Questo garantisce una protezione "di serie" che con SQL puro richiederebbe sforzi manuali costanti e proni all'errore.
*   **Developer Velocity:** La mappatura dei dati in oggetti Python velocizza drasticamente lo sviluppo e la manutenzione. La leggibilità del codice migliora, riducendo il "debito tecnico" e facilitando il refactoring.
*   **Agnosticismo del Linguaggio (Modello Concettuale):** Definire lo schema tramite classi Python (modelli) crea una documentazione vivente della struttura dati che è più facile da tradurre concettualmente per altri membri del team o per futuri microservizi in altri linguaggi.

---

### Considerazioni sulle Performance
Siamo consapevoli che SQL puro permetta ottimizzazioni di basso livello (es. query ultra-complesse o tuning specifico). Tuttavia, la scelta è ricaduta sull'ORM per favorire la robustezza del sistema. Nei casi in cui le performance dovessero diventare un collo di bottiglia critico (es. calcoli analitici pesanti nel Worker), l'architettura scelta permette comunque l'esecuzione di **Raw SQL** mirato all'interno di sessioni SQLAlchemy, offrendoci il meglio dei due mondi.

---
