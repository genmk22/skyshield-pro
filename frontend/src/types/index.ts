export interface SatelliteSummary {
  id: string;
  norad_id: number;
  name: string;
  object_type: string;
  tle_line1: string;
  tle_line2: string;
  epoch_datetime: string;
  age_hours: number;
  confidence_level: 'HIGH' | 'MODERATE' | 'LOW' | 'STALE';
  semi_major_axis_km: number;
  eccentricity: number;
  inclination_deg: number;
  period_min: number;
  apogee_km: number;
  perigee_km: number;
}

export interface EncouterGeometry {
  miss_distance_km: number;
  radial_sep_km: number;
  along_track_sep_km: number;
  cross_track_sep_km: number;
  relative_velocity_kms: number;
  relative_position_eci: number[];
  relative_velocity_eci: number[];
}

export interface ConjunctionEvent {
  id: string;
  primary_norad_id: number;
  primary_name: string;
  secondary_norad_id: number;
  secondary_name: string;
  secondary_type: string;
  tca: string;
  time_to_tca_hours: number;
  geometry: EncouterGeometry;
  estimated_pc: number;
  monte_carlo_pc?: number;
  risk_level: 'SAFE' | 'MONITOR' | 'WARNING' | 'HIGH RISK' | 'CRITICAL';
  primary_tle_age_hours: number;
  secondary_tle_age_hours: number;
  combined_uncertainty_m: number;
  confidence: string;
  is_approximate: boolean;
}

export interface RiskFactor {
  name: string;
  value: string;
  weight: string;
  description: string;
  threshold_crossed: boolean;
}

export interface RiskExplanation {
  conjunction_id: string;
  risk_level: string;
  summary: string;
  key_factors: RiskFactor[];
  data_freshness_impact: string;
  uncertainty_scaling_factor: number;
  recommendation_note: string;
}

export interface MonteCarloResult {
  conjunction_id: string;
  num_samples: number;
  collision_count: number;
  analytical_pc: number;
  monte_carlo_pc: number;
  percentage_difference: number;
  convergence_series: { samples: number; mc_pc: number; analytical_pc: number }[];
  execution_time_ms: number;
}

export interface ManeuverCandidate {
  id: string;
  direction: string;
  delta_v_ms: number;
  burn_epoch: string;
  delta_v_components_kms: number[];
  estimated_fuel_cost_kg: number;
  risk_before: number;
  risk_after: number;
  risk_reduction_pct: number;
  post_maneuver_miss_distance_km: number;
  affected_threats_count: number;
  score: number;
  is_valid: boolean;
  status: string;
  failure_reason?: string;
}

export interface MultiThreatEvaluationResult {
  satellite_id: string;
  total_active_threats: number;
  evaluated_candidates_count: number;
  best_candidate?: ManeuverCandidate;
  all_candidates: ManeuverCandidate[];
  has_safe_maneuver: boolean;
  no_safe_maneuver_reason?: string;
}

export interface CommandPayload {
  command_id: string;
  mission_id: string;
  satellite_id: string;
  timestamp: string;
  maneuver_type: string;
  delta_v_ms: number;
  direction: string;
  execution_time: string;
  status: string;
}

export interface SignedCommandPayload {
  command: CommandPayload;
  canonical_json: string;
  payload_hash_sha256: string;
  signature_base64: string;
  algorithm: string;
  signed_by: string;
  signed_at: string;
}

export interface VerificationResult {
  command_id: string;
  is_valid: boolean;
  status_message: string;
  verification_time: string;
  tampered_fields?: string[];
}

export interface AuditLogEvent {
  id: string;
  timestamp: string;
  event_type: string;
  object_id: string;
  status: string;
  details: Record<string, any>;
}
