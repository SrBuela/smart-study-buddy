import json
from typing import List, Optional, Dict
from openai import AsyncOpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def generate_flashcards(
            self,
            text: str,
            count: int = 10,
            include_hints: bool = False
    ) -> List[Dict]:
        """Generate flashcards from text using AI"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        prompt = f"""You are an expert flashcard creator. Generate {count} high-quality flashcards from the following text.

        Rules for creating flashcards:
        1. Follow the minimum information principle (one concept per card)
        2. Questions should be clear, specific, and unambiguous
        3. Answers should be concise (1-3 sentences)
        4. Cover the most important concepts
        5. Categorize each card by topic
        {f'6. Include helpful hints where appropriate' if include_hints else ''}

        Text: {text[:4000]}  # Limit text length

        Return ONLY valid JSON with this structure:
        {{
            "cards": [
                {{
                    "front": "Question text here",
                    "back": "Answer text here",
                    "topic": "Topic category",
                    "hint": "Optional hint" 
                }}
            ]
        }}"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000
            )

            result = json.loads(response.choices[0].message.content)
            tokens_used = response.usage.total_tokens

            logger.info(f"Generated {len(result.get('cards', []))} cards using {tokens_used} tokens")
            return result.get("cards", [])

        except Exception as e:
            logger.error(f"Error generating flashcards: {str(e)}")
            raise

    async def summarize_notes(
            self,
            text: str,
            max_length: int = 500
    ) -> Dict:
        """Generate summary and key points from notes"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        prompt = f"""Summarize the following text. Provide:
        1. A concise summary (max {max_length} characters)
        2. Key points (bullet points, 3-7 items)
        3. Key terms with brief definitions (3-7 items)

        Text: {text[:4000]}

        Return ONLY valid JSON:
        {{
            "summary": "Summary text",
            "key_points": ["Point 1", "Point 2", ...],
            "key_terms": [{{"term": "Term", "definition": "Brief definition"}}, ...]
        }}"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1000
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.error(f"Error summarizing notes: {str(e)}")
            raise

    async def generate_quiz(
            self,
            cards_content: List[Dict],
            question_count: int = 5,
            difficulty: str = "medium"
    ) -> List[Dict]:
        """Generate quiz questions from flashcard content"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        # Prepare card content for prompt
        cards_text = "\n".join([
            f"Q: {card['front']}\nA: {card['back']}"
            for card in cards_content[:20]  # Limit to 20 cards
        ])

        prompt = f"""Based on these flashcards, create {question_count} multiple-choice quiz questions.
        Difficulty level: {difficulty}

        Flashcards:
        {cards_text}

        Requirements:
        - 4 options per question
        - One correct answer (indicated by index 0-3)
        - Brief explanation of the correct answer
        - Questions should test understanding, not just recall

        Return ONLY valid JSON:
        {{
            "questions": [
                {{
                    "question": "Question text",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "Why this is correct"
                }}
            ]
        }}"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("questions", [])

        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            raise