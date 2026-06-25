from .models import AuditLog


def log_action(actor, action, target_type, target_id=None, metadata=None):
    AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=target_id,
        metadata_json=metadata or {},
    )
