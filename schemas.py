from datetime import timezone as dt_timezone
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(default='healthy', description='Service health status')
    timestamp: str = Field(default_factory=lambda: datetime.now(dt_timezone.utc).isoformat(), description='UTC ISO-8601 timestamp')

class ToolItem(BaseModel):
    name: str = Field(default='', description='Name of the agent or MCP tool')
    description: str = Field(default='', description='Tool description')
    input_schema: Dict[str, Any] = Field(default_factory=dict, description='Input schema definition')
    output_schema: Dict[str, Any] = Field(default_factory=dict, description='Output schema definition')

class ToolsResponse(BaseModel):
    tools: List[Dict[str, Any]] = Field(default_factory=list, description='List of available agent and MCP tools')

class ExplainabilityDetail(BaseModel):
    primary_driver: str = Field(default='signature_validity', description='Primary driving factor of the score')
    weights: Dict[str, float] = Field(default_factory=lambda: {'identity_assurance': 0.35, 'capability_assurance': 0.3, 'reputation_stability': 0.2, 'attestation_consensus': 0.15}, description='Weight distribution for metrics')

class VerifyAgentAttestationRequest(BaseModel):
    target_identifier: str = Field(default='agent-001', description='Unique target agent or entity identifier')
    query_parameter: str = Field(default='verify', description='Query mode or action parameter')
    lat: float = Field(default=0.0, description='Latitude coordinate')
    lon: float = Field(default=0.0, description='Longitude coordinate')
    window_steps: int = Field(default=10, description='Temporal or step window size')

class VerifyAgentAttestationResponse(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(dt_timezone.utc).isoformat(), description='UTC ISO-8601 timestamp')
    status: str = Field(default='healthy', description='Execution status')
    primary_metric: float = Field(default=94.7, description='Primary trust score (0-100)')
    secondary_score: float = Field(default=0.98, description='Secondary assurance ratio')
    state_index: float = Field(default=92.8, description='State classification index')
    classification: str = Field(default='STRONGLY_VERIFIED', description='Trust classification category')
    explainability: ExplainabilityDetail = Field(default_factory=ExplainabilityDetail, description='Explainability breakdown')

class GetSpatialH3TensorRequest(BaseModel):
    lat: float = Field(default=2.0442, description='Latitude coordinate')
    lon: float = Field(default=102.5689, description='Longitude coordinate')
    resolution: int = Field(default=8, description='H3 spatial resolution index (7-9)')

class GetSpatialH3TensorResponse(BaseModel):
    h3_index: str = Field(default='886520d81dfffff', description='H3 cell index string')
    spatial_cell: str = Field(default='886520d81dfffff', description='Spatial cell identifier')
    density_score: float = Field(default=64.2, description='Trust density score')
    terrain_state_index: float = Field(default=75.1, description='Terrain trust state index')
    status: str = Field(default='ACTIVE', description='Spatial region status')

class GenericAttestationRequest(BaseModel):
    agent_id: str = Field(default='agent-001', description='Identifier of the agent')
    public_key: str = Field(default='ed25519_default_pub_key', description='Public key material')
    signature: str = Field(default='default_signature', description='Cryptographic signature')
    mcp_endpoint: str = Field(default='https://example.com/mcp', description='MCP server endpoint URI')
    verification_depth: int = Field(default=3, description='Chain verification depth')
    lat: float = Field(default=0.0, description='Optional latitude coordinate')
    lon: float = Field(default=0.0, description='Optional longitude coordinate')

class GenericAttestationResponse(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(dt_timezone.utc).isoformat(), description='UTC timestamp')
    agent_id: str = Field(default='agent-001', description='Target agent identifier')
    identity_assurance_index: float = Field(default=0.95, description='Identity Assurance Index (IAI)')
    capability_assurance_index: float = Field(default=0.9, description='Capability Assurance Index (CAI)')
    reputation_stability_index: float = Field(default=0.92, description='Reputation Stability Index (RSI)')
    risk_exposure_index: float = Field(default=0.05, description='Risk Exposure Index (REI)')
    trust_score: float = Field(default=92.5, description='Composite Trust Score (0-100)')
    blast_radius: float = Field(default=0.15, description='Blast Radius Score')
    revocation_status: bool = Field(default=False, description='Whether identity is revoked')
    readiness_state: str = Field(default='TRUST', description='Agent operational readiness state')
    classification: str = Field(default='STRONGLY_VERIFIED', description='Trust classification level')
    details: Dict[str, Any] = Field(default_factory=dict, description='Additional diagnostic metrics')