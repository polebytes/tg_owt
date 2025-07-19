import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import logging

from .config import Config
from .models import DebateSession, TheoryFramework, AlgorithmRulesBook

class KnowledgeManager:
    """Manages the growing knowledge base of trading theories"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("KnowledgeManager")
        
        # Initialize knowledge base
        self.rules_book_path = self.config.OUTPUT_DIR / self.config.RULES_BOOK_FILE
        self.rules_book = self._load_or_create_rules_book()
        
    def _load_or_create_rules_book(self) -> AlgorithmRulesBook:
        """Load existing rules book or create a new one"""
        
        rules_book_json_path = self.config.OUTPUT_DIR / "rules_book.json"
        
        if rules_book_json_path.exists():
            try:
                with open(rules_book_json_path, 'r') as f:
                    data = json.load(f)
                return AlgorithmRulesBook(**data)
            except Exception as e:
                self.logger.warning(f"Could not load existing rules book: {e}")
        
        # Create new rules book
        return AlgorithmRulesBook()
    
    async def save_debate_session(self, session: DebateSession):
        """Save a debate session to disk"""
        
        try:
            # Create session file
            session_file = self.config.DEBATE_LOGS_DIR / f"debate_{session.session_id}.json"
            
            with open(session_file, 'w') as f:
                json.dump(session.dict(), f, indent=2, default=str)
            
            # Add to rules book tracking
            if session.session_id not in self.rules_book.debate_sessions:
                self.rules_book.debate_sessions.append(session.session_id)
            
            self.logger.info(f"Saved debate session: {session.session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save debate session: {e}")
            raise
    
    async def add_theory_framework(self, framework: TheoryFramework):
        """Add a new theory framework to the rules book"""
        
        try:
            self.rules_book.add_framework(framework)
            await self._save_rules_book()
            await self._generate_markdown_book()
            
            self.logger.info(f"Added framework: {framework.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to add framework: {e}")
            raise
    
    async def _save_rules_book(self):
        """Save the rules book as JSON"""
        
        rules_book_json_path = self.config.OUTPUT_DIR / "rules_book.json"
        
        with open(rules_book_json_path, 'w') as f:
            json.dump(self.rules_book.dict(), f, indent=2, default=str)
    
    async def _generate_markdown_book(self):
        """Generate the markdown version of the Algorithm & Rules Book"""
        
        try:
            markdown_content = self._create_markdown_content()
            
            with open(self.rules_book_path, 'w') as f:
                f.write(markdown_content)
            
            self.logger.info("Generated markdown rules book")
            
        except Exception as e:
            self.logger.error(f"Failed to generate markdown book: {e}")
            raise
    
    def _create_markdown_content(self) -> str:
        """Create markdown content for the rules book"""
        
        content = f"""# {self.rules_book.title}

{self.rules_book.description}

**Created:** {self.rules_book.created_at.strftime('%Y-%m-%d %H:%M:%S')}  
**Last Updated:** {self.rules_book.last_updated.strftime('%Y-%m-%d %H:%M:%S')}  
**Total Frameworks:** {len(self.rules_book.frameworks)}  
**Total Insights:** {self.rules_book.total_insights}  
**Debate Sessions:** {len(self.rules_book.debate_sessions)}

---

## Table of Contents

"""
        
        # Generate table of contents
        for i, framework in enumerate(self.rules_book.frameworks, 1):
            content += f"{i}. [{framework.name}](#{framework.name.lower().replace(' ', '-').replace('-', '-')})\n"
        
        content += "\n---\n\n"
        
        # Generate framework sections
        for framework in self.rules_book.frameworks:
            content += self._create_framework_section(framework)
        
        # Add appendix
        content += self._create_appendix()
        
        return content
    
    def _create_framework_section(self, framework: TheoryFramework) -> str:
        """Create a markdown section for a theory framework"""
        
        section = f"""## {framework.name}

**Description:** {framework.description}

**Concept Type:** {framework.concept_type.value.replace('_', ' ').title()}

**Created From Debate:** {framework.created_from_debate}

**Created:** {framework.created_at.strftime('%Y-%m-%d %H:%M:%S')}

### Core Principles

"""
        
        for i, principle in enumerate(framework.core_principles, 1):
            section += f"{i}. {principle}\n"
        
        if framework.assumptions:
            section += "\n### Key Assumptions\n\n"
            for assumption in framework.assumptions:
                section += f"- {assumption}\n"
        
        if framework.theoretical_basis:
            section += "\n### Theoretical Foundations\n\n"
            for basis in framework.theoretical_basis:
                section += f"- {basis}\n"
        
        if framework.risk_considerations:
            section += "\n### Risk Considerations\n\n"
            for risk in framework.risk_considerations:
                section += f"- {risk}\n"
        
        if framework.implementation_guidelines:
            section += "\n### Implementation Guidelines\n\n"
            for guideline in framework.implementation_guidelines:
                section += f"- {guideline}\n"
        
        if framework.validation_criteria:
            section += "\n### Validation Criteria\n\n"
            for criteria in framework.validation_criteria:
                section += f"- {criteria}\n"
        
        section += "\n---\n\n"
        
        return section
    
    def _create_appendix(self) -> str:
        """Create appendix with additional information"""
        
        appendix = """## Appendix

### Debate Sessions

"""
        
        for session_id in self.rules_book.debate_sessions:
            appendix += f"- Session {session_id}: [debate_{session_id}.json](debate_logs/debate_{session_id}.json)\n"
        
        appendix += f"""

### Framework Statistics

| Concept Type | Count |
|--------------|-------|
"""
        
        # Count frameworks by type
        from collections import Counter
        type_counts = Counter(fw.concept_type for fw in self.rules_book.frameworks)
        
        for concept_type, count in type_counts.items():
            appendix += f"| {concept_type.value.replace('_', ' ').title()} | {count} |\n"
        
        appendix += f"""

### Development Timeline

"""
        
        # Sort frameworks by creation date
        sorted_frameworks = sorted(self.rules_book.frameworks, key=lambda x: x.created_at)
        
        for framework in sorted_frameworks:
            appendix += f"- **{framework.created_at.strftime('%Y-%m-%d')}**: {framework.name}\n"
        
        appendix += f"""

---

*This document is automatically generated by the AI Trading Theory Development Framework.*
*Each framework represents the synthesis of collaborative AI debate on trading concepts.*

"""
        
        return appendix
    
    def get_frameworks_by_concept(self, concept_type: str) -> List[TheoryFramework]:
        """Get frameworks filtered by concept type"""
        from .models import TradingConcept
        
        try:
            concept_enum = TradingConcept(concept_type)
            return self.rules_book.get_frameworks_by_type(concept_enum)
        except ValueError:
            return []
    
    def search_frameworks(self, query: str) -> List[TheoryFramework]:
        """Search frameworks by name or description"""
        query_lower = query.lower()
        
        matching_frameworks = []
        for framework in self.rules_book.frameworks:
            if (query_lower in framework.name.lower() or 
                query_lower in framework.description.lower()):
                matching_frameworks.append(framework)
        
        return matching_frameworks
    
    async def export_framework(self, framework_name: str) -> Optional[str]:
        """Export a specific framework as standalone markdown"""
        
        framework = None
        for fw in self.rules_book.frameworks:
            if fw.name == framework_name:
                framework = fw
                break
        
        if not framework:
            return None
        
        export_content = f"""# {framework.name}

Exported from Algorithm & Rules Book  
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{self._create_framework_section(framework)}
"""
        
        export_path = self.config.OUTPUT_DIR / f"{framework.name.replace(' ', '_').lower()}.md"
        
        with open(export_path, 'w') as f:
            f.write(export_content)
        
        return str(export_path)