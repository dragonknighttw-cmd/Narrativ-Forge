from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.api.routes.phase4 import ensure_membership
from app.models import BillingSubscription, OrganizationMembership


pytestmark = pytest.mark.unit


def test_existing_membership_recovers_from_concurrent_subscription_creation():
    membership = SimpleNamespace(organization_id="org-1", user_id="user-1", role="owner")
    existing_subscription = SimpleNamespace(organization_id="org-1")

    membership_query = MagicMock()
    membership_query.filter.return_value.order_by.return_value.first.return_value = membership

    initial_subscription_query = MagicMock()
    initial_subscription_query.filter.return_value.first.return_value = None

    recheck_subscription_query = MagicMock()
    recheck_subscription_query.filter.return_value.first.return_value = existing_subscription

    db = MagicMock()
    db.query.side_effect = [
        membership_query,
        initial_subscription_query,
        recheck_subscription_query,
    ]
    db.get.return_value = SimpleNamespace(plan="trial")
    db.commit.side_effect = IntegrityError("insert", {}, RuntimeError("unique constraint"))

    result = ensure_membership(db, {"id": "user-1", "email": "owner@example.test", "role": "owner"})

    assert result is membership
    db.add.assert_called_once()
    assert isinstance(db.add.call_args.args[0], BillingSubscription)
    db.rollback.assert_called_once()
    db.refresh.assert_called_once_with(membership)


def test_existing_membership_does_not_hide_unrelated_integrity_error():
    membership = SimpleNamespace(organization_id="org-1", user_id="user-1", role="owner")

    membership_query = MagicMock()
    membership_query.filter.return_value.order_by.return_value.first.return_value = membership
    initial_subscription_query = MagicMock()
    initial_subscription_query.filter.return_value.first.return_value = None
    recheck_subscription_query = MagicMock()
    recheck_subscription_query.filter.return_value.first.return_value = None

    db = MagicMock()
    db.query.side_effect = [
        membership_query,
        initial_subscription_query,
        recheck_subscription_query,
    ]
    db.get.return_value = SimpleNamespace(plan="trial")
    db.commit.side_effect = IntegrityError("insert", {}, RuntimeError("unrelated integrity error"))

    with pytest.raises(IntegrityError):
        ensure_membership(db, {"id": "user-1", "email": "owner@example.test", "role": "owner"})

    db.rollback.assert_called_once()
    db.refresh.assert_not_called()
