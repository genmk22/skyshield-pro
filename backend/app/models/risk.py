from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RiskFactor(BaseModel):
    name: str
    value: str
    weight: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    threshold_crossed: bool

class RiskExplanation(BaseModel):
    conjunction_id: str
    risk_level: str
    summary: str
    key_factors: List[RiskFactor]
    data_freshness_impact: str
    uncertainty_scaling_factor: float
    recommendation_note: str

class MonteCarloRequest(BaseModel):
    conjunction_id: str
    num_samples: int = 10000
    random_seed: Optional[int] = 42

class MonteCarloResult(BaseModel):
    conjunction_id: str
    num_samples: int
    collision_count: int
    analytical_pc: float
    monte_carlo_pc: float
    percentage_difference: float
    convergence_series: List[Dict[str, Any]]
    execution_time_ms: float
