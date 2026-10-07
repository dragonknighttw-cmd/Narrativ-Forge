from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StorageThresholds:
    warning: float = 0.80
    critical: float = 0.90
    emergency: float = 0.95

    def __post_init__(self) -> None:
        values = (self.warning, self.critical, self.emergency)
        if any(value < 0 or value > 1 for value in values):
            raise ValueError("storage thresholds must be between 0 and 1")
        if not self.warning <= self.critical <= self.emergency:
            raise ValueError("storage thresholds must be ordered warning <= critical <= emergency")


@dataclass(frozen=True)
class StorageUsage:
    used_bytes: int
    capacity_bytes: int

    @property
    def ratio(self) -> float:
        if self.capacity_bytes <= 0:
            return 1.0
        return max(0.0, min(1.0, self.used_bytes / self.capacity_bytes))

    def state(self, thresholds: StorageThresholds = StorageThresholds()) -> str:
        if self.ratio >= thresholds.emergency:
            return "emergency"
        if self.ratio >= thresholds.critical:
            return "critical"
        if self.ratio >= thresholds.warning:
            return "warning"
        return "normal"



def classify_storage_usage(used_bytes: int, capacity_bytes: int, thresholds: StorageThresholds = StorageThresholds()) -> StorageUsage:
    if used_bytes < 0 or capacity_bytes < 0:
        raise ValueError("storage sizes must be non-negative")
    return StorageUsage(used_bytes=used_bytes, capacity_bytes=capacity_bytes)


def can_delete_asset(*, is_final: bool, is_approved: bool, is_only_copy: bool, retention_expired: bool) -> bool:
    if is_final or is_approved or is_only_copy:
        return False
    return retention_expired
