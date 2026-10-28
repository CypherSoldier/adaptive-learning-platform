"""Compatibility import. AI and seeded content share the canonical Question mapping."""
from src.models.question import Question as AIQuestion

__all__ = ["AIQuestion"]
