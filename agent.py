#!/usr/bin/env python3
"""
AI Agent that uses Claude to perform tasks
"""

import os
import anthropic
from pathlib import Path

class ClaudeAgent:
    def __init__(self):
        """Initialize the Claude agent with API key"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-haiku-20240307"
    
    def perform_task(self, task_description: str) -> str:
        """Use Claude to perform a task"""
        try:
            # Create the prompt for Claude
            prompt = f"""
            You are a helpful AI agent that can perform terminal tasks.
            
            Task: {task_description}
            
            Please provide the exact terminal commands needed to complete this task.
            Only provide the commands, no explanations.
            """
            
            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error calling Claude: {e}"
    
    def execute_task(self, task_description: str):
        """Execute a task using Claude's guidance"""
        print(f"🤖 Claude Agent performing task: {task_description}")
        
        # Get instructions from Claude
        instructions = self.perform_task(task_description)
        print(f"📋 Claude's instructions:\n{instructions}")
        
        # Execute the commands Claude provided
        try:
            import subprocess
            import re
            
            # Split instructions into individual commands
            commands = instructions.strip().split('\n')
            
            for command in commands:
                command = command.strip()
                if command and not command.startswith('#'):  # Skip empty lines and comments
                    print(f"🔄 Executing: {command}")
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    
                    if result.stdout:
                        # Format the output nicely
                        formatted_output = self.format_output(result.stdout, task_description)
                        print(f"📤 Results:\n{formatted_output}")
                    if result.stderr:
                        print(f"⚠️ Error:\n{result.stderr}")
            
            print("✅ Task completed successfully!")
            print("The END-----------------------------")
            
        except Exception as e:
            print(f"❌ Error executing task: {e}")
    
    def format_output(self, raw_output: str, task_description: str) -> str:
        """Format the raw output to extract relevant information"""
        try:
            # Clean up the text
            clean_text = self.clean_and_extract_content(raw_output)
            
            # Use generic extraction that works for all content types
            return self.extract_relevant_info(clean_text, task_description)
                
        except Exception as e:
            return f"Error formatting output: {e}\n\nRaw output:\n{raw_output[:500]}..."
    
    def clean_and_extract_content(self, raw_text: str) -> str:
        """Clean HTML and extract meaningful content"""
        import re
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', raw_text)
        
        # Remove JavaScript and CSS content
        clean_text = re.sub(r'<script.*?</script>', '', clean_text, flags=re.DOTALL)
        clean_text = re.sub(r'<style.*?</style>', '', clean_text, flags=re.DOTALL)
        
        # Remove common Wikipedia/web page artifacts
        clean_text = re.sub(r'\[edit\]', '', clean_text)
        clean_text = re.sub(r'\[citation needed\]', '', clean_text)
        clean_text = re.sub(r'\[\d+\]', '', clean_text)  # Remove reference numbers
        clean_text = re.sub(r'Jump to navigation.*?Jump to search', '', clean_text)
        
        # Clean up whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text)
        clean_text = clean_text.strip()
        
        return clean_text
    
    def extract_relevant_info(self, text: str, task_description: str) -> str:
        """Extract relevant information based on the task"""
        import re
        
        # Extract key terms from the task description
        task_keywords = self.extract_keywords_from_task(task_description)
        
        # Split text into sentences and paragraphs
        sentences = re.split(r'[.!?]+', text)
        
        # Score sentences based on relevance
        scored_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 300:  # Skip very short or very long sentences
                continue
                
            score = self.score_sentence_relevance(sentence, task_keywords)
            if score > 0:
                scored_sentences.append((score, sentence))
        
        # Sort by relevance and take top sentences
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [sentence for score, sentence in scored_sentences[:5]]
        
        if top_sentences:
            return "📋 **Key Information:**\n" + "\n".join(f"• {sentence.strip()}" for sentence in top_sentences)
        else:
            # Fallback: show first few meaningful sentences
            fallback_sentences = []
            for sentence in sentences[:10]:
                sentence = sentence.strip()
                if len(sentence) > 30 and len(sentence) < 200:
                    fallback_sentences.append(sentence)
                    if len(fallback_sentences) >= 3:
                        break
            
            if fallback_sentences:
                return "📄 **Summary:**\n" + "\n".join(f"• {sentence}" for sentence in fallback_sentences)
            else:
                return "📄 **Content:**\n" + text[:500] + "..." if len(text) > 500 else text
    
    def extract_keywords_from_task(self, task_description: str) -> list:
        """Extract important keywords from the task description"""
        import re
        
        # Remove common words and extract meaningful terms
        common_words = {'what', 'is', 'the', 'who', 'where', 'when', 'how', 'about', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by'}
        
        # Extract words and clean them
        words = re.findall(r'\b\w+\b', task_description.lower())
        keywords = [word for word in words if word not in common_words and len(word) > 2]
        
        return keywords
    
    def score_sentence_relevance(self, sentence: str, keywords: list) -> int:
        """Score a sentence based on how many keywords it contains"""
        sentence_lower = sentence.lower()
        score = 0
        
        for keyword in keywords:
            if keyword in sentence_lower:
                score += 1
        
        # Bonus points for sentences that seem informative
        if any(word in sentence_lower for word in ['founded', 'established', 'company', 'organization', 'known for', 'specializes']):
            score += 2
        
        if any(word in sentence_lower for word in ['born', 'elected', 'served', 'became', 'appointed']):
            score += 2
            
        return score

def main():
    """Main function to run the agent"""
    try:
        # Create the agent
        agent = ClaudeAgent()
        
        # Get task from user input
        print("🤖 Claude Agent - Enter your task:")
        task = input("> ")
        
        if not task.strip():
            print("❌ No task provided. Exiting.")
            return
        
        # Execute the task
        agent.execute_task(task)
        
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        print("💡 Make sure ANTHROPIC_API_KEY is set in your environment")

if __name__ == "__main__":
    main()
    