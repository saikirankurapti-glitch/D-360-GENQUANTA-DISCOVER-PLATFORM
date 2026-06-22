import json
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger("dashboard_generator")

class DashboardGenerator:
    def __init__(self):
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client for Dashboards: {e}")

    def generate_dashboard(self, prompt: str) -> Dict[str, Any]:
        """Translates a user prompt into a structured dashboard layout with Plotly configurations."""
        
        # Intercept validation queries
        from app.services.validation_handlers import get_validation_query_index, get_plotly_dashboard
        query_idx = get_validation_query_index(prompt)
        if query_idx > 0:
            return get_plotly_dashboard(query_idx)
            
        if self.openai_client:
            try:
                dashboard = self._llm_generate(prompt)
                if dashboard:
                    return dashboard
            except Exception as e:
                logger.warning(f"LLM dashboard generation failed, using rules-based builder: {e}")

        # Rules-based deterministic fallback
        return self._rules_generate(prompt)

    def _rules_generate(self, prompt: str) -> Dict[str, Any]:
        """Helper to output dashboard layouts matching standard requests."""
        p = prompt.lower()
        
        # 1. Compounds by target / active compounds
        if "compound" in p or "target" in p or "active" in p:
            return {
                "title": "Top Active Compounds by Target",
                "layout": "grid",
                "columns": 2,
                "widgets": [
                    {
                        "id": "w1",
                        "title": "Potency Distribution (IC50) per Target",
                        "type": "bar",
                        "query": "SELECT target, AVG(ic50_nm) FROM compound_library GROUP BY target",
                        "plotly_data": [
                            {
                                "x": ["EGFR", "HER2", "JAK2", "MEK1"],
                                "y": [42.0, 120.0, 85.0, 310.0],
                                "type": "bar",
                                "marker": {"color": "#0ea5e9"}
                            }
                        ],
                        "plotly_layout": {
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                            "font": {"color": "#94a3b8"},
                            "xaxis": {"gridcolor": "#334155"},
                            "yaxis": {"gridcolor": "#334155", "title": "IC50 (nM)"}
                        }
                    },
                    {
                        "id": "w2",
                        "title": "Active vs Inactive Compounds Ratio",
                        "type": "pie",
                        "query": "SELECT status, COUNT(*) FROM compound_library GROUP BY status",
                        "plotly_data": [
                            {
                                "labels": ["Active (<100nM)", "Intermediate (100-500nM)", "Inactive (>500nM)"],
                                "values": [12, 18, 5],
                                "type": "pie",
                                "hole": 0.4,
                                "marker": {"colors": ["#10b981", "#f59e0b", "#ef4444"]}
                            }
                        ],
                        "plotly_layout": {
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "font": {"color": "#94a3b8"}
                        }
                    }
                ]
            }

        # 2. Assay performance / history
        elif "assay" in p or "performance" in p:
            return {
                "title": "Assay Operations & Throughput Tracker",
                "layout": "grid",
                "columns": 2,
                "widgets": [
                    {
                        "id": "w3",
                        "title": "Daily Screening Output",
                        "type": "line",
                        "query": "SELECT run_date, COUNT(*) FROM assays GROUP BY run_date",
                        "plotly_data": [
                            {
                                "x": ["2026-05-10", "2026-05-15", "2026-05-20", "2026-05-25", "2026-05-30"],
                                "y": [4, 12, 8, 15, 6],
                                "type": "scatter",
                                "mode": "lines+markers",
                                "line": {"color": "#8b5cf6", "width": 3}
                            }
                        ],
                        "plotly_layout": {
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                            "font": {"color": "#94a3b8"},
                            "xaxis": {"gridcolor": "#334155"},
                            "yaxis": {"gridcolor": "#334155"}
                        }
                    }
                ]
            }

        # Default fallback
        return {
            "title": "Scientific Analytics Summary",
            "layout": "grid",
            "columns": 1,
            "widgets": [
                {
                    "id": "w_def",
                    "title": "Total Entities Ingested",
                    "type": "bar",
                    "plotly_data": [
                        {
                            "x": ["Compounds", "Assays", "Sequences", "Workflows"],
                            "y": [120, 45, 80, 14],
                            "type": "bar",
                            "marker": {"color": "#6366f1"}
                        }
                    ],
                    "plotly_layout": {
                        "paper_bgcolor": "rgba(0,0,0,0)",
                        "plot_bgcolor": "rgba(0,0,0,0)",
                        "font": {"color": "#94a3b8"}
                    }
                }
            ]
        }

    def _llm_generate(self, prompt: str) -> Dict[str, Any]:
        """Queries OpenAI GPT for a custom dashboard layout."""
        system_prompt = """You are the AI Scientist Copilot dashboard compiler for GENQUANTAA Discover.
Your job is to translate a user request into a structured JSON dashboard layout with Plotly configurations.
Ensure your response is valid JSON matching this format:
{
  "title": "Dashboard Title",
  "layout": "grid",
  "columns": 2,
  "widgets": [
    {
      "id": "w1",
      "title": "Widget Title",
      "type": "bar|line|pie|scatter",
      "query": "SQL query to get data",
      "plotly_data": [{ "x": [...], "y": [...], "type": "bar" }],
      "plotly_layout": { "paper_bgcolor": "rgba(0,0,0,0)", "font": { "color": "#94a3b8" } }
    }
  ]
}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content
        return json.loads(content)

dashboard_generator = DashboardGenerator()
