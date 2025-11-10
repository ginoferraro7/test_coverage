export const ROUTES = {
  // AUTH
  main: '/',
  login: '/login',
  login2: '/login/',
  passwordReset: '/password-reset',
  verifyAccount: '/verifyaccount/[uuidb64]/[token]',
  version: '/version',

  // DASHBOARD
  dashboard: '/dashboard',

  //PROFILE PAGE
  settings: '/profile/settings',
  changePassword: '/profile/change-password',
  createToken: '/profile/create-token',

  // SECURITY PAGE
  createUser: '/security/users/invite-new-user',
  users: '/security/users',
  editUser: (userId: string) => `/security/users/${userId}/edit-user`,
  editRole: (roleId: string) => `/security/roles/${roleId}/edit-role`,
  createRole: '/security/roles/new-role',
  roles: '/security/roles',
  editRowPolicy: (tableId: string, rowPolicyId: string) =>
    `/security/row-policies/${tableId}/${rowPolicyId}/edit-row-policy`,
  createRowPolicy: '/security/row-policies/new-row-policy',
  rowPolicies: '/security/row-policies',
  rowPoliciesWithTable: (tableId: string, tableName: string) =>
    `/security/row-policies/?table_id=${tableId}&data=${tableName}`,
  auditTrails: '/security/audit-trails',
  authLogs: '/security/auth-logs',
  buckets: '/security/buckets',
  createBucket: '/security/new-bucket',
  editBucket: (bucketId: string) => `/security/buckets/${bucketId}/`,
  credentials: '/security/credentials',
  createCredential: '/security/new-credential',
  editCredential: (credentialId: string) => `/security/credentials/${credentialId}/`,
  pendingInvites: '/security/pending-invites',
  serviceAccounts: '/security/service-accounts',
  createServiceAccount: '/security/new-service-account',
  editServiceAccount: (accountId: string) =>
    `/security/service-accounts/${accountId}/update-service-account`,

  // DATA PAGE
  dataTables: '/data/tables',
  singleTable: '/data/tables/',
  createDataTable: '/data/new-table',
  createSummaryTable: '/data/new-summary-table',
  createSummaryTableColumnAnalysis: '/data/new-summary-table/column-analysis',
  editSummaryTableSettingsColumnAnalysis: (tableId: string) =>
    `/data/tables/${tableId}/edit-summary-settings/column-analysis`,
  editSummaryTableSettings: (tableId: string) => `/data/tables/${tableId}/edit-summary-settings`,
  createView: '/data/new-view',
  editView: (tableId: string, uuid: string | number) => `/data/tables/${tableId}/view/edit/${uuid}`,
  dataDictionaries: '/data/dictionaries',
  createDataDictionaries: '/data/dictionaries/new-data-dictionary',
  dataFunctions: '/data/functions',
  dataFiles: '/data/files',
  dataOrgSettings: '/data/organization-settings',
  createDataFile: '/data/files/new-file',
  createDataFunctions: '/data/functions/new-custom-function',
  createIngestSource: '/data/new-ingest-source',
  createTransform: '/data/new-transform',
  editSingleTable: (tableId: string) => `/data/tables/${tableId}`,
  editSingleTableColumnManagement: (tableId: string) => `/data/tables/${tableId}/column-management`,
  newSingleTableColumnAlias: (tableId: string) =>
    `/data/tables/${tableId}/column-management/new-column-alias`,
  newSingleTableColumnAliasAnalyze: (tableId: string) =>
    `/data/tables/${tableId}/column-management/analyze-expression`,
  editSingleTableColumnAlias: (tableId: string, columnId: number) =>
    `/data/tables/${tableId}/column-management/${columnId}`,
  editSingleTableColumnAliasAnalyze: (tableId: string, columnId: number) =>
    `/data/tables/${tableId}/column-management/${columnId}/analyze-expression`,
  editIngestSource: (tableId: string, type: string, uuid: string | number) =>
    `/data/tables/${tableId}/source/edit/${type}/${uuid}`,
  editTransform: (tableId: string, uuid: string | number) =>
    `/data/tables/${tableId}/transform/edit/${uuid}`,
  editFile: (projectId: string, name: string) => `/data/files/${projectId}/${name}/update-file`,
  validateTransform: '/data/validate-transform',
  editDictionary: (projectId: string, dictionaryId: string) =>
    `/data/dictionaries/${projectId}/${dictionaryId}/edit-dictionary`,
  editFunction: (projectId: string, functionId: string) =>
    `/data/functions/${projectId}/${functionId}/edit-function`,
  createTransformTemplate: '/data/new-transform-template',
  dataTransformTemplates: '/data/transform-templates',
  editTransformTemplate: (templateId: string) => `/data/transform-templates/${templateId}/edit`,
  projectHealth: (projectId: string) => `/data/project/${projectId}/health`,
  projectDelete: (projectId: string) => `/data/project/${projectId}/health/delete-project`,

  // SCALE PAGE
  scaleTables: '/scale',
  scaleSearchTable: '/scale/search',
  scaleCore: '/scale/core',
  scalePool: '/scale/pool/create',
  scalePoolEdit: (id: string) => `/scale/pool/${id}`,

  // JOBS
  alterNew: '/jobs/alter-jobs/create',
  batchNew: '/jobs/batch-jobs/create',
  alterTables: '/jobs/alter-jobs',
  batchTable: '/jobs/batch-jobs',

  // QUERY
  query: '/queries',
  queryReference: (selectedTableStore?: IFormTableListItem | null) =>
    selectedTableStore
      ? `/queries/reference/?table_id=${selectedTableStore?.table_id}&data=${selectedTableStore?.data}`
      : '/queries/reference',
  queryResult: '/result',
  queryStatistics: '/result',
  queryHierarchy: (selectedTableStore?: IFormTableListItem | null) =>
    selectedTableStore
      ? `/queries/hierarchy/?table_id=${selectedTableStore?.table_id}&data=${selectedTableStore?.data}`
      : '/queries/hierarchy',

  // SUPPORT
  support: '/support',

  // System Health
  systemHealthCounts: '/system-health/counts',
  systemHealthLogs: '/system-health/logs',
};