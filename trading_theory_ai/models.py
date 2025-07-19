from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DebateRole(str, Enum):
    """Roles for AI debaters"""
    CHALLENGER = "challenger"
    DEFENDER = "defender"
    SYNTHESIZER = "synthesizer"

class TradingConcept(str, Enum):
    """Types of trading concepts to develop"""
    MICRO_ALPHA = "micro_alpha"
    RISK_MANAGEMENT = "risk_management"
    MARKET_STRUCTURE = "market_structure"
    ALGORITHMIC_STRATEGY = "algorithmic_strategy"
    PORTFOLIO_THEORY = "portfolio_theory"
    BEHAVIORAL_FINANCE = "behavioral_finance"

class DebateArgument(BaseModel):
    """Single argument in a debate"""
    role: DebateRole
    model_name: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    round_number: int
    key_insights: List[str] = Field(default_factory=list)
    theoretical_foundations: List[str] = Field(default_factory=list)

class DebateSession(BaseModel):
    """Complete debate session"""
    topic: str
    concept_type: TradingConcept
    session_id: str
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    arguments: List[DebateArgument] = Field(default_factory=list)
    final_synthesis: Optional[str] = None
    key_outcomes: List[str] = Field(default_factory=list)
    status: str = "active"  # active, completed, failed

class TheoryFramework(BaseModel):
    """Structured trading theory framework"""
    name: str
    description: str
    concept_type: TradingConcept
    core_principles: List[str]
    assumptions: List[str]
    theoretical_basis: List[str]
    risk_considerations: List[str]
    implementation_guidelines: List[str]
    validation_criteria: List[str]
    created_from_debate: str  # session_id
    created_at: datetime = Field(default_factory=datetime.now)

class AlgorithmRulesBook(BaseModel):
    """The growing knowledge base of trading theories"""
    title: str = "Algorithm & Rules Book"
    description: str = "AI-Developed Trading Theory Framework"
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    frameworks: List[TheoryFramework] = Field(default_factory=list)
    debate_sessions: List[str] = Field(default_factory=list)  # session_ids
    total_insights: int = 0
    
    def add_framework(self, framework: TheoryFramework):
        """Add a new theory framework to the book"""
        self.frameworks.append(framework)
        self.total_insights += len(framework.core_principles)
        self.last_updated = datetime.now()
    
    def get_frameworks_by_type(self, concept_type: TradingConcept) -> List[TheoryFramework]:
        """Get all frameworks of a specific type"""
        return [fw for fw in self.frameworks if fw.concept_type == concept_type]