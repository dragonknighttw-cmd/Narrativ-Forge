export const WORKFLOW_STATES = [
  "empty",
  "loading",
  "uploading",
  "processing",
  "completed",
  "failed",
  "retrying",
  "rejected",
  "offline",
  "read_only",
  "permission_denied",
  "session_expired",
  "drive_disconnected",
  "drive_export_failed",
  "storage_warning",
  "unsupported_file",
  "critical_quality_issue",
] as const;

export type WorkflowState = (typeof WORKFLOW_STATES)[number];

export type WorkflowStateSpec = {
  labelKey: string;
  actionKey?: string;
  blocking: boolean;
};

const BLOCKING = new Set<WorkflowState>([
  "failed",
  "rejected",
  "permission_denied",
  "session_expired",
  "drive_disconnected",
  "drive_export_failed",
  "unsupported_file",
  "critical_quality_issue",
]);

export function workflowStateSpec(state: WorkflowState): WorkflowStateSpec {
  return {
    labelKey: `state.${state}.title`,
    actionKey: state === "completed" || state === "loading" ? undefined : `state.${state}.action`,
    blocking: BLOCKING.has(state),
  };
}

export function isBlockingWorkflowState(state: WorkflowState): boolean {
  return BLOCKING.has(state);
}
