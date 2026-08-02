import { apiClient } from "@/lib/axios";
import type { WorkflowExecution } from "@/types/api";

export async function getWorkflowHistory(): Promise<WorkflowExecution[]> {
  const response = await apiClient.get("/workflow/history");
  const rawData = response.data;
  if (Array.isArray(rawData)) {
    return rawData.map((item: any) => ({
      executionId: String(item.id),
      execution_id: String(item.id),
      stage: item.workflow_status,
      status: item.workflow_status,
      progress: item.workflow_status === "COMPLETED" ? 100 : 50,
    }));
  }
  const data = rawData as { data?: WorkflowExecution[]; items?: WorkflowExecution[]; results?: WorkflowExecution[] };
  return data.data ?? data.items ?? data.results ?? [];
}

export async function getWorkflowExecution(executionId: string): Promise<WorkflowExecution> {
  const response = await apiClient.get(`/workflow/${executionId}`);
  const item = response.data as any;
  return {
    executionId: String(item.id),
    execution_id: String(item.id),
    stage: item.workflow_status,
    status: item.workflow_status,
    progress: item.workflow_status === "COMPLETED" ? 100 : 50,
  };
}