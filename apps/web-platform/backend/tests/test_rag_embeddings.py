import pytest
from app.services.rag_embeddings import (
    VOYAGE_MODEL_ID,
    VOYAGE_VECTOR_DIMENSION,
    VectorDimensionMismatchError,
    validate_vector_dimension,
    cosine_similarity,
    generate_mock_embedding,
    get_rag_vector_schema,
)
from app.models import Idea, Organization, OrganizationMembership, User
from client_utils import create_test_client
from app.main import app
from app.db import get_db
from app.api.dependencies import get_current_user, get_current_membership


def test_voyage_dimension_is_strictly_512():
    assert VOYAGE_MODEL_ID == "voyage-3-lite"
    assert VOYAGE_VECTOR_DIMENSION == 512

    # Vector of correct length passes
    valid_vec = [0.1] * 512
    validate_vector_dimension(valid_vec)

    # 768 or 1536 dimension vector fails validation
    invalid_vec_768 = [0.1] * 768
    with pytest.raises(VectorDimensionMismatchError) as exc_768:
        validate_vector_dimension(invalid_vec_768)
    assert "768 does not match expected Voyage dimension 512" in str(exc_768.value)

    invalid_vec_1536 = [0.1] * 1536
    with pytest.raises(VectorDimensionMismatchError) as exc_1536:
        validate_vector_dimension(invalid_vec_1536)
    assert "1536 does not match expected Voyage dimension 512" in str(exc_1536.value)


def test_cosine_similarity_calculation():
    vec_a = generate_mock_embedding("မြန်မာ့သမိုင်း ရှေးဟောင်းအမွေအနှစ်")
    vec_b = generate_mock_embedding("မြန်မာ့သမိုင်း ရှေးဟောင်းအမွေအနှစ်")
    vec_c = generate_mock_embedding("နည်းပညာအကြောင်း စက်ရုပ်များ")

    assert len(vec_a) == 512
    # Self-similarity is 1.0
    sim_identical = cosine_similarity(vec_a, vec_b)
    assert pytest.approx(sim_identical, 0.001) == 1.0

    # Different texts yield valid similarity in [-1, 1]
    sim_diff = cosine_similarity(vec_a, vec_c)
    assert -1.0 <= sim_diff <= 1.0


def test_get_rag_vector_schema():
    schema = get_rag_vector_schema()
    assert schema["provider"] == "voyage"
    assert schema["model"] == "voyage-3-lite"
    assert schema["dimension"] == 512
    assert schema["pgvector_column"] == "vector(512)"


def test_rag_endpoints_api(db_session):
    org = Organization(name="RAG Org", slug="rag-org")
    user = User(email="rag@test.local", role="owner", password_hash="dummy-hash")
    db_session.add(org)
    db_session.add(user)
    db_session.flush()

    membership = OrganizationMembership(organization_id=org.id, user_id=user.id, role="owner")
    db_session.add(membership)

    idea = Idea(
        organization_id=org.id,
        title="ပုဂံခေတ် စေတီပုထိုးများ",
        concept="ရှေးဟောင်း ဗိသုကာပညာ",
        hook="မသိသေးတဲ့ လျှို့ဝှက်ချက်",
    )
    db_session.add(idea)
    db_session.commit()

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: {"id": user.id, "email": user.email, "role": "owner", "organization_id": org.id}
    app.dependency_overrides[get_current_membership] = lambda: membership

    try:
        client = create_test_client(app)

        # GET rag-config
        resp_cfg = client.get("/api/v1/search/rag-config")
        assert resp_cfg.status_code == 200
        cfg = resp_cfg.json()
        assert cfg["dimension"] == 512
        assert cfg["model"] == "voyage-3-lite"

        # GET semantic search
        resp_sem = client.get("/api/v1/search/semantic?q=ပုဂံခေတ်")
        assert resp_sem.status_code == 200
        data = resp_sem.json()
        assert data["vector_dimension"] == 512
        assert len(data["results"]) >= 1
        assert data["results"][0]["id"] == idea.id
    finally:
        app.dependency_overrides.clear()
