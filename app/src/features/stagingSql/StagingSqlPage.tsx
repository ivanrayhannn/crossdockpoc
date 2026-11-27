import { SimulationFrame } from '../../components/SimulationFrame';

/**
 * Staging Sync SQL: the staging tables (TB_H_STG_APPOLE_KANBAN / _EXPORT, TB_H_STG_GTOPAS) and the AP POLE upload views in SQLite,
 * with six [Sync] runs (OPERATION_TYPE 1 to 5) and the robot queries. Built by
 * deliverables/function_list_v2/erd/proposal_staging_sync/simulation/sql_studio/build_sql_studio.py.
 */
export function StagingSqlPage() {
  return <SimulationFrame file="staging-sql-studio.html?v=2" title="Staging SQL Studio" />;
}

/** Staging Upload Files: from the staging rows of a [Sync] to the EXPORT_PRE, KANBAN and EXPORT_POST files, per OPERATION_TYPE. */
export function StagingUploadFilesPage() {
  return <SimulationFrame file="staging-upload-files.html?v=5" title="Staging to upload files simulation" />;
}
