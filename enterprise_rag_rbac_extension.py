
# Enterprise RAG Intelligence System — RBAC Extension
#
# This file adds:
#   - Multi-format data ingestion (PDF, CSV, JSON, TXT)
#   - Role-Based Access Control (RBAC)
#   - Query routing
#   - Explainability (citations, confidence, trace)
#   - Synthetic enterprise dataset generation


import json
import csv
import os
import re
import math
import random
import requests
from typing import List, Dict, Optional
from datetime import datetime


VECTOR_DB_URL = "http://localhost:8080"  # existing C++ backend

# If Ollama/C++ backend not running, we use fallback mode
FALLBACK_MODE = True # Set False if backend is running



def create_synthetic_dataset():
    """
    Creates synthetic enterprise documents simulating real
    enterprise data across multiple formats and departments.
    """

    # --- PDF-like text documents ---
    documents = {
        "HR_Policy.txt": {
            "content": """HR POLICY DOCUMENT - CONFIDENTIAL
Department: Human Resources
Version: 2.1 | Updated: June 2026

LEAVE POLICY:
Employees are entitled to 20 days paid annual leave.
Leave requests must be submitted 5 days in advance.
Sick leave: 10 days per year with medical certificate.
Maternity leave: 26 weeks as per government regulations.
Paternity leave: 15 days.

PERFORMANCE REVIEW:
Annual reviews conducted every December.
Mid-year check-ins in June.
KPIs are set at the start of each financial year.

SALARY REVISION:
Salary revisions happen annually in April.
Average increment: 8-12% based on performance rating.
            """,
            "allowed_roles": ["HR", "Admin"],
            "department": "HR",
            "doc_type": "PDF"
        },

        "Finance_Report_Q3.txt": {
            "content": """FINANCE REPORT - Q3 2026 - RESTRICTED
Department: Finance
Prepared by: CFO Office

REVENUE SUMMARY:
Total Q3 Revenue: $4.5 Million
Growth vs Q2: +12%
Growth vs Q3 2025: +28%

TOP PERFORMING PRODUCTS:
1. CloudSync Pro: $1.2M revenue, 1200 units sold
2. DataVault Enterprise: $0.9M revenue, 450 units
3. SecureLink API: $0.7M revenue, 2100 subscriptions

EXPENSES:
Total Operating Expenses: $2.8M
Infrastructure: $1.1M (+3% due to server upgrades)
Marketing: $0.8M
HR & Salaries: $0.9M

NET PROFIT: $1.7M (37.7% margin)

FORECAST Q4:
Projected revenue: $5.2M
Expected growth: 15%
            """,
            "allowed_roles": ["Finance", "Admin", "CEO"],
            "department": "Finance",
            "doc_type": "PDF"
        },

        "Compliance_Audit.txt": {
            "content": """COMPLIANCE AUDIT REPORT 2026 - CONFIDENTIAL
Audit Period: Jan 2026 - June 2026
Conducted by: External Auditors - PwC

FINDINGS:
3 minor non-conformities identified in data handling procedures.
All issues resolved within the 30-day remediation window.

DATA PRIVACY:
GDPR compliance: PASSED
Data retention policies: PASSED
User consent mechanisms: PASSED with minor recommendations

SECURITY COMPLIANCE:
ISO 27001 audit: PASSED
SOC2 Type II: IN PROGRESS (expected completion Aug 2026)
Penetration testing: Completed, 2 medium vulnerabilities patched

RECOMMENDATIONS:
1. Implement automated data classification tagging
2. Strengthen employee security training
3. Review third-party vendor access controls quarterly
            """,
            "allowed_roles": ["Compliance", "Legal", "Admin", "CEO"],
            "department": "Compliance",
            "doc_type": "PDF"
        },

        "Security_Guidelines.txt": {
            "content": """SECURITY GUIDELINES - ALL EMPLOYEES
Classification: Internal Use Only

PASSWORD POLICY:
Minimum 12 characters required.
Must include: uppercase, lowercase, numbers, special characters.
Password rotation: Every 90 days.
No reuse of last 10 passwords.

MULTI-FACTOR AUTHENTICATION:
MFA mandatory for all systems from July 2026.
Approved MFA apps: Google Authenticator, Microsoft Authenticator.

INCIDENT REPORTING:
All security incidents must be reported within 2 hours.
Contact: security@company.com or call ext. 911.
Do not attempt to investigate incidents independently.

DEVICE POLICY:
Company devices only for sensitive data access.
Personal devices require MDM enrollment.
Full disk encryption mandatory on all devices.
            """,
            "allowed_roles": ["Admin", "Security", "Employee", "HR", "Finance", "Engineering"],
            "department": "Security",
            "doc_type": "PDF"
        }
    }

    # --- CSV structured data ---
    csv_data = {
        "employees.csv": {
            "headers": ["emp_id", "name", "department", "role", "salary", "manager", "joined"],
            "rows": [
                ["E001", "Alice Johnson", "Finance", "Finance Manager", "95000", "CEO", "2019-03-15"],
                ["E002", "Bob Smith", "Engineering", "Senior Engineer", "105000", "CTO", "2020-07-01"],
                ["E003", "Charlie Brown", "HR", "HR Manager", "85000", "CEO", "2018-11-20"],
                ["E004", "Diana Prince", "Security", "Security Lead", "110000", "CTO", "2021-02-10"],
                ["E005", "Eve Wilson", "Marketing", "Marketing Exec", "75000", "CMO", "2022-05-30"],
                ["E006", "Frank Castle", "Legal", "Legal Counsel", "120000", "CEO", "2017-08-15"],
            ],
            "allowed_roles": ["HR", "Admin"],
            "doc_type": "CSV"
        },
        "sales.csv": {
            "headers": ["product", "units_sold", "revenue", "region", "quarter", "sales_rep"],
            "rows": [
                ["CloudSync Pro", "1200", "240000", "North America", "Q3 2026", "Alice J"],
                ["DataVault Enterprise", "450", "900000", "Europe", "Q3 2026", "Bob K"],
                ["SecureLink API", "2100", "210000", "Asia Pacific", "Q3 2026", "Carol M"],
                ["CloudSync Pro", "800", "160000", "Europe", "Q3 2026", "David L"],
                ["DataVault Enterprise", "300", "600000", "North America", "Q3 2026", "Eve R"],
            ],
            "allowed_roles": ["Finance", "Sales", "Admin", "CEO"],
            "doc_type": "CSV"
        }
    }

    # --- JSON logs ---
    json_logs = {
        "payment_logs.json": {
            "logs": [
                {"timestamp": "2026-06-10T14:23:11", "level": "ERROR", "event": "payment_failure",
                 "transaction_id": "TX9821", "amount": 5200, "currency": "USD",
                 "retry_count": 3, "status": "FAILED", "reason": "Gateway timeout"},
                {"timestamp": "2026-06-11T09:15:44", "level": "INFO", "event": "payment_success",
                 "transaction_id": "TX9822", "amount": 1500, "currency": "USD",
                 "retry_count": 0, "status": "SUCCESS"},
                {"timestamp": "2026-06-12T16:45:02", "level": "WARNING", "event": "payment_delay",
                 "transaction_id": "TX9823", "amount": 8900, "currency": "USD",
                 "retry_count": 1, "status": "PENDING", "reason": "Bank processing delay"},
            ],
            "allowed_roles": ["Finance", "Admin", "Engineering"],
            "doc_type": "JSON_LOG"
        },
        "security_logs.json": {
            "logs": [
                {"timestamp": "2026-06-11T02:14:33", "level": "WARNING", "event": "failed_login",
                 "user_id": "U0045", "ip": "192.168.1.105", "attempts": 5,
                 "action": "account_locked", "reason": "Brute force detected"},
                {"timestamp": "2026-06-12T23:58:01", "level": "CRITICAL", "event": "unauthorized_access",
                 "user_id": "U0089", "resource": "Finance_Report_Q3.txt",
                 "action": "access_denied", "reason": "Insufficient role permissions"},
                {"timestamp": "2026-06-13T11:22:45", "level": "INFO", "event": "mfa_enabled",
                 "user_id": "U0012", "action": "mfa_setup_complete"},
            ],
            "allowed_roles": ["Admin", "Security"],
            "doc_type": "JSON_LOG"
        }
    }

    # --- RBAC: User role mappings ---
    user_roles = {
        "alice": {"roles": ["Finance", "Admin"], "department": "Finance", "clearance": "HIGH"},
        "bob": {"roles": ["Engineering", "Employee"], "department": "Engineering", "clearance": "MEDIUM"},
        "charlie": {"roles": ["HR", "Admin"], "department": "HR", "clearance": "HIGH"},
        "diana": {"roles": ["Security", "Admin"], "department": "Security", "clearance": "HIGH"},
        "eve": {"roles": ["Employee"], "department": "Marketing", "clearance": "LOW"},
        "frank": {"roles": ["Compliance", "Legal", "Admin"], "department": "Legal", "clearance": "HIGH"},
        "ceo_user": {"roles": ["CEO", "Admin", "Finance", "HR", "Legal"], "department": "Executive", "clearance": "TOP"},
    }

    return documents, csv_data, json_logs, user_roles


# ============================================================
# 2. DATA INGESTION — Parse multiple formats into chunks
# ============================================================

def ingest_text_document(name: str, data: Dict) -> List[Dict]:
    """Chunk a text/PDF document into pieces with metadata"""
    content = data["content"]
    chunks = []
    # Split into ~200 word chunks
    words = content.split()
    chunk_size = 200
    overlap = 30
    i = 0
    chunk_num = 0
    while i < len(words):
        chunk_words = words[i:i+chunk_size]
        chunk_text = " ".join(chunk_words)
        chunks.append({
            "id": f"{name}_chunk{chunk_num}",
            "source": name,
            "content": chunk_text,
            "doc_type": data["doc_type"],
            "allowed_roles": data["allowed_roles"],
            "department": data.get("department", "General"),
            "chunk_index": chunk_num
        })
        i += chunk_size - overlap
        chunk_num += 1
    return chunks

def ingest_csv(name: str, data: Dict) -> List[Dict]:
    """Convert CSV rows to readable text chunks"""
    chunks = []
    headers = data["headers"]
    for i, row in enumerate(data["rows"]):
        # Convert row to natural language
        row_text = f"Record from {name}: " + ", ".join(
            f"{h} is {v}" for h, v in zip(headers, row)
        )
        chunks.append({
            "id": f"{name}_row{i}",
            "source": name,
            "content": row_text,
            "doc_type": data["doc_type"],
            "allowed_roles": data["allowed_roles"],
            "department": "Data",
            "chunk_index": i
        })
    return chunks

def ingest_json_logs(name: str, data: Dict) -> List[Dict]:
    """Convert JSON log entries to readable text chunks"""
    chunks = []
    for i, log in enumerate(data["logs"]):
        # Convert log to readable sentence
        log_text = f"Log entry from {name}: " + " | ".join(
            f"{k}: {v}" for k, v in log.items()
        )
        chunks.append({
            "id": f"{name}_log{i}",
            "source": name,
            "content": log_text,
            "doc_type": data["doc_type"],
            "allowed_roles": data["allowed_roles"],
            "department": "Operations",
            "chunk_index": i
        })
    return chunks

def ingest_all_data() -> List[Dict]:
    """Ingest all enterprise data sources into unified chunk list"""
    documents, csv_data, json_logs, _ = create_synthetic_dataset()
    all_chunks = []

    print(" Ingesting enterprise data sources...")

    for name, data in documents.items():
        chunks = ingest_text_document(name, data)
        all_chunks.extend(chunks)
        print(f"    {name}: {len(chunks)} chunks")

    for name, data in csv_data.items():
        chunks = ingest_csv(name, data)
        all_chunks.extend(chunks)
        print(f"    {name}: {len(chunks)} chunks")

    for name, data in json_logs.items():
        chunks = ingest_json_logs(name, data)
        all_chunks.extend(chunks)
        print(f"    {name}: {len(chunks)} chunks")

    print(f"\n Total chunks ingested: {len(all_chunks)}")
    return all_chunks



class RBACManager:
    """
    Role-Based Access Control Manager.
    Enforces access policies at retrieval level — BEFORE LLM sees data.
    This is the only truly secure approach. Post-generation filtering
    still risks data leakage through the LLM's internal processing.
    """

    def __init__(self, user_roles: Dict):
        self.user_roles = user_roles

    def get_user_roles(self, user_id: str) -> List[str]:
        """Get roles for a user"""
        user = self.user_roles.get(user_id)
        if not user:
            return []
        return user["roles"]

    def filter_chunks(self, chunks: List[Dict], user_id: str) -> tuple:
        """
        Filter chunks to only those the user is authorized to see.
        Returns (authorized_chunks, denied_count)
        """
        user_roles = self.get_user_roles(user_id)
        if not user_roles:
            return [], len(chunks)

        authorized = []
        denied = 0
        for chunk in chunks:
            allowed = chunk.get("allowed_roles", [])
            if any(role in allowed for role in user_roles):
                authorized.append(chunk)
            else:
                denied += 1

        return authorized, denied

    def check_access(self, user_id: str, required_roles: List[str]) -> bool:
        """Check if user has any of the required roles"""
        user_roles = self.get_user_roles(user_id)
        return any(role in required_roles for role in user_roles)



def route_query(query: str) -> List[str]:
    """
    Intelligently routes query to relevant data source types.
    Avoids unnecessary searching across all sources.
    """
    query_lower = query.lower()
    sources = []

    routing_rules = {
        "PDF": ["policy", "leave", "compliance", "audit", "security guideline",
                "procedure", "regulation", "standard", "revenue", "budget", "forecast"],
        "CSV": ["employee", "salary", "sales", "product", "units", "record",
                "staff", "team", "department", "revenue", "quarter"],
        "JSON_LOG": ["log", "error", "failed", "warning", "attack", "login",
                     "transaction", "payment", "incident", "breach", "attempt"]
    }

    for doc_type, keywords in routing_rules.items():
        if any(kw in query_lower for kw in keywords):
            sources.append(doc_type)

    # Default: search all
    if not sources:
        sources = ["PDF", "CSV", "JSON_LOG"]

    return list(set(sources))



class SimpleRetriever:
    """
    Lightweight retrieval using TF-IDF style scoring + BM25.
    Used as fallback when the C++ Ollama backend is not running.
    In production, this calls the existing /doc/ask endpoint.
    """

    def __init__(self, chunks: List[Dict]):
        self.chunks = chunks
        self.vocab = self._build_vocab()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _build_vocab(self) -> Dict[str, int]:
        vocab = {}
        for chunk in self.chunks:
            for token in self._tokenize(chunk["content"]):
                vocab[token] = vocab.get(token, 0) + 1
        return vocab

    def _bm25_score(self, query: str, doc_text: str) -> float:
        """BM25 scoring"""
        query_tokens = self._tokenize(query)
        doc_tokens = self._tokenize(doc_text)
        doc_len = len(doc_tokens)
        avg_doc_len = 80
        k1, b = 1.5, 0.75
        N = len(self.chunks)
        score = 0.0
        for token in query_tokens:
            tf = doc_tokens.count(token)
            if tf > 0:
                df = sum(1 for c in self.chunks if token in self._tokenize(c["content"]))
                idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
                tf_score = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avg_doc_len))
                score += idf * tf_score
        return score

    def _semantic_score(self, query: str, doc_text: str) -> float:
        """Simple word overlap semantic score"""
        q_tokens = set(self._tokenize(query))
        d_tokens = set(self._tokenize(doc_text))
        if not q_tokens or not d_tokens:
            return 0.0
        intersection = q_tokens & d_tokens
        return len(intersection) / math.sqrt(len(q_tokens) * len(d_tokens))

    def retrieve(self, query: str, authorized_chunks: List[Dict],
                 target_sources: List[str], top_k: int = 3) -> List[Dict]:
        """Hybrid retrieval: semantic + BM25 on authorized chunks only"""

        # Filter by routed doc types
        routed = [c for c in authorized_chunks if c["doc_type"] in target_sources]
        if not routed:
            routed = authorized_chunks  # fallback to all authorized

        results = []
        for chunk in routed:
            sem = self._semantic_score(query, chunk["content"])
            bm25 = self._bm25_score(query, chunk["content"])
            # Normalize BM25
            bm25_norm = min(bm25 / 10.0, 1.0)
            # Hybrid score
            hybrid = 0.5 * sem + 0.5 * bm25_norm
            results.append({
                "chunk": chunk,
                "score": round(hybrid, 4),
                "semantic_score": round(sem, 4),
                "bm25_score": round(bm25, 4)
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


def generate_response(query: str, retrieved: List[Dict],
                      user_id: str, user_roles: List[str]) -> Dict:
    """
    Generates grounded response from authorized retrieved context.
    In production: calls the existing /doc/ask endpoint on C++ backend.
    Here: simulates grounded generation with citation support.
    """
    if not retrieved:
        return {
            "answer": "I could not find any relevant information you are authorized to access for this query.",
            "sources": [],
            "confidence": 0.0,
            "citations": []
        }

    context_parts = []
    sources = []
    citations = []
    total_score = 0

    for i, item in enumerate(retrieved):
        chunk = item["chunk"]
        context_parts.append(f"[Source {i+1} - {chunk['source']}]:\n{chunk['content']}")
        sources.append({
            "source": chunk["source"],
            "doc_type": chunk["doc_type"],
            "department": chunk["department"],
            "relevance_score": item["score"],
            "chunk_id": chunk["id"]
        })
        citations.append(f"[{i+1}] {chunk['source']} (Relevance: {item['score']*100:.1f}%)")
        total_score += item["score"]

    avg_confidence = round((total_score / len(retrieved)) * 100, 1)
    context = "\n\n".join(context_parts)

    answer = f"""Based on authorized enterprise documents, here is the response to your query:

"{query}"

--- Retrieved Context ---
{context}

--- Answer ---
The above context from {len(retrieved)} authorized source(s) addresses your query.
All information is retrieved from documents you are authorized to access based on your role(s): {', '.join(user_roles)}.

Note: This response is strictly grounded in retrieved documents. No information beyond the provided context has been used."""

    return {
        "answer": answer,
        "sources": sources,
        "citations": citations,
        "confidence": min(avg_confidence, 99.0)
    }


class EnterpriseRAGSystem:
    """
    Full Enterprise RAG system with RBAC.
    Extends the existing C++ vector DB backend from:
    https://github.com/shrutii-mishra/my-ai-project
    """

    def __init__(self):
        print("  Initializing Enterprise RAG System...")
        print("   Based on: github.com/shrutii-mishra/my-ai-project")
        print("   Extension: RBAC + Multi-format ingestion + Explainability\n")

        # Load data
        _, _, _, user_roles_data = create_synthetic_dataset()
        self.all_chunks = ingest_all_data()

        # Initialize components
        self.rbac = RBACManager(user_roles_data)
        self.retriever = SimpleRetriever(self.all_chunks)

        # Try to connect to existing C++ backend
        self.backend_available = self._check_backend()
        if self.backend_available:
            print("\n C++ Vector DB backend connected at localhost:8080")
        else:
            print("\n  C++ backend offline — using built-in retriever")
            print("   (Start backend: compile main.cpp and run ./server)")

        print(f"\n System ready! {len(self.all_chunks)} chunks indexed.\n")

    def _check_backend(self) -> bool:
        """Check if existing C++ backend is running"""
        try:
            r = requests.get(f"{VECTOR_DB_URL}/status", timeout=2)
            return r.status_code == 200
        except:
            return False

    def query(self, query: str, user_id: str) -> Dict:
        """
        Main query pipeline:
        Query → Auth Check → Route → RBAC Filter → Retrieve → Generate
        """
        print(f"\n{'='*65}")
        print(f"  QUERY  : {query}")
        print(f"  USER   : {user_id}")
        print(f"  TIME   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*65}")

        # Step 1: Authenticate user
        user_roles = self.rbac.get_user_roles(user_id)
        if not user_roles:
            print(" Unknown user — access denied")
            return {
                "status": "DENIED",
                "reason": "User not recognized in the system",
                "answer": "Access denied. Unknown user.",
                "sources": [], "confidence": 0.0
            }
        print(f"\n User Roles    : {user_roles}")

        # Step 2: Route query
        target_sources = route_query(query)
        print(f" Query Routed  : {target_sources}")

        # Step 3: RBAC filtering (BEFORE retrieval)
        authorized_chunks, denied_count = self.rbac.filter_chunks(self.all_chunks, user_id)
        print(f" RBAC Filter   : {len(self.all_chunks)} total → "
              f"{len(authorized_chunks)} authorized, {denied_count} restricted")

        if not authorized_chunks:
            return {
                "status": "DENIED",
                "reason": "No authorized documents for your role",
                "answer": "Access denied. You do not have permission to access any relevant documents.",
                "sources": [], "confidence": 0.0
            }

        # Step 4: Retrieve (via C++ backend or fallback)
        if self.backend_available:
            # Use existing HNSW-powered backend
            retrieved = self._backend_retrieve(query, authorized_chunks, target_sources)
        else:
            # Use built-in hybrid retriever
            retrieved = self.retriever.retrieve(query, authorized_chunks, target_sources, top_k=3)

        print(f"📄 Retrieved     : {len(retrieved)} relevant chunks")
        for i, r in enumerate(retrieved):
            print(f"   [{i+1}] {r['chunk']['source']} (score: {r['score']})")

        # Step 5: Generate response
        result = generate_response(query, retrieved, user_id, user_roles)

        # Step 6: Add explainability metadata
        result.update({
            "status": "AUTHORIZED",
            "user": user_id,
            "user_roles": user_roles,
            "sources_searched": target_sources,
            "total_chunks_available": len(self.all_chunks),
            "authorized_chunks": len(authorized_chunks),
            "retrieval_trace": {
                "query_routing": target_sources,
                "rbac_filter": f"{len(authorized_chunks)}/{len(self.all_chunks)} chunks authorized",
                "retrieval_method": "C++ HNSW Backend" if self.backend_available else "Hybrid BM25+Semantic",
                "chunks_retrieved": len(retrieved)
            }
        })

        return result

    def _backend_retrieve(self, query: str, authorized_chunks: List[Dict],
                          target_sources: List[str]) -> List[Dict]:
        """
        Use existing C++ HNSW backend for retrieval,
        then apply RBAC filter on returned results.
        """
        try:
            # Call existing /doc/search endpoint
            response = requests.post(
                f"{VECTOR_DB_URL}/doc/search",
                json={"question": query, "k": 10},
                timeout=10
            )
            if response.status_code != 200:
                raise Exception("Backend error")

            results = response.json().get("results", [])
            authorized_ids = {c["id"] for c in authorized_chunks}

            # Filter to only authorized results
            filtered = []
            for r in results:
                if r.get("id") in authorized_ids:
                    filtered.append({
                        "chunk": r,
                        "score": r.get("score", 0.5),
                        "semantic_score": r.get("score", 0.5),
                        "bm25_score": 0.0
                    })
            return filtered[:3]

        except Exception as e:
            print(f"    Backend error: {e}, using fallback retriever")
            return self.retriever.retrieve(query, authorized_chunks, target_sources)



def display_result(result: Dict):
    """Pretty print the RAG response with full explainability"""
    print(f"\n{'='*65}")
    print("  RESPONSE")
    print(f"{'='*65}")

    status = result.get("status", "UNKNOWN")
    status_icon = "✅" if status == "AUTHORIZED" else "❌"
    print(f"\n{status_icon} Access Status : {status}")

    if status == "DENIED":
        print(f" Reason       : {result.get('reason', 'Access denied')}")
        print(f"{'='*65}\n")
        return

    print(f" Confidence   : {result.get('confidence', 0)}%")
    print(f" User Roles   : {result.get('user_roles', [])}")

    print(f"\n ANSWER:")
    print("-" * 40)
    # Print only the answer section for brevity
    answer_lines = result["answer"].split('\n')
    for line in answer_lines:
        if line.strip():
            print(f"  {line}")

    print(f"\n SOURCES CITED:")
    for citation in result.get("citations", []):
        print(f"  {citation}")

    print(f"\n RETRIEVAL TRACE:")
    trace = result.get("retrieval_trace", {})
    for k, v in trace.items():
        print(f"  {k}: {v}")

    print(f"\n Sources Searched: {result.get('sources_searched', [])}")
    print(f"{'='*65}\n")


if __name__ == "__main__":

    print("=" * 65)
    print("  ENTERPRISE RAG INTELLIGENCE SYSTEM")
    print("  SimplifyX Hiring Challenge 2026")
    print("  Built on: github.com/shrutii-mishra/my-ai-project")
    print("=" * 65)

    # Initialize system
    rag = EnterpriseRAGSystem()

    # ── TEST 1: Finance user asks about revenue ──
    print("\n TEST 1: Finance user queries revenue data")
    r1 = rag.query("What was the Q3 revenue growth and top products?", "alice")
    display_result(r1)

    # ── TEST 2: Employee asks about leave policy ──
    print("\n TEST 2: Regular employee asks about leave policy")
    r2 = rag.query("How many leave days am I entitled to?", "bob")
    display_result(r2)

    # ── TEST 3: Unauthorized access attempt ──
    print("\n TEST 3: Regular employee tries to access finance data (RBAC BLOCK)")
    r3 = rag.query("What is the company Q3 revenue and net profit?", "eve")
    display_result(r3)

    # ── TEST 4: HR queries employee records ──
    print("\n TEST 4: HR manager queries employee salary data")
    r4 = rag.query("Show me salary information for engineering department", "charlie")
    display_result(r4)

    # ── TEST 5: Security admin checks logs ──
    print("\n TEST 5: Security admin investigates failed login attempts")
    r5 = rag.query("Were there any suspicious login attempts or security incidents?", "diana")
    display_result(r5)

    print("\n✅ All tests complete!")
    print("\n NOTE: In production, retrieval uses the C++ HNSW vector")
    print("   database from github.com/shrutii-mishra/my-ai-project")
    print("   which provides sub-millisecond semantic search at scale.")
    print("   Start the backend: compile main.cpp → ./server")
    print("   Then set FALLBACK_MODE = False in this file.\n")