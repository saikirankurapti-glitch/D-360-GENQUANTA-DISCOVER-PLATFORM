import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute, PublicRoute } from './RouteGuards';
import { SidebarLayout } from '../layouts/SidebarLayout';
import { LoginPage } from '../features/auth/pages/LoginPage';
import { DashboardPage } from '../features/dashboard/pages/DashboardPage';
import { MetadataPage } from '../features/metadata/pages/MetadataPage';
import { QueryBuilderPage } from '../features/query_builder/pages/QueryBuilderPage';
import { ConnectorDashboard } from '../features/connectors/pages/ConnectorDashboard';
import { AddConnectorWizard } from '../features/connectors/pages/AddConnectorWizard';
import { SchemaDiscoveryView } from '../features/connectors/pages/SchemaDiscoveryView';
import { SyncMonitorDashboard } from '../features/connectors/pages/SyncMonitorDashboard';
import { EnterpriseIntegrationsPage } from '../features/connectors/pages/EnterpriseIntegrationsPage';
import { CompoundExplorerPage } from '../features/compounds/pages/CompoundExplorerPage';
import { SARDecompositionPage } from '../features/compounds/pages/SARDecompositionPage';
import { AnalysisWorkbench } from '../features/analytics/pages/AnalysisWorkbench';
import { AuditTrailPage } from '../features/admin/pages/AuditTrailPage';
import { ComplianceConsolePage } from '../features/compliance/pages/ComplianceConsolePage';
import { BioinformaticsDashboard } from '../features/bioinformatics/pages/BioinformaticsDashboard';
import { SequenceExplorerPage } from '../features/bioinformatics/pages/SequenceExplorerPage';
import { AlignmentPage } from '../features/bioinformatics/pages/AlignmentPage';
import { ClusteringPage } from '../features/bioinformatics/pages/ClusteringPage';
import { CopilotDashboard } from '../features/copilot/pages/CopilotDashboard';
import { WorkflowDesignerPage } from '../features/workflow/pages/WorkflowDesignerPage';

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      {/* Protected Routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<SidebarLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/metadata" element={<MetadataPage />} />
          <Route path="/query-builder" element={<QueryBuilderPage />} />
          <Route path="/copilot" element={<CopilotDashboard />} />
          <Route path="/analytics-workbench" element={<AnalysisWorkbench />} />
          <Route path="/compounds" element={<CompoundExplorerPage />} />
          <Route path="/sar" element={<SARDecompositionPage />} />
          <Route path="/connectors" element={<ConnectorDashboard />} />
          <Route path="/connectors/new" element={<AddConnectorWizard />} />
          <Route path="/connectors/sync-monitor" element={<SyncMonitorDashboard />} />
          <Route path="/connectors/enterprise" element={<EnterpriseIntegrationsPage />} />
          <Route path="/connectors/:id/schema" element={<SchemaDiscoveryView />} />
          <Route path="/admin/audit" element={<AuditTrailPage />} />
          <Route path="/compliance" element={<ComplianceConsolePage />} />
          <Route path="/bioinformatics" element={<BioinformaticsDashboard />} />
          <Route path="/sequences" element={<SequenceExplorerPage />} />
          <Route path="/alignments" element={<AlignmentPage />} />
          <Route path="/clusters" element={<ClusteringPage />} />
          <Route path="/workflows" element={<WorkflowDesignerPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};
