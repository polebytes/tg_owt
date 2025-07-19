import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional

from .debate_engine import DebateEngine
from .models import TradingConcept
from .knowledge_manager import KnowledgeManager

app = typer.Typer(help="AI Trading Theory Development Framework")
console = Console()

@app.command()
def start_debate(
    topic: str = typer.Argument(..., help="The trading theory topic to debate"),
    concept: str = typer.Option("micro_alpha", help="Type of trading concept (micro_alpha, risk_management, etc.)"),
    ):
    """Start a new AI debate session on a trading theory topic"""
    
    try:
        # Validate concept type
        concept_type = TradingConcept(concept)
    except ValueError:
        console.print(f"[red]Invalid concept type: {concept}[/red]")
        console.print("Valid options: " + ", ".join([c.value for c in TradingConcept]))
        raise typer.Exit(1)
    
    console.print(f"[bold green]Starting AI debate on:[/bold green] {topic}")
    console.print(f"[dim]Concept type: {concept_type.value}[/dim]\n")
    
    # Run the debate
    debate_engine = DebateEngine()
    
    try:
        asyncio.run(debate_engine.start_debate(topic, concept_type))
    except KeyboardInterrupt:
        console.print("\n[yellow]Debate interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Debate failed: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def list_frameworks(
    concept: Optional[str] = typer.Option(None, help="Filter by concept type")
):
    """List all theory frameworks in the knowledge base"""
    
    km = KnowledgeManager()
    
    if concept:
        frameworks = km.get_frameworks_by_concept(concept)
        title = f"Frameworks - {concept.replace('_', ' ').title()}"
    else:
        frameworks = km.rules_book.frameworks
        title = "All Frameworks"
    
    if not frameworks:
        console.print("[yellow]No frameworks found[/yellow]")
        return
    
    table = Table(title=title)
    table.add_column("Name", style="cyan")
    table.add_column("Concept", style="green")
    table.add_column("Principles", justify="center")
    table.add_column("Created", style="dim")
    
    for fw in frameworks:
        table.add_row(
            fw.name,
            fw.concept_type.value.replace('_', ' ').title(),
            str(len(fw.core_principles)),
            fw.created_at.strftime('%Y-%m-%d')
        )
    
    console.print(table)

@app.command()
def show_framework(name: str):
    """Show detailed information about a specific framework"""
    
    km = KnowledgeManager()
    
    framework = None
    for fw in km.rules_book.frameworks:
        if fw.name.lower() == name.lower() or name.lower() in fw.name.lower():
            framework = fw
            break
    
    if not framework:
        console.print(f"[red]Framework not found: {name}[/red]")
        return
    
    # Display framework details
    info_text = f"""
**Description:** {framework.description}
**Concept Type:** {framework.concept_type.value.replace('_', ' ').title()}
**Created:** {framework.created_at.strftime('%Y-%m-%d %H:%M:%S')}
**From Debate:** {framework.created_from_debate}
    """
    
    console.print(Panel(info_text, title=f"[bold]{framework.name}[/bold]"))
    
    # Core Principles
    if framework.core_principles:
        console.print("\n[bold]Core Principles:[/bold]")
        for i, principle in enumerate(framework.core_principles, 1):
            console.print(f"{i}. {principle}")
    
    # Risk Considerations
    if framework.risk_considerations:
        console.print("\n[bold]Risk Considerations:[/bold]")
        for risk in framework.risk_considerations:
            console.print(f"• {risk}")
    
    # Theoretical Foundations
    if framework.theoretical_basis:
        console.print("\n[bold]Theoretical Foundations:[/bold]")
        for basis in framework.theoretical_basis:
            console.print(f"• {basis}")

@app.command()
def search(query: str):
    """Search frameworks by name or description"""
    
    km = KnowledgeManager()
    frameworks = km.search_frameworks(query)
    
    if not frameworks:
        console.print(f"[yellow]No frameworks found matching: {query}[/yellow]")
        return
    
    console.print(f"[bold]Search Results for:[/bold] {query}\n")
    
    for fw in frameworks:
        console.print(f"[cyan]{fw.name}[/cyan]")
        console.print(f"  {fw.description}")
        console.print(f"  [dim]Type: {fw.concept_type.value} | Created: {fw.created_at.strftime('%Y-%m-%d')}[/dim]\n")

@app.command()
def export_framework(name: str):
    """Export a framework as standalone markdown file"""
    
    km = KnowledgeManager()
    
    try:
        export_path = asyncio.run(km.export_framework(name))
        
        if export_path:
            console.print(f"[green]Framework exported to:[/green] {export_path}")
        else:
            console.print(f"[red]Framework not found: {name}[/red]")
    
    except Exception as e:
        console.print(f"[red]Export failed: {str(e)}[/red]")

@app.command()
def show_book():
    """Show Algorithm & Rules Book statistics"""
    
    km = KnowledgeManager()
    book = km.rules_book
    
    stats_text = f"""
**Total Frameworks:** {len(book.frameworks)}
**Total Insights:** {book.total_insights}
**Debate Sessions:** {len(book.debate_sessions)}
**Created:** {book.created_at.strftime('%Y-%m-%d %H:%M:%S')}
**Last Updated:** {book.last_updated.strftime('%Y-%m-%d %H:%M:%S')}

**Book Location:** {km.rules_book_path}
    """
    
    console.print(Panel(stats_text, title="[bold]Algorithm & Rules Book[/bold]"))
    
    # Show concept distribution
    from collections import Counter
    concept_counts = Counter(fw.concept_type for fw in book.frameworks)
    
    if concept_counts:
        console.print("\n[bold]Framework Distribution:[/bold]")
        table = Table()
        table.add_column("Concept Type", style="cyan")
        table.add_column("Count", justify="center", style="green")
        
        for concept, count in concept_counts.items():
            table.add_row(concept.value.replace('_', ' ').title(), str(count))
        
        console.print(table)

@app.command()
def list_concepts():
    """List all available trading concept types"""
    
    console.print("[bold]Available Trading Concept Types:[/bold]\n")
    
    concept_descriptions = {
        TradingConcept.MICRO_ALPHA: "Small-scale market inefficiencies and rapid execution strategies",
        TradingConcept.RISK_MANAGEMENT: "Portfolio protection and loss mitigation frameworks",
        TradingConcept.MARKET_STRUCTURE: "Market mechanics and liquidity analysis",
        TradingConcept.ALGORITHMIC_STRATEGY: "Systematic and rule-based trading approaches",
        TradingConcept.PORTFOLIO_THEORY: "Asset allocation and optimization methodologies",
        TradingConcept.BEHAVIORAL_FINANCE: "Psychology and cognitive bias considerations"
    }
    
    for concept, description in concept_descriptions.items():
        console.print(f"[cyan]{concept.value}[/cyan]: {description}")

@app.command()
def demo():
    """Run a demonstration debate on NIFTY futures micro-alpha strategy"""
    
    console.print("[bold green]Running Demo: NIFTY Futures Micro-Alpha Strategy[/bold green]\n")
    
    topic = "Design a micro-alpha strategy for NIFTY futures that exploits order book imbalances and latency arbitrage opportunities"
    concept_type = TradingConcept.MICRO_ALPHA
    
    console.print(f"Topic: {topic}")
    console.print(f"Concept: {concept_type.value}\n")
    
    debate_engine = DebateEngine()
    
    try:
        asyncio.run(debate_engine.start_debate(topic, concept_type))
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Demo failed: {str(e)}[/red]")
        console.print("[dim]Make sure you have set the GEMINI_API_KEY environment variable[/dim]")

if __name__ == "__main__":
    app()