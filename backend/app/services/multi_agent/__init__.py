"""Multi-Agent package — Asahlagi full multi-agent architecture.

AI_AGENT_IDEAS.md §Fase 3 implementation menggunakan LangGraph.

Agents:
    - agent_extractor   : ekstrak & analisis materi (PDF/URL/teks)
    - agent_quiz_maker  : generate + polish + validasi soal
    - agent_evaluator   : nilai jawaban + granular topic analysis
    - agent_insight     : generate insight & study path personal (LLM)
    - agent_asahi       : chatbot dengan tools
    - orchestrator      : LangGraph StateGraph yang koordinasi semua agen
"""
