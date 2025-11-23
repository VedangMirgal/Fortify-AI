# agent_context.py

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List


@dataclass
class AgentEvent:
    agent_name: str
    step: str
    details: Dict[str, Any]


@dataclass
class AgentContext:
    """
    Shared context passed between agents during a run.
    - run_id: unique id for this analysis run
    - shared_state: arbitrary key/value state agents can read/write
    - events: structured log of what each agent did (for observability / debugging)
    """
    run_id: str
    shared_state: Dict[str, Any] = field(default_factory=dict)
    events: List[AgentEvent] = field(default_factory=list)

    def log(self, agent_name: str, step: str, **details: Any) -> None:
        """
        Record an event from an agent. e.g.
        context.log("failure_agent", "simulated_scenarios", count=5)
        """
        self.events.append(AgentEvent(agent_name=agent_name, step=step, details=details))

    def to_dict(self) -> Dict[str, Any]:
        """Convert context + events to a plain dict (for saving to JSON)."""
        return {
            "run_id": self.run_id,
            "shared_state": self.shared_state,
            "events": [
                {
                    "agent_name": e.agent_name,
                    "step": e.step,
                    "details": e.details,
                }
                for e in self.events
            ],
        }
