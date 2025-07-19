import google.generativeai as genai
import asyncio
import logging
from typing import List, Optional
from datetime import datetime

from .config import Config
from .models import DebateArgument, DebateRole, TradingConcept

class AIDebater:
    """AI Debater using Gemini models for trading theory development"""
    
    def __init__(self, model_name: str, role: DebateRole):
        self.model_name = model_name
        self.role = role
        self.config = Config()
        
        # Configure Gemini
        genai.configure(api_key=self.config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name)
        
        # Setup logging
        self.logger = logging.getLogger(f"AIDebater-{model_name}-{role}")
        
    def _create_debate_prompt(self, topic: str, concept_type: TradingConcept, 
                            context: List[DebateArgument], round_number: int) -> str:
        """Create a contextualized prompt for the debate"""
        
        role_descriptions = {
            DebateRole.CHALLENGER: "Critical analyst who challenges assumptions and identifies weaknesses",
            DebateRole.DEFENDER: "Theory advocate who builds upon ideas and reinforces strong concepts",
            DebateRole.SYNTHESIZER: "Integrative thinker who combines different perspectives into cohesive frameworks"
        }
        
        # Build context from previous arguments
        context_text = ""
        if context:
            context_text = "\n\nPrevious Arguments:\n"
            for arg in context[-3:]:  # Last 3 arguments for context
                context_text += f"Round {arg.round_number} - {arg.role.value} ({arg.model_name}):\n{arg.content}\n\n"
        
        prompt = self.config.SYSTEM_PROMPT_TEMPLATE.format(
            role=f"{self.role.value} - {role_descriptions[self.role]}",
            topic=topic,
            context=context_text
        )
        
        # Add specific instructions based on round
        if round_number == 1:
            prompt += f"\n\nThis is Round 1. Provide your initial theoretical perspective on: {topic}"
        else:
            prompt += f"\n\nThis is Round {round_number}. Respond to the previous arguments while advancing the theoretical discussion."
        
        # Add concept-specific guidance
        concept_guidance = {
            TradingConcept.MICRO_ALPHA: "Focus on small-scale market inefficiencies, signal detection, and rapid execution theories.",
            TradingConcept.RISK_MANAGEMENT: "Emphasize portfolio protection, uncertainty quantification, and loss mitigation frameworks.",
            TradingConcept.MARKET_STRUCTURE: "Analyze market mechanics, liquidity dynamics, and structural inefficiencies.",
            TradingConcept.ALGORITHMIC_STRATEGY: "Develop systematic approaches, rule-based frameworks, and automated decision processes.",
            TradingConcept.PORTFOLIO_THEORY: "Address asset allocation, diversification, and optimization methodologies.",
            TradingConcept.BEHAVIORAL_FINANCE: "Incorporate psychological factors, cognitive biases, and market sentiment analysis."
        }
        
        prompt += f"\n\nConcept Focus: {concept_guidance.get(concept_type, 'General trading theory development')}"
        
        return prompt
    
    async def generate_argument(self, topic: str, concept_type: TradingConcept,
                              context: List[DebateArgument], round_number: int) -> DebateArgument:
        """Generate a debate argument using the AI model"""
        
        try:
            prompt = self._create_debate_prompt(topic, concept_type, context, round_number)
            
            # Generate response using Gemini
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.model.generate_content, prompt
            )
            
            # Extract key insights and theoretical foundations
            content = response.text
            key_insights = self._extract_key_insights(content)
            theoretical_foundations = self._extract_theoretical_foundations(content)
            
            argument = DebateArgument(
                role=self.role,
                model_name=self.model_name,
                content=content,
                round_number=round_number,
                key_insights=key_insights,
                theoretical_foundations=theoretical_foundations
            )
            
            self.logger.info(f"Generated argument for round {round_number}")
            return argument
            
        except Exception as e:
            self.logger.error(f"Error generating argument: {str(e)}")
            raise
    
    def _extract_key_insights(self, content: str) -> List[str]:
        """Extract key insights from the generated content"""
        insights = []
        
        # Look for common insight indicators
        insight_indicators = [
            "key insight:",
            "important finding:",
            "crucial observation:",
            "fundamental principle:",
            "critical factor:"
        ]
        
        lines = content.lower().split('\n')
        for line in lines:
            for indicator in insight_indicators:
                if indicator in line:
                    # Extract the insight (everything after the indicator)
                    insight = line.split(indicator, 1)[1].strip()
                    if insight:
                        insights.append(insight.capitalize())
        
        # If no explicit insights found, extract from bullet points or numbered lists
        if not insights:
            for line in content.split('\n'):
                line = line.strip()
                if (line.startswith('•') or line.startswith('-') or 
                    (len(line) > 0 and line[0].isdigit() and '.' in line[:3])):
                    clean_line = line.lstrip('•-0123456789. ').strip()
                    if len(clean_line) > 20:  # Reasonable insight length
                        insights.append(clean_line)
        
        return insights[:5]  # Limit to 5 key insights
    
    def _extract_theoretical_foundations(self, content: str) -> List[str]:
        """Extract theoretical foundations from the content"""
        foundations = []
        
        # Look for theoretical references
        theory_indicators = [
            "efficient market hypothesis",
            "modern portfolio theory",
            "capital asset pricing model",
            "behavioral finance",
            "game theory",
            "information theory",
            "random walk theory",
            "adaptive market hypothesis",
            "prospect theory",
            "market microstructure",
            "quantitative finance",
            "stochastic calculus",
            "time series analysis",
            "machine learning"
        ]
        
        content_lower = content.lower()
        for theory in theory_indicators:
            if theory in content_lower:
                foundations.append(theory.title())
        
        return list(set(foundations))  # Remove duplicates