"""
Streamlined Script Generator for YouTube Shorts
"""
from openai import OpenAI
import json
import os
import random
from datetime import datetime
from typing import Optional, Dict, Any
from .config import Config

class ScriptGenerator:
    """Generates YouTube Shorts scripts using Gemini API"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """Initialize the Script Generator"""
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model = model or Config.DEFAULT_MODEL
        
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        # Initialize OpenAI client for Gemini
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=Config.GEMINI_BASE_URL
        )
        
        self.topics = Config.AVAILABLE_TOPICS
        self.facts_file = "generated_facts.json"
        self.facts_data = self.load_facts()
    
    def load_facts(self) -> Dict[str, Any]:
        """Load existing facts from JSON file"""
        if os.path.exists(self.facts_file):
            try:
                with open(self.facts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {"facts_by_topic": {}, "metadata": {"total_facts": 0}}
    
    def save_facts(self):
        """Save facts data to JSON file"""
        self.facts_data["metadata"]["last_updated"] = datetime.now().isoformat()
        self.facts_data["metadata"]["total_facts"] = sum(
            len(facts) for facts in self.facts_data["facts_by_topic"].values()
        )
        
        with open(self.facts_file, 'w', encoding='utf-8') as f:
            json.dump(self.facts_data, f, indent=2, ensure_ascii=False)
    
    def get_existing_facts(self, topic: str) -> list:
        """Get existing facts for a topic"""
        return [fact["fact"] for fact in self.facts_data["facts_by_topic"].get(topic, [])]
    
    def is_fact_duplicate(self, new_fact: str, topic: str) -> bool:
        """Check if a fact is too similar to existing ones"""
        existing_facts = self.get_existing_facts(topic)
        new_fact_words = set(new_fact.lower().split())
        
        for existing_fact in existing_facts:
            existing_words = set(existing_fact.lower().split())
            intersection = len(new_fact_words.intersection(existing_words))
            union = len(new_fact_words.union(existing_words))
            
            if union > 0:
                similarity = intersection / union
                if similarity > Config.SIMILARITY_THRESHOLD:
                    return True
        return False
    
    def generate_script(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Generate a YouTube Shorts script"""
        if topic is None:
            topic = random.choice(self.topics)
        elif topic not in self.topics:
            # If custom topic provided, add it to available topics
            self.topics.append(topic)
        
        existing_facts = self.get_existing_facts(topic)
        limited_facts = existing_facts[-3:]  # Only last 3 facts to avoid token overflow
        existing_facts_text = "\n".join([f"- {fact[:100]}..." for fact in limited_facts])
        
        prompt = f"""Create a YouTube Shorts script about {topic}.
        Target: 30 seconds when spoken (70-80 words total).

        Include:
        1. Hook (max 12 words)
        2. Interesting fact (max 25 words)
        3. Brief explanation (max 30 words)
        4. Call-to-action (max 12 words)

        Avoid these facts: {existing_facts_text if existing_facts else "None yet!"}

        Format:
        HOOK: [12 words max]
        FACT: [25 words max]
        EXPLANATION: [30 words max]
        CTA: [12 words max]

        Keep it punchy, fast-paced, and engaging."""
        
        for attempt in range(Config.MAX_RETRIES):
            try:
                print(f"🧠 Generating script (attempt {attempt + 1}/{Config.MAX_RETRIES})...")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a viral YouTube content creator. Create engaging, factual scripts that captivate viewers in the first 3 seconds."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=Config.MAX_TOKENS,
                    temperature=Config.TEMPERATURE
                )
                
                if not response or not response.choices:
                    raise Exception("Empty response from API")
                
                script_content = response.choices[0].message.content.strip()
                script_parts = self._parse_script_content(script_content)
                
                # Validate we got all parts
                required_parts = ['hook', 'fact', 'explanation', 'cta']
                if not all(part in script_parts for part in required_parts):
                    print(f"⚠️ Missing script parts, retrying...")
                    continue
                
                # Check for duplicates
                main_fact = script_parts['fact']
                if not self.is_fact_duplicate(main_fact, topic):
                    full_script = f"{script_parts['hook']} {script_parts['fact']} {script_parts['explanation']} {script_parts['cta']}"
                    word_count = len(full_script.split())
                    
                    script_data = {
                        "topic": topic,
                        "hook": script_parts['hook'],
                        "fact": script_parts['fact'],
                        "explanation": script_parts['explanation'],
                        "cta": script_parts['cta'],
                        "full_script": full_script.strip(),
                        "generated_at": datetime.now().isoformat(),
                        "word_count": word_count,
                        "estimated_duration": f"{word_count * 0.6:.1f} seconds",
                        "model": self.model
                    }
                    
                    self._save_script_to_database(script_data, main_fact, topic)
                    print(f"✅ Script generated successfully!")
                    return script_data
                
                else:
                    print(f"🔄 Generated fact too similar to existing ones, retrying...")
                    
            except Exception as e:
                print(f"❌ Error generating script (attempt {attempt + 1}): {str(e)}")
                if attempt == Config.MAX_RETRIES - 1:
                    raise
        
        raise Exception(f"Failed to generate unique script for {topic} after {Config.MAX_RETRIES} attempts")
    
    def _parse_script_content(self, script_content: str) -> Dict[str, str]:
        """Parse the script content into structured parts"""
        script_parts = {}
        lines = script_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('HOOK:'):
                script_parts['hook'] = line.replace('HOOK:', '').strip()
            elif line.startswith('FACT:'):
                script_parts['fact'] = line.replace('FACT:', '').strip()
            elif line.startswith('EXPLANATION:'):
                script_parts['explanation'] = line.replace('EXPLANATION:', '').strip()
            elif line.startswith('CTA:'):
                script_parts['cta'] = line.replace('CTA:', '').strip()
        
        return script_parts
    
    def _save_script_to_database(self, script_data: Dict[str, Any], main_fact: str, topic: str):
        """Save the generated script to the facts database"""
        if topic not in self.facts_data["facts_by_topic"]:
            self.facts_data["facts_by_topic"][topic] = []
        
        self.facts_data["facts_by_topic"][topic].append({
            "fact": main_fact,
            "full_script": script_data["full_script"],
            "generated_at": datetime.now().isoformat(),
            "model": self.model
        })
        
        self.save_facts()