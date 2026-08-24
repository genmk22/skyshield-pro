import type {
  SatelliteSummary, ConjunctionEvent, RiskExplanation, MonteCarloResult,
  MultiThreatEvaluationResult, CommandPayload, SignedCommandPayload, VerificationResult, AuditLogEvent
} from '../types';

const API_BASE = '/api';

export async function fetchSatellites(live: boolean = false): Promise<SatelliteSummary[]> {
  const res = await fetch(`${API_BASE}/satellites?live=${live}`);
  if (!res.ok) throw new Error('Failed to fetch satellites');
  return res.json();
}

export async function fetchConjunctions(): Promise<ConjunctionEvent[]> {
  const res = await fetch(`${API_BASE}/conjunctions`);
  if (!res.ok) throw new Error('Failed to fetch conjunctions');
  return res.json();
}

export async function analyzeConjunctions(primaryId: number): Promise<ConjunctionEvent[]> {
  const res = await fetch(`${API_BASE}/conjunctions/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ primary_norad_id: primaryId, lookahead_hours: 72.0 })
  });
  if (!res.ok) throw new Error('Failed to analyze conjunctions');
  return res.json();
}

export async function fetchRiskExplanation(conjunctionId: string): Promise<RiskExplanation> {
  const res = await fetch(`${API_BASE}/risk/explain/${conjunctionId}`);
  if (!res.ok) throw new Error('Failed to fetch risk explanation');
  return res.json();
}

export async function runMonteCarlo(conjunctionId: string, samples: number = 10000): Promise<MonteCarloResult> {
  const res = await fetch(`${API_BASE}/risk/monte-carlo`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conjunction_id: conjunctionId, num_samples: samples })
  });
  if (!res.ok) throw new Error('Failed to run Monte Carlo simulation');
  return res.json();
}

export async function evaluateManeuvers(satelliteId: string = "25544", forceNoSafe: boolean = false): Promise<MultiThreatEvaluationResult> {
  const res = await fetch(`${API_BASE}/maneuvers/evaluate?satellite_id=${satelliteId}&force_no_safe=${forceNoSafe}`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to evaluate maneuvers');
  return res.json();
}

export async function createCommand(satelliteId: string = "25544", candidateId?: string): Promise<CommandPayload> {
  let url = `${API_BASE}/commands/create?satellite_id=${satelliteId}`;
  if (candidateId) url += `&candidate_id=${candidateId}`;
  const res = await fetch(url, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to create command');
  return res.json();
}

export async function signCommand(payload: CommandPayload, operatorId: string = "FLIGHT_DYNAMICS_OPERATOR_01"): Promise<SignedCommandPayload> {
  const res = await fetch(`${API_BASE}/commands/sign?operator_id=${operatorId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to sign command');
  return res.json();
}

export async function verifyCommand(signedPayload: SignedCommandPayload): Promise<VerificationResult> {
  const res = await fetch(`${API_BASE}/commands/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(signedPayload)
  });
  if (!res.ok) throw new Error('Failed to verify command');
  return res.json();
}

export async function tamperCommandDemo(signedPayload: SignedCommandPayload, field: string = "delta_v_ms", value: any = 99.9): Promise<VerificationResult> {
  const res = await fetch(`${API_BASE}/commands/tamper-demo`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      original_signed_command: signedPayload,
      field_to_tamper: field,
      tampered_value: value
    })
  });
  if (!res.ok) throw new Error('Failed to run tamper demo');
  return res.json();
}

export async function fetchScenarios(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/scenarios`);
  if (!res.ok) throw new Error('Failed to fetch scenarios');
  return res.json();
}

export async function runScenario(scenarioId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/scenarios/${scenarioId}/run`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to run scenario');
  return res.json();
}

export async function fetchAuditLogs(): Promise<AuditLogEvent[]> {
  const res = await fetch(`${API_BASE}/logs`);
  if (!res.ok) throw new Error('Failed to fetch audit logs');
  return res.json();
}
