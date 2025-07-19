import asyncio
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config
from .models import (
    DebateSession, DebateArgument, DebateRole, TradingConcept,
    TheoryFramework, AlgorithmRulesBook
)
from .ai_debater import AIDebater
from .knowledge_manager import KnowledgeManager

class DebateEngine:
    """Main engine for orchestrating AI debates on trading theory"""
    
    def __init__(self):
        self.config = Config()
        self.console = Console()
        self.knowledge_manager = KnowledgeManager()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("DebateEngine")
        
        # Initialize AI debaters
        self.debater_1 = AIDebater(self.config.GEMINI_MODEL_1, DebateRole.CHALLENGER)
        self.debater_2 = AIDebater(self.config.GEMINI_MODEL_2, DebateRole.DEFENDER)
        
    async def start_debate(self, topic: str, concept_type: TradingConcept) -> DebateSession:
        """Start a new debate session on a trading theory topic"""
        
        session_id = str(uuid.uuid4())[:8]
        session = DebateSession(
            topic=topic,
            concept_type=concept_type,
            session_id=session_id
        )
        
        self._display_debate_header(session)
        
        try:
            # Conduct debate rounds
            for round_num in range(1, self.config.MAX_DEBATE_ROUNDS + 1):
                await self._conduct_round(session, round_num)
                
                # Display round results
                self._display_round_results(session, round_num)
                
                # Allow some processing time between rounds
                await asyncio.sleep(1)
            
            # Generate final synthesis
            await self._generate_synthesis(session)
            
            # Create theory framework from debate
            framework = await self._create_theory_framework(session)
            
            # Save to knowledge base
            await self.knowledge_manager.save_debate_session(session)
            await self.knowledge_manager.add_theory_framework(framework)
            
            session.status = "completed"
            session.end_time = datetime.now()
            
            self._display_completion(session, framework)
            
            return session
            
        except Exception as e:
            self.logger.error(f"Debate session failed: {str(e)}")
            session.status = "failed"
            session.end_time = datetime.now()
            raise
    
    async def _conduct_round(self, session: DebateSession, round_num: int):
        """Conduct a single round of debate"""
        
        self.console.print(f"\n[bold blue]═══ Round {round_num} ═══[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            # Debater 1 (Challenger) argues
            task1 = progress.add_task(f"[cyan]{self.debater_1.model_name} thinking...", total=None)
            
            try:
                arg1 = await asyncio.wait_for(
                    self.debater_1.generate_argument(
                        session.topic, 
                        session.concept_type, 
                        session.arguments, 
                        round_num
                    ),
                    timeout=self.config.DEBATE_TIMEOUT
                )
                session.arguments.append(arg1)
                progress.update(task1, description=f"[green]{self.debater_1.model_name} completed")
                
            except asyncio.TimeoutError:
                self.logger.error(f"Timeout for debater 1 in round {round_num}")
                raise
            
            # Small delay between debaters
            await asyncio.sleep(2)
            
            # Debater 2 (Defender) responds
            task2 = progress.add_task(f"[yellow]{self.debater_2.model_name} responding...", total=None)
            
            try:
                arg2 = await asyncio.wait_for(
                    self.debater_2.generate_argument(
                        session.topic, 
                        session.concept_type, 
                        session.arguments, 
                        round_num
                    ),
                    timeout=self.config.DEBATE_TIMEOUT
                )
                session.arguments.append(arg2)
                progress.update(task2, description=f"[green]{self.debater_2.model_name} completed")
                
            except asyncio.TimeoutError:
                self.logger.error(f"Timeout for debater 2 in round {round_num}")
                raise
    
    async def _generate_synthesis(self, session: DebateSession):
        """Generate a final synthesis of the debate"""
        
        self.console.print("\n[bold purple]Generating Synthesis...[/bold purple]")
        
        # Create a synthesizer to combine perspectives
        synthesizer = AIDebater(self.config.GEMINI_MODEL_1, DebateRole.SYNTHESIZER)
        
        # Build synthesis prompt
        synthesis_prompt = f"""
        Based on the complete debate on "{session.topic}", create a comprehensive synthesis that:
        
        1. Identifies the strongest theoretical arguments from both perspectives
        2. Resolves contradictions and finds common ground
        3. Proposes a unified theoretical framework
        4. Highlights key insights and practical implications
        5. Suggests areas for further theoretical development
        
        The debate included {len(session.arguments)} arguments across {self.config.MAX_DEBATE_ROUNDS} rounds.
        
        Create a coherent synthesis that captures the best ideas from the entire discussion.
        """
        
        try:
            # Add all arguments as context
            for arg in session.arguments:
                synthesis_prompt += f"\n\n{arg.role.value} ({arg.model_name}) - Round {arg.round_number}:\n{arg.content}"
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, synthesizer.model.generate_content, synthesis_prompt
            )
            
            session.final_synthesis = response.text
            
        except Exception as e:
            self.logger.error(f"Failed to generate synthesis: {str(e)}")
            session.final_synthesis = "Synthesis generation failed."
    
    async def _create_theory_framework(self, session: DebateSession) -> TheoryFramework:
        """Create a structured theory framework from the debate"""
        
        # Extract insights from all arguments
        all_insights = []
        all_foundations = []
        
        for arg in session.arguments:
            all_insights.extend(arg.key_insights)
            all_foundations.extend(arg.theoretical_foundations)
        
        # Create framework name
        framework_name = f"{session.concept_type.value.replace('_', ' ').title()} Framework - {session.session_id}"
        
        framework = TheoryFramework(
            name=framework_name,
            description=f"Theoretical framework developed through AI debate on: {session.topic}",
            concept_type=session.concept_type,
            core_principles=list(set(all_insights))[:10],  # Top 10 unique insights
            assumptions=self._extract_assumptions_from_debate(session),
            theoretical_basis=list(set(all_foundations)),
            risk_considerations=self._extract_risk_considerations(session),
            implementation_guidelines=self._extract_implementation_guidelines(session),
            validation_criteria=self._extract_validation_criteria(session),
            created_from_debate=session.session_id
        )
        
        return framework
    
    def _extract_assumptions_from_debate(self, session: DebateSession) -> List[str]:
        """Extract key assumptions from the debate content"""
        assumptions = []
        
        for arg in session.arguments:
            content_lower = arg.content.lower()
            
            # Look for assumption indicators
            assumption_phrases = [
                "assume", "assuming", "assumption", "given that", "if we accept",
                "premise", "foundation", "based on the idea"
            ]
            
            for phrase in assumption_phrases:
                if phrase in content_lower:
                    # Extract sentences containing assumptions
                    sentences = arg.content.split('.')
                    for sentence in sentences:
                        if phrase in sentence.lower() and len(sentence.strip()) > 20:
                            assumptions.append(sentence.strip())
        
        return list(set(assumptions))[:5]  # Top 5 unique assumptions
    
    def _extract_risk_considerations(self, session: DebateSession) -> List[str]:
        """Extract risk considerations from the debate"""
        risks = []
        
        risk_keywords = ["risk", "danger", "threat", "volatility", "uncertainty", 
                        "drawdown", "loss", "failure", "limitation"]
        
        for arg in session.arguments:
            sentences = arg.content.split('.')
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in risk_keywords):
                    if len(sentence.strip()) > 20:
                        risks.append(sentence.strip())
        
        return list(set(risks))[:7]  # Top 7 unique risk considerations
    
    def _extract_implementation_guidelines(self, session: DebateSession) -> List[str]:
        """Extract implementation guidelines from the debate"""
        guidelines = []
        
        implementation_keywords = ["implement", "execute", "apply", "deploy", 
                                 "strategy", "approach", "method", "process"]
        
        for arg in session.arguments:
            sentences = arg.content.split('.')
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in implementation_keywords):
                    if len(sentence.strip()) > 20:
                        guidelines.append(sentence.strip())
        
        return list(set(guidelines))[:8]  # Top 8 unique guidelines
    
    def _extract_validation_criteria(self, session: DebateSession) -> List[str]:
        """Extract validation criteria from the debate"""
        criteria = []
        
        validation_keywords = ["validate", "test", "measure", "evaluate", "assess",
                              "performance", "metric", "benchmark", "criteria"]
        
        for arg in session.arguments:
            sentences = arg.content.split('.')
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in validation_keywords):
                    if len(sentence.strip()) > 20:
                        criteria.append(sentence.strip())
        
        return list(set(criteria))[:6]  # Top 6 unique criteria
    
    def _display_debate_header(self, session: DebateSession):
        """Display the debate session header"""
        header_text = f"""
🤖 AI Trading Theory Debate Session

Topic: {session.topic}
Concept: {session.concept_type.value.replace('_', ' ').title()}
Session ID: {session.session_id}

Debaters:
• {self.debater_1.model_name} ({self.debater_1.role.value})
• {self.debater_2.model_name} ({self.debater_2.role.value})
        """
        
        self.console.print(Panel(header_text, title="[bold green]Debate Starting[/bold green]"))
    
    def _display_round_results(self, session: DebateSession, round_num: int):
        """Display results of a completed round"""
        round_args = [arg for arg in session.arguments if arg.round_number == round_num]
        
        for arg in round_args:
            self.console.print(f"\n[bold]{arg.model_name} ({arg.role.value}):[/bold]")
            self.console.print(Panel(arg.content[:500] + "..." if len(arg.content) > 500 else arg.content))
            
            if arg.key_insights:
                self.console.print(f"[dim]Key Insights: {', '.join(arg.key_insights[:3])}[/dim]")
    
    def _display_completion(self, session: DebateSession, framework: TheoryFramework):
        """Display debate completion summary"""
        completion_text = f"""
✅ Debate Completed Successfully!

Session: {session.session_id}
Duration: {(session.end_time - session.start_time).total_seconds():.1f} seconds
Arguments Generated: {len(session.arguments)}

Framework Created: {framework.name}
Core Principles: {len(framework.core_principles)}
Risk Considerations: {len(framework.risk_considerations)}

The theory framework has been added to your Algorithm & Rules Book.
        """
        
        self.console.print(Panel(completion_text, title="[bold green]Success![/bold green]"))