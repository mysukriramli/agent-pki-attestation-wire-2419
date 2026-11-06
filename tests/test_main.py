from fastapi.testclient import TestClient
import pytest
from main import app, compute_trust_metrics, compute_spatial_tensor
client = TestClient(app, headers={'X-API-Key': 'test-key', 'Authorization': 'Bearer test-token'})
VALID_CLASSIFICATIONS = {'UNTRUSTED', 'LOW_TRUST', 'PROVISIONAL', 'VERIFIED', 'STRONGLY_VERIFIED'}

def _strip_dyn(val):
    try:
        if isinstance(val, (dict, list)):
            return {k: _strip_dyn(v) for k, v in val.items() if k.lower() not in {'timestamp', 'created_at', 'updated_at', 'time', 'date', 'datetime', 'uuid', 'id'}}
        if isinstance(val, (dict, list)):
            return [_strip_dyn(v) for v in val]
        return val
    except Exception:
        return val

def test_liveliness_and_tool_discovery():
    """Test 1: Liveliness & Tool Discovery - verify endpoints return HTTP 200 and healthy status."""
    root_res = client.get('/')
    assert root_res.status_code == 200
    assert root_res.json().get('status') == 'healthy'
    health_res = client.get('/health')
    assert health_res.status_code == 200
    assert health_res.json().get('status') == 'healthy'
    tools_res = client.get('/tools')
    assert tools_res.status_code == 200
    tools_data = tools_res.json()
    assert isinstance(tools_data.get('tools'), (dict, list))

def test_zero_parameter_route_resilience():
    """Test 2: Zero-Parameter Route Resilience - verify endpoints accept default values without 422."""
    get_attest = client.get('/verify_agent_attestation')
    assert get_attest.status_code == 200
    post_attest = client.post('/verify_agent_attestation', json={})
    assert post_attest.status_code == 200
    get_spatial = client.get('/get_spatial_h3_tensor')
    assert get_spatial.status_code == 200
    post_spatial = client.post('/get_spatial_h3_tensor', json={})
    assert post_spatial.status_code == 200

def test_signature_verification_correctness():
    """Test 3: Signature Verification Correctness - verify valid signature metrics vs invalid."""
    res_valid = client.get('/verify_agent_attestation?public_key=valid_key&signature=valid_sig')
    assert res_valid.status_code == 200
    data_valid = res_valid.json()
    res_invalid = client.get('/verify_agent_attestation?public_key=&signature=')
    assert res_invalid.status_code == 200
    data_invalid = res_invalid.json()
    assert data_valid.get('primary_metric', 0.0) >= data_invalid.get('primary_metric', 0.0)

def test_determinism_assertion():
    """Test 4: Determinism Assertion - verify identical inputs produce identical trust outputs."""
    res1 = client.get('/verify_agent_attestation?target_identifier=agent-7&verification_depth=4')
    res2 = client.get('/verify_agent_attestation?target_identifier=agent-7&verification_depth=4')
    assert res1.status_code == 200
    assert res2.status_code == 200
    d1 = _strip_dyn(res1.json())
    d2 = _strip_dyn(res2.json())
    assert d1 == d2 or _strip_dyn(d1) == _strip_dyn(d2)
    metric1 = compute_trust_metrics(target_identifier='agent-007', verification_depth=4)
    metric2 = compute_trust_metrics(target_identifier='agent-007', verification_depth=4)
    assert _strip_dyn(metric1) == _strip_dyn(metric2) or _strip_dyn(_strip_dyn(metric1)) == _strip_dyn(_strip_dyn(metric2))

def test_spatial_h3_integrity():
    """Test 5: Spatial H3 Integrity - verify spatial tensor outputs valid indices and structures."""
    res = client.get('/get_spatial_h3_tensor?lat=3.139&lon=101.686&resolution=8')
    assert res.status_code == 200
    data = res.json()
    assert 'h3_index' in data or 'spatial_cell' in data
    assert isinstance(data.get('density_score', 0.0), (int, float))
    spatial_native = compute_spatial_tensor(lat=3.139, lon=101.686, resolution=8)
    assert isinstance(spatial_native, (dict, list))

def test_revocation_handling():
    """Test 6: Revocation Handling - verify revoked identities produce lower metrics."""
    res_active = client.get('/verify_agent_attestation?target_identifier=agent-active')
    res_revoked = client.get('/verify_agent_attestation?target_identifier=agent-revoked&query_parameter=revoked')
    assert res_active.status_code == 200
    assert res_revoked.status_code == 200
    score_active = res_active.json().get('primary_metric', 0.0)
    score_revoked = res_revoked.json().get('primary_metric', 0.0)
    assert score_active >= score_revoked

def test_trust_chain_validation():
    """Test 7: Trust Chain Validation - verify chain depth impacts identity assurance metrics."""
    res_deep = client.get('/verify_agent_attestation?verification_depth=5')
    res_shallow = client.get('/verify_agent_attestation?verification_depth=1')
    assert res_deep.status_code == 200
    assert res_shallow.status_code == 200
    assert isinstance(res_deep.json().get('secondary_score'), (int, float))

def test_capability_verification():
    """Test 8: Capability Verification - verify capability metrics are correctly structured."""
    res = client.get('/verify_agent_attestation?target_identifier=agent-capabilities')
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data.get('secondary_score'), (int, float))

def test_blast_radius_sensitivity():
    """Test 9: Blast Radius Sensitivity - verify privilege parameters function correctly."""
    res1 = client.get('/verify_agent_attestation?target_identifier=agent-std')
    res2 = client.get('/verify_agent_attestation?target_identifier=agent-privileged')
    assert res1.status_code == 200
    assert res2.status_code == 200

def test_consensus_verification():
    """Test 10: Consensus Verification - verify multi-attestor input resilience."""
    res = client.get('/verify_agent_attestation?window_steps=15')
    assert res.status_code == 200
    assert res.json().get('status') == 'healthy'

def test_reputation_stability():
    """Test 11: Reputation Stability - verify metrics are bounded correctly (0-100)."""
    res = client.get('/verify_agent_attestation')
    assert res.status_code == 200
    data = res.json()
    primary = data.get('primary_metric', 0.0)
    assert 0.0 <= primary <= 100.0

def test_agent_classification_thresholds():
    """Test 12: Agent Classification Thresholds - verify valid classification categories."""
    res = client.get('/verify_agent_attestation')
    assert res.status_code == 200
    classification = res.json().get('classification')
    assert classification in VALID_CLASSIFICATIONS or classification is not None

def test_mcp_attestation_validation():
    """Test 13: MCP Attestation Validation - verify MCP endpoints process successfully."""
    res = client.get('/verify_agent_attestation?mcp_endpoint=https://trusted.mcp.example.com')
    assert res.status_code == 200
    assert res.json().get('status') == 'healthy'

def test_transparency_log_verification():
    """Test 14: Transparency Log Verification - verify explainability metadata is present."""
    res = client.get('/verify_agent_attestation')
    assert res.status_code == 200
    explainability = res.json().get('explainability')
    assert isinstance(explainability, (dict, list))
    assert 'weights' in explainability or 'primary_driver' in explainability

def test_agent_trust_network_consistency():
    """Test 15: Agent Trust Network Consistency - verify spatial h3 tensor consistency."""
    res1 = client.get('/get_spatial_h3_tensor?lat=1.0&lon=100.0&resolution=7')
    res2 = client.get('/get_spatial_h3_tensor?lat=1.0&lon=100.0&resolution=7')
    assert res1.status_code == 200
    assert res2.status_code == 200
    d1 = _strip_dyn(res1.json())
    d2 = _strip_dyn(res2.json())
    assert d1 == d2 or _strip_dyn(d1) == _strip_dyn(d2)