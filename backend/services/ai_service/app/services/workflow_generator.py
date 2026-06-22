import json
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger("workflow_generator")

class WorkflowGenerator:
    def __init__(self):
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client for Workflows: {e}")

    def generate_workflow(self, prompt: str) -> Dict[str, Any]:
        """Translates a user prompt into a structured React Flow-compatible workflow definition."""
        if self.openai_client:
            try:
                workflow = self._llm_generate(prompt)
                if workflow:
                    return workflow
            except Exception as e:
                logger.warning(f"LLM workflow generation failed, using rules-based builder: {e}")

        # Rules-based deterministic fallback
        return self._rules_generate(prompt)

    def _rules_generate(self, prompt: str) -> Dict[str, Any]:
        """Helper to output workflow definitions matching standard requests."""
        p = prompt.lower()
        
        # 1. Benchling Daily Sync, Sequence Alignment & Email
        if "benchling" in p or "alignment" in p or "email" in p:
            nodes = [
                {
                    "id": "node_1",
                    "type": "datasource",
                    "position": {"x": 100, "y": 150},
                    "data": {"label": "Benchling LIMS", "source_id": "benchling_eln", "limit": 10}
                },
                {
                    "id": "node_2",
                    "type": "sequence_analysis",
                    "position": {"x": 350, "y": 150},
                    "data": {"label": "Multiple Sequence Alignment", "alignment_tool": "clustalo"}
                },
                {
                    "id": "node_3",
                    "type": "approval",
                    "position": {"x": 600, "y": 150},
                    "data": {"label": "Review Signature", "role_required": "REVIEWER"}
                },
                {
                    "id": "node_4",
                    "type": "notification",
                    "position": {"x": 850, "y": 150},
                    "data": {"label": "Email Results", "channel": "EMAIL", "recipient": "team@genquantaa.com"}
                }
            ]
            edges = [
                {"id": "e1-2", "source": "node_1", "target": "node_2"},
                {"id": "e2-3", "source": "node_2", "target": "node_3"},
                {"id": "e3-4", "source": "node_3", "target": "node_4"}
            ]
            return {
                "name": "Daily Benchling Sequence Alignment & Sync",
                "description": "Triggered daily to pull sequences from Benchling, execute Clustal Omega alignment, await signature approval, and email results.",
                "trigger_type": "SCHEDULED",
                "cron_schedule": "0 8 * * *",  # Daily at 8:00 AM
                "nodes": nodes,
                "edges": edges
            }

        # Default fallback workflow
        nodes = [
            {
                "id": "node_1",
                "type": "datasource",
                "position": {"x": 200, "y": 100},
                "data": {"label": "Experiment Catalog Ingest", "source_id": "metadata_catalog"}
            },
            {
                "id": "node_2",
                "type": "notification",
                "position": {"x": 500, "y": 100},
                "data": {"label": "Alert Team", "channel": "SLACK", "recipient": "#scientific-ops"}
            }
        ]
        edges = [
            {"id": "e1-2", "source": "node_1", "target": "node_2"}
        ]
        return {
            "name": "Standard Metadata Sync Pipeline",
            "description": "Standard pipeline to monitor and ingest catalog changes.",
            "trigger_type": "MANUAL",
            "cron_schedule": None,
            "nodes": nodes,
            "edges": edges
        }

    def _llm_generate(self, prompt: str) -> Dict[str, Any]:
        """Queries OpenAI GPT for a custom React Flow workflow JSON representation."""
        system_prompt = """You are the AI Scientist Copilot workflow compiler for GENQUANTAA Discover.
Your job is to translate a user request into a valid JSON workflow definition:
{
  "name": "Workflow Name",
  "description": "Workflow Description",
  "trigger_type": "MANUAL|SCHEDULED|EVENT",
  "cron_schedule": "cron string if scheduled, else null",
  "nodes": [
    {
      "id": "node_1",
      "type": "datasource|sync|query|compound_search|sequence_analysis|assay_analysis|export|notification|approval",
      "position": { "x": 100, "y": 150 },
      "data": { "label": "Node Label", "source_id": "optional", "channel": "optional", "recipient": "optional", "role_required": "optional" }
    }
  ],
  "edges": [
    { "id": "e1-2", "source": "node_1", "target": "node_2" }
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

workflow_generator = WorkflowGenerator()
