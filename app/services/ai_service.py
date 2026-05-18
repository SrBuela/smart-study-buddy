import json
from typing import List, Dict
from app.core.config import settings

class AIService:
    def __init__(self):
        # If DEEPSEEK_API_KEY is empty or still the placeholder, use mock
        self.use_mock = (
            not settings.DEEPSEEK_API_KEY
            or settings.DEEPSEEK_API_KEY == "your-deepseek-api-key"
        )

    # ------------------------------------------------------------
    # 🧠 Real DeepSeek client (OpenAI‑compatible)
    # ------------------------------------------------------------
    def _get_client(self):
        from openai import OpenAI
        return OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com",  # OpenAI‑compatible endpoint[reference:1]
        )

    # ------------------------------------------------------------
    # 📝 Generate flashcards
    # ------------------------------------------------------------
    async def generate_flashcards(
        self, text: str, count: int = 10, include_hints: bool = False
    ) -> List[Dict]:
        if self.use_mock:
            return [
                {
                    "front": "What is the capital of France?",
                    "back": "Paris",
                    "topic": "Geography",
                    "hint": "City of Light" if include_hints else "",
                },
                {
                    "front": "Explain the concept of variables in programming.",
                    "back": "A variable is a named storage location that holds data.",
                    "topic": "Programming",
                    "hint": "Think of a labeled box" if include_hints else "",
                },
                {
                    "front": "What does the input() function do in Python?",
                    "back": "It reads a line from standard input and returns it as a string.",
                    "topic": "Python",
                    "hint": "User interaction" if include_hints else "",
                },
            ][:count]

        # --- Real DeepSeek call ---
        client = self._get_client()
        prompt = f"""You are an expert flashcard creator. Generate {count} high-quality flashcards from the following text.
        Rules:
        1. One concept per card.
        2. Clear questions, concise answers.
        3. Categorize each card by topic.
        {f'4. Include helpful hints where appropriate.' if include_hints else ''}

        Text: {text[:4000]}

        Return ONLY valid JSON with this structure:
        {{"cards": [{{"front": "...", "back": "...", "topic": "...", "hint": "..."}}]}}
        """
        response = client.chat.completions.create(
            model="deepseek-v4-pro",   # or deepseek-v4-flash, deepseek-chat[reference:2]
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,           # low temperature for structured output
            max_tokens=2000,
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("cards", [])

    # ------------------------------------------------------------
    # 📄 Summarise notes
    # ------------------------------------------------------------
    async def summarize_notes(self, text: str, max_length: int = 500) -> Dict:
        if self.use_mock:
            return {
                "summary": "This text appears to be about technology and programming concepts.",
                "key_points": ["Variables store data.", "Functions perform actions."],
                "key_terms": [{"term": "Variable", "definition": "A named storage location"}],
            }

        client = self._get_client()
        prompt = f"""Summarize the following text in JSON:
        {{
            "summary": "a concise summary (max {max_length} chars)",
            "key_points": ["point1", "point2", ...],
            "key_terms": [{{"term": "...", "definition": "..."}}]
        }}
        Text: {text[:4000]}
        """
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1000,
        )
        return json.loads(response.choices[0].message.content)

    # ------------------------------------------------------------
    # ❓ Generate quiz
    # ------------------------------------------------------------
    async def generate_quiz(
        self, cards_content: List[Dict], question_count: int = 5, difficulty: str = "medium"
    ) -> List[Dict]:
        if self.use_mock:
            return [
                {
                    "question": "What is the output of print(2+2)?",
                    "options": ["2", "4", "22", "Error"],
                    "correct_answer": 1,
                    "explanation": "The '+' operator adds two integers.",
                }
            ][:question_count]

        client = self._get_client()
        cards_text = "\n".join([f"Q: {c['front']}\nA: {c['back']}" for c in cards_content[:20]])
        prompt = f"""Create {question_count} multiple‑choice questions (difficulty: {difficulty}) based on these flashcards:
        {cards_text}
        Return JSON: {{"questions": [{{"question": "...", "options": ["A","B","C","D"], "correct_answer": 0, "explanation": "..."}}]}}
        """
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000,
        )
        return json.loads(response.choices[0].message.content).get("questions", [])