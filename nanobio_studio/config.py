from dataclasses import dataclass

@dataclass(frozen=True)
class AIConfig:
    # Optimization defaults
    n_trials: int = 200
    top_k: int = 10
    random_seed: int = 42

    # Sampling / constraints defaults
    size_nm_min: float = 30.0
    size_nm_max: float = 200.0
    charge_mV_min: float = -30.0
    charge_mV_max: float = 30.0

    # Safety constraints (soft/hard can be handled in objectives)
    pdi_max: float = 0.25

AI_DEFAULTS = AIConfig()
