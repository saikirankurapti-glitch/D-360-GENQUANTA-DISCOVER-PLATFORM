import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Download, 
  ExternalLink, 
  ShieldAlert, 
  CheckCircle2, 
  BookMarked,
  ArrowRight,
  Cpu
} from 'lucide-react';

interface ComponentInfo {
  name: string;
  description: string;
}

interface ErrorInfo {
  error: string;
  solution: string;
}

interface ModuleData {
  id: number;
  name: string;
  category: string;
  purpose: string;
  business: string;
  scientific: string;
  navigation: string;
  screen_overview: string;
  components: ComponentInfo[];
  workflow: string[];
  expected: string;
  errors: ErrorInfo[];
  tips: string;
}

const docModules: ModuleData[] = [
  {
    id: 1,
    name: "Dashboard & Informatics Hub",
    category: "Onboarding & Core",
    purpose: "Provides the primary administrative and scientific launchpad of the AnalytiX platform. Renders real-time platform key performance indicators (KPIs), active computational pipeline statuses, recent project activity, and immediate database connector health feeds.",
    business: "Minimizes decision lag by providing operations and scientific managers a unified overview of all active drug discovery workloads, compute resource availability, and system throughput metrics.",
    scientific: "Integrates heterogeneous study telemetry (e.g., active target structure counts, compound registration velocities, alignment queue sizes) to help researchers immediately identify platform usage and pipeline blockages.",
    navigation: "Select 'Dashboard' from the left sidebar or navigate to '/dashboard'.",
    screen_overview: "Divided into three zones: a top-row KPI panel (4 metric cards), a middle section containing a split grid for 'Compute Pipeline Status' and 'System Feeds', and a right-hand quick shortcut sidebar.",
    components: [
      { name: "Platform Health Card", description: "A visual status indicator reporting backend connection status, server response times, and active database connection pool counts." },
      { name: "Active Pipelines Panel", description: "A live table reporting active screening runs, workflow executions, and bioinformatics alignment queues with status badges." },
      { name: "Active User Activity Feed", description: "A real-time list of system audit actions completed by researchers (e.g., compound registrations, queries run)." },
      { name: "Quick Navigation Cards", description: "A set of tiles linking to Compound Explorer, Visual Query Builder, and Bioinformatics Hub." }
    ],
    workflow: [
      "Log into the AnalytiX platform using your verified electronic credentials.",
      "Verify the 'Secure Session' indicator in the top header is green and active.",
      "Review the 'Platform Health Card' for active connector database configurations.",
      "Assess the running counts of compound libraries, active workflows, and sequence files in the KPI ribbon.",
      "Double-click on any active pipeline status card to drill down into the respective module detail page."
    ],
    expected: "Immediate rendering of active metrics, live connection status of backend databases, and high-fidelity navigation links.",
    errors: [
      { error: "Database Connectivity Latency", solution: "If a service is restarting, a yellow 'LATENCY' badge appears. Check connection parameters in the Settings tab." },
      { error: "API Handshake Failed", solution: "Red status badge. Verify VPN connections or consult your system administrator." }
    ],
    tips: "Utilize the Dashboard as an operational health check. Keep the browser window open to receive real-time, event-driven updates from the message broker."
  },
  {
    id: 2,
    name: "Data Registry",
    category: "Data Management",
    purpose: "Serves as the unified registration repository for all newly discovered or purchased chemical compounds, biological sequences, and assay structures. Enforces strict schema validations and uniqueness constraints before inserting records.",
    business: "Protects IP integrity and ensures a single version of truth for molecular and biological inventory, preventing costly assay duplicates.",
    scientific: "Ensures that SMILES and FASTA inputs are validated via cheminformatics/bioinformatics libraries (RDKit, BioPython) to prevent corrupted molecular structures from polluting database records.",
    navigation: "Click the 'Data Registry' pill button in the top header navigation panel or access the '/metadata' catalog and click 'Register Entity'.",
    screen_overview: "A multi-tab workspace with tabs for: 'Chemical Registration' (SMILES/MOL inputs), 'Sequence Registration' (FASTA formats), and 'Assay Data Loader' (CSV/Excel parsing).",
    components: [
      { name: "SMILES Text Field", description: "Input area for SMILES strings with real-time chemical valence and sanity checks." },
      { name: "Structure Canvas Previewer", description: "Renders molecular structural formulas on the fly using vector graphics (SVGs) dynamically compiled by RDKit." },
      { name: "FASTA File Drag-Drop Area", description: "Accepts uploads of raw FASTA files containing biological sequences with automatic sequence type detection (DNA, RNA, Protein)." },
      { name: "Register Button", description: "Triggers synchronous backend validation, audits, database insertion, and electronic signature prompts." }
    ],
    workflow: [
      "Navigate to the Data Registry via the header button.",
      "Select the 'Chemical Registration' tab.",
      "Paste the SMILES string 'CC(=O)NC1=CC=C(O)C=C1' (Acetaminophen) into the SMILES input field.",
      "Confirm the vector drawing matches the expected structural formula.",
      "Enter molecular metadata fields (e.g., Lot Number, Purity, Storage Condition).",
      "Click 'Register' and authenticate with your digital signature credentials."
    ],
    expected: "A notification popup indicating 'Entity Registered successfully' with a unique internal identifier (e.g., GQC-100204) and corresponding audit log entry.",
    errors: [
      { error: "Invalid SMILES Representation", solution: "RDKit parse failure. Verify chemical structure and format syntax." },
      { error: "Duplicate Compound Detected", solution: "An identical chemical structure is already present under another ID. The system highlights the existing ID link." }
    ],
    tips: "For high-throughput screening libraries, use the batch upload template (CSV format) under the 'Assay Data Loader' tab to register up to 10,000 compounds at once."
  },
  {
    id: 3,
    name: "Metadata Catalog",
    category: "Data Management",
    purpose: "A flexible, dynamic repository implemented via an Entity-Attribute-Value (EAV) database model that stores all properties, descriptors, annotations, and parameters for compounds, sequences, and assays without requiring hardcoded database migrations.",
    business: "Enables rapid extension of the database schema as new discovery methodologies and properties emerge, reducing IT overhead.",
    scientific: "Allows researchers to tag compounds with arbitrary custom attributes (e.g., custom IC50 limits, ADMET prediction metrics, gene expression scores) for subsequent visual filtering.",
    navigation: "Select 'Metadata Catalog' from the left-hand navigation sidebar (or navigate directly to '/metadata').",
    screen_overview: "Features an left-hand hierarchical taxonomy browser and a right-hand details table representing all active metadata definitions, datatypes, and validation constraints.",
    components: [
      { name: "Taxonomy Tree View", description: "Displays folders and tags representing metadata classes (e.g., ADMET, Physicochemical, Assay Results)." },
      { name: "Attribute Table List", description: "Shows defined attributes (e.g., mw, clogp, ic50_nm, smiles) with datatype badges (Float, String, Structure)." },
      { name: "New Attribute Dialog", description: "A modal window allowing administrators to add new metadata fields with custom bounds and validation regex." },
      { name: "Search Metadata Box", description: "Filters attributes by name, category, or description." }
    ],
    workflow: [
      "Access the Metadata Catalog from the sidebar.",
      "Search for the attribute 'clogp' using the Search box.",
      "Click on the 'clogp' row in the table to display validation limits, target ranges, and description fields.",
      "Click 'Edit Attribute' (requires Compliance Officer or Administrator role).",
      "Modify the minimum value constraint to -2.0 and maximum value to 9.0.",
      "Click 'Save Attributes' and review the change confirmation details."
    ],
    expected: "Immediate propagation of the modified metadata bounds, updated database validation schema, and audit history entry.",
    errors: [
      { error: "Schema Validation Mismatch", solution: "Occurs when trying to change a data type of an attribute that already has active values. Delete or migrate values first." },
      { error: "Permission Denied", solution: "Read-only access. Request Metadata administrator access permissions." }
    ],
    tips: "Always define clear physical units (e.g., nM, g/mol, angstroms) in the description of metadata attributes to ensure clarity during query operations."
  },
  {
    id: 4,
    name: "Connector Management",
    category: "Administration",
    purpose: "Manages physical connections, credentials, schema definitions, and synchronization tasks for external databases (Snowflake, PostgreSQL, Oracle, SQL Server, MongoDB) and scientific systems (Benchling, LabWare ELN, LIMS).",
    business: "Breaks down internal data silos by federating access to third-party databases, eliminating manual data export/import workflows.",
    scientific: "Enables live integration of raw screening data from active robotic liquid-handlers and sequencing machines straight into the research workbench.",
    navigation: "Click 'Data Connectors' in the left-hand sidebar menu, or navigate to '/connectors'.",
    screen_overview: "A dashboard displaying cards for each configured connector, connection status pills (Connected, Syncing, Offline), and buttons for initiating syncs or editing credentials.",
    components: [
      { name: "Connector Inventory Grid", description: "Cards containing connector name, type (e.g., Snowflake), last sync timestamp, and status badges." },
      { name: "New Connector Button", description: "Launches a step-by-step wizard for database/API settings (host, port, DB, username, credentials)." },
      { name: "Schema Discovery View", description: "Renders the external database schema, tables, columns, and keys mapped during metadata discovery." },
      { name: "Sync Scheduler panel", description: "Configures cron jobs for automated metadata sync runs." }
    ],
    workflow: [
      "Open the Connectors page from the sidebar.",
      "Click 'Add New Connector' (launches wizard).",
      "Choose 'PostgreSQL' from the connector types list.",
      "Enter connection parameters: Host 'localhost', Port '5432', Database 'assay_db', Username 'app_read'.",
      "Toggle 'Encrypted Credentials' to enabled, and enter Password.",
      "Click 'Test Connection' to verify network and credentials.",
      "Click 'Discover Schema' to map external tables.",
      "Click 'Save Connector'."
    ],
    expected: "A new connector card is added to the dashboard, displaying a green 'CONNECTED' status, and schema details become queryable in the metadata catalog.",
    errors: [
      { error: "Connection Timeout", solution: "Verify database port accessibility through local firewall rules and VPN tunnels." },
      { error: "Authentication Failure", solution: "Invalid password or database privileges. Request read access from database administrator." }
    ],
    tips: "Use dedicated, read-only database accounts for all connectors to minimize security risks and audit footprints."
  },
  {
    id: 5,
    name: "Compound Explorer",
    category: "Scientific Analytics",
    purpose: "A powerful chemical search and visualization dashboard designed to execute exact structures, substructures, and molecular similarity searches against millions of registered compounds using RDKit query engines.",
    business: "Shortens compound screening loops, helping chemists identify relevant chemical space and structural analogs within minutes.",
    scientific: "Allows researchers to execute structural searches with Tanimoto coefficient metrics and view structural overlays to identify pharmacophores.",
    navigation: "Click 'Compound Explorer' in the left sidebar or go to '/compounds'.",
    screen_overview: "Features an interactive JSME chemical structure drawer panel on the left, query configurations in the center, and a results grid showing structure cards on the right.",
    components: [
      { name: "JSME Chemical Structure Drawer", description: "Web-based chemical sketcher to draw molecules, export SMILES, or paste MOL files." },
      { name: "Search Mode Dropdown", description: "Selects between 'Exact Structure', 'Substructure', or 'Similarity (Tanimoto)'." },
      { name: "Similarity Threshold Slider", description: "Controls the Tanimoto similarity threshold percentage (range: 50% to 100%)." },
      { name: "Results Structure Grid", description: "Renders structural formulas of matching compounds with key descriptors (MW, LogP, PSA, HBD, HBA) and checkboxes for exporting." }
    ],
    workflow: [
      "Open Compound Explorer from the sidebar.",
      "In the JSME Structure Drawer, sketch a benzene ring and add an amide substituent.",
      "Select 'Substructure Search' from the dropdown.",
      "Click the 'Execute Search' button.",
      "Wait for results to render. Use the checkboxes to select molecules of interest.",
      "Click the 'Export to CSV' button to save results locally."
    ],
    expected: "Renders a paginated grid of all compounds containing the sketched amide-benzene pharmacophore, along with live calculated physicochemical values.",
    errors: [
      { error: "Empty Canvas Error", solution: "No structure drawn. Draw a chemical scaffold or paste a SMILES string before executing structure search." },
      { error: "RDKit Initialization Failure", solution: "WebAssembly file could not load. Reload the browser tab to restart the cheminformatics backend." }
    ],
    tips: "When executing similarity searches, a threshold of 80% is the industry standard for finding meaningful lead candidates while filtering out noise."
  },
  {
    id: 6,
    name: "Bioinformatics Explorer",
    category: "Scientific Analytics",
    purpose: "A comprehensive sequence analytics center designed to parse, align, cluster, and visualize biological sequences (DNA, RNA, proteins) using BioPython adapters and visual matrices.",
    business: "Reduces dependency on disconnected command-line bioinformatics utilities, facilitating sequence-structure correlations in a single platform.",
    scientific: "Allows biologists to identify motifs, run global/local sequence alignments (Needleman-Wunsch / Smith-Waterman), and build sequence similarity dendrograms.",
    navigation: "Click 'Bioinformatics Hub' in the left-hand navigation sidebar (or go to '/bioinformatics').",
    screen_overview: "A dashboard with cards linking to the 'Sequence Database', 'Sequence Alignment Studio', 'Sequence Clustering Center', and 'Sequence Explorer'.",
    components: [
      { name: "Sequence Import Field", description: "Input text box for pasting sequences in FASTA/Raw formats, or uploading sequence files (.fasta, .gb)." },
      { name: "Alignment Workspace Panel", description: "Displays color-coded aligned sequences with consensus markers and gap statistics." },
      { name: "Clustering Tree / Dendrogram", description: "Visualizes hierarchical clustering results using interactive Plotly tree maps and clusters." },
      { name: "Motif Search Input", description: "Searches sequences for specific conservation patterns (e.g., DNA primer sequences or protein binding pockets)." }
    ],
    workflow: [
      "Open the Bioinformatics Hub and click 'Sequence Alignment Studio'.",
      "Paste two FASTA protein sequences in the input field.",
      "Select 'Global (Needleman-Wunsch)' alignment algorithm.",
      "Set gap opening penalty to -10 and gap extension to -1.",
      "Click 'Perform Alignment'.",
      "View the alignment output matrix and review the sequence identity score."
    ],
    expected: "A side-by-side aligned sequence grid highlighting matching bases (green), substitutions (yellow), and insertions/deletions (red dashes).",
    errors: [
      { error: "Unsupported Sequence Type", solution: "Mixed sequence types (e.g. aligning protein with DNA). Ensure both sequences are of the same molecule type." },
      { error: "Fasta Format Error", solution: "Missing header starting with '>' character. Wrap the sequence with correct FASTA metadata." }
    ],
    tips: "Use local alignment for longer genomic sequences to identify small regions of high conservation without penalizing long mismatching ends."
  },
  {
    id: 7,
    name: "Query Builder",
    category: "Onboarding & Core",
    purpose: "Provides a visual query interface to query complex, federated databases across chemical structures, biological targets, metadata attributes, and assay metrics without requiring SQL knowledge.",
    business: "Empowers scientists to perform self-service data mining, reducing reliance on database administrators and data science queues.",
    scientific: "Combines structural constraints (e.g., substructure matching) with numerical descriptors (e.g., molecular weight) and assay targets (e.g., target proteins) in a single query matrix.",
    navigation: "Click 'Query Builder' in the sidebar or go to '/query-builder'.",
    screen_overview: "A node-based query workspace with block categories (Filters, Entities, joins) on the left, a central canvas to arrange query blocks, and a query SQL/JSON review panel on the bottom.",
    components: [
      { name: "Query Block Canvas", description: "A visual space where users drag and drop filter blocks (e.g., 'Molecular Weight < 500', 'IC50 < 10nM') and connect them with logical operators (AND, OR)." },
      { name: "Add Rule Dropdown", description: "Selects attributes from the Metadata Catalog to instantiate a new query block." },
      { name: "Query History Panel", description: "Accesses and loads queries run previously by the current researcher." },
      { name: "Execute Query Button", description: "Compiles the visual AST node graph to SQL, runs it against the federated engine, and redirects to the results table." }
    ],
    workflow: [
      "Navigate to the Visual Query Builder.",
      "Drag a new 'Rule Block' into the canvas.",
      "Select 'molecular_weight' from the attribute dropdown, choose operator '<', and input value '500'.",
      "Click 'Add Group' to introduce an AND condition block.",
      "Add another rule with 'clogp' operator '<' and value '5.0'.",
      "Click 'Run Query' in the bottom toolbar."
    ],
    expected: "Compilation of the query graph, database execution, and rendering of a table displaying matching compounds.",
    errors: [
      { error: "Orphaned Node Error", solution: "A logical block is unconnected on the canvas. Connect all query blocks with valid relational wires." },
      { error: "Query Timeout Error", solution: "The query was too complex or returned too many rows. Refine rules to restrict chemical or metadata ranges." }
    ],
    tips: "Save complex queries as Templates using the 'Save Template' button to share query configurations with other team members."
  },
  {
    id: 8,
    name: "Analytics Workbench",
    category: "Scientific Analytics",
    purpose: "A comprehensive scientific data science sandbox equipped to perform 4-Parameter Logistic (4PL) regression for dose-response curves, Principal Component Analysis (PCA), t-SNE clustering, K-Means clustering, and Pearson correlation matrices.",
    business: "Reduces licensing fees for third-party analysis packages by hosting advanced statistics directly on the server next to the data registry.",
    scientific: "Enables researchers to identify structural clusters in high-dimensional screening data and generate publication-ready plots directly from queries.",
    navigation: "Select 'Analytics Workbench' from the sidebar menu, or navigate to '/analytics-workbench'.",
    screen_overview: "A split layout featuring statistical parameter settings on the left (e.g., dimensions, clusters, fit algorithms) and interactive, high-fidelity Plotly charts on the right.",
    components: [
      { name: "Analysis Type Selector", description: "Dropdown to choose between 4PL Regression, PCA, t-SNE, K-Means, or Correlation Matrix." },
      { name: "Input Data Selector", description: "Allows selection of query results or registered assay tables as input datasets." },
      { name: "Interactive Plot Canvas", description: "Renders statistical charts (dose-response curves, scatter plots, Heatmaps) using Plotly with tooltips, zooming, and image export capabilities." },
      { name: "Export Plot Button", description: "Downloads high-resolution vector figures in PDF or PNG formats." }
    ],
    workflow: [
      "Open the Analytics Workbench.",
      "Select the 'Dose-Response (4PL)' tab.",
      "Choose 'Assay Data Series 12' as the input dataset.",
      "Map 'Concentration (uM)' to the X-axis and 'Inhibition (%)' to the Y-axis.",
      "Click 'Fit 4PL Model'.",
      "Review the calculated EC50/IC50 value and hill slope coefficient."
    ],
    expected: "A fitted Sigmoidal curve plotted over the concentration data points, with statistical metrics (R2, IC50) displayed in the summary card.",
    errors: [
      { error: "Insufficient Data Points", solution: "Fewer than 4 concentration points provided. 4PL models require at least 4 unique concentrations to fit." },
      { error: "Model Convergence Failure", solution: "Data is too noisy or lacks a sigmoidal shape. Check concentrations or select a linear fit." }
    ],
    tips: "Use PCA or t-SNE before clustering to reduce chemical descriptor dimensionality, allowing K-Means to identify more cohesive pharmacophore clusters."
  },
  {
    id: 9,
    name: "Workflow Automation Engine",
    category: "Onboarding & Core",
    purpose: "A node-based drag-and-drop designer and engine that automates scientific pipelines, orchestrating data retrieval, ADMET prediction, molecular docking, and electronic sign-off into standard operating procedures.",
    business: "Ensures process standardization and eliminates manual tasks, accelerating compound design cycles.",
    scientific: "Automates multi-stage workflows such as: taking query output -> running ADMET predictions -> filtering by Lipinski rules -> running molecular docking -> saving results to the database.",
    navigation: "Click 'Workflow Designer' in the left-hand sidebar menu, or navigate to '/workflows'.",
    screen_overview: "A large grid canvas where node blocks representing tasks (Database Query, RDKit, Docking, Approval, E-Signature) are connected by directional wires representing execution flow.",
    components: [
      { name: "Workflow Canvas", description: "The visual design area where execution pipelines are constructed and reviewed." },
      { name: "Node Toolbox", description: "A sidebar menu listing available scientific, logical, and database nodes." },
      { name: "Node Configurator Drawer", description: "Slide-out panel where properties of the selected node are configured." },
      { name: "Execute Pipeline Button", description: "Saves and initiates execution of the workflow definition, displaying live progress." }
    ],
    workflow: [
      "Open Workflow Designer.",
      "Drag a 'Database Query' node and a 'Lipinski Filter' node onto the canvas.",
      "Connect the output of the Query node to the input of the Filter node.",
      "Drag a 'Molecular Docking' node and connect the Filter output to it.",
      "Click the 'Database Query' node, open the configurator, and select the query template 'EGFR Candidates'.",
      "Click 'Run Workflow' and track the green execution path."
    ],
    expected: "A step-by-step progress tracking indicator, concluding with a run execution report showing results and a download link for docked structures.",
    errors: [
      { error: "Relational Type Mismatch", solution: "The output type of node A is incompatible with the input of node B. Verify data formats in the configurator." },
      { error: "Execution Timeout", solution: "Molecular docking took longer than the timeout threshold. Adjust docking parameters to reduce grid size." }
    ],
    tips: "Insert 'Approval / E-Signature' nodes before write operations to enforce regulatory compliance in automated workflows."
  },
  {
    id: 10,
    name: "Audit Trail & Compliance",
    category: "Compliance & Security",
    purpose: "Records all user actions, database mutations, configuration modifications, and signature approvals inside a secure ledger. Each log entry is cryptographically linked to the previous entry using SHA-256 hash chains, creating a tamper-evident audit history.",
    business: "Ensures legal defense and audit readiness for FDA reviews, protecting clinical submissions from disqualification.",
    scientific: "Enforces complete reproducibility of in silico experiments by tracing exactly who performed a computation, what parameters were used, and when it occurred.",
    navigation: "Click 'Audit Trail' in the sidebar or go to '/admin/audit'.",
    screen_overview: "Shows a table of historical system logs with filters for date range, user, action type, and status, and a prominent 'Verify Ledger Integrity' button.",
    components: [
      { name: "Audit Logs Table", description: "Lists timestamp, user email, action, module, IP address, and cryptographic block hash." },
      { name: "Ledger Integrity Panel", description: "Displays the result of the SHA-256 chain verification, reporting 'VALID' or warning of unauthorized modification." },
      { name: "Action Type Filter", description: "Dropdown to isolate specific auditable events (e.g., LOGIN, DATA_INSERT, DELETE, E_SIGN)." },
      { name: "Export Audit Log Button", description: "Generates a signed CSV or PDF report of the current log selection." }
    ],
    workflow: [
      "Navigate to the Audit Trail page.",
      "Filter actions by setting the 'Module' to 'Cheminformatics'.",
      "Select a specific log entry detailing a compound modification.",
      "Click the log entry to open the JSON detail payload showing 'Before' and 'After' states.",
      "Click 'Verify Ledger Integrity' to run the verification algorithm across the database table."
    ],
    expected: "Verification report showing 'All audit ledger blocks successfully validated. Hash chain is unbroken.' with green checkmarks.",
    errors: [
      { error: "Chain Integrity Warning", solution: "Red alert showing a hash mismatch. Indicates a database record was altered outside the platform interface. Contact security team." },
      { error: "Signature Verification Failure", solution: "Public keys do not match. Verify the user's compliance certificate." }
    ],
    tips: "Schedule weekly ledger integrity checks to automatically run and email reports to the Compliance Officer."
  },
  {
    id: 11,
    name: "FDA 21 CFR Part 11 Compliance",
    category: "Compliance & Security",
    purpose: "Enforces specific regulations for electronic records and signatures, including session timeouts, credential double-entry, password expiration policies, and restricted admin actions.",
    business: "Guarantees regulatory compliance for electronic records, enabling digital workflows to replace physical signatures.",
    scientific: "Validates the digital authenticity of calculations and target selections, ensuring results can be included in FDA Investigational New Drug (IND) applications.",
    navigation: "Access the 'Compliance Console' from the left sidebar and select the 'FDA Part 11' tab.",
    screen_overview: "A dashboard displaying compliance checklists, policy configuration controls, and validation settings.",
    components: [
      { name: "Session Timeout Field", description: "Configures inactivity duration (in minutes) before automatic session termination." },
      { name: "Double-Entry Toggle", description: "Enforces re-entering password for critical actions (e.g., compound approval, data export)." },
      { name: "Compliance Status Panel", description: "Real-time list of CFR Part 11 requirements showing green (Met) or red (Action required) markers." },
      { name: "Validation Report Builder", description: "Generates system validation logs for auditor inspection." }
    ],
    workflow: [
      "Open the Compliance Console and go to the 'FDA Part 11' tab.",
      "Enable 'Double-Factor E-Signatures' for all metadata schema changes.",
      "Set the 'Inactivity Session Timeout' to 15 minutes.",
      "Click 'Apply Compliance Settings'.",
      "Test the setting by attempting to export a query dataset; verify that a password confirmation dialog appears."
    ],
    expected: "Security configuration update, audited system event, and enforcement of security constraints across all user sessions.",
    errors: [
      { error: "Session Terminated", solution: "Session expired due to inactivity. Re-authenticate to resume work." },
      { error: "Verification Lockout", solution: "Too many incorrect password entries during electronic signing. Account is locked for 30 minutes." }
    ],
    tips: "Conduct monthly simulated compliance audits to verify that user permissions and activity logs meet FDA requirements."
  },
  {
    id: 12,
    name: "Electronic Signatures",
    category: "Compliance & Security",
    purpose: "A secure digital signing engine that prompts users to authenticate and select a reason (e.g., author, reviewer, approval) for critical actions, storing the signature in an immutable, audited ledger.",
    business: "Enables completely paperless approvals, saving days in lead candidate selection and workflow validations.",
    scientific: "Attaches a validated scientist signature to target validations, docking runs, and ADMET reports to confirm scientific peer review.",
    navigation: "Prompts automatically when signing off on workflows, registering molecules, or exporting compliance reports.",
    screen_overview: "A modal dialog overlay displaying the action details, signing reasons dropdown, password input field, and verification buttons.",
    components: [
      { name: "Signer Profile Details", description: "Displays the current user's name, email, and digital certificate details." },
      { name: "Signing Reason Dropdown", description: "A mandatory selection of standard reasons: 'Author', 'Reviewer', 'Approval', or 'Sponsor'." },
      { name: "Electronic Signature Password Field", description: "Enforces password re-entry to validate the signature identity." },
      { name: "Submit Signature Button", description: "Applies cryptographic signature and appends it to the target entity." }
    ],
    workflow: [
      "Initiate a critical action (e.g., click 'Approve Workflow' in the designer).",
      "Review the popup E-Signature modal.",
      "Select 'Approval' as the signing reason.",
      "Type your account password in the electronic password input field.",
      "Click 'Sign and Submit'.",
      "Verify the green 'Signature Applied' checkmark."
    ],
    expected: "Successful execution of the signature, creation of an audit log containing the digital certificate details, and completion of the target action.",
    errors: [
      { error: "Invalid Credentials", solution: "Password incorrect. Re-enter password. Note: 3 failures locks the digital signing capability." },
      { error: "Expired Certificate", solution: "User certificate is expired. Contact IT to renew your digital signing certificate." }
    ],
    tips: "Always check that your digital signature certificate is updated before entering critical IND validation phases."
  },
  {
    id: 13,
    name: "Data Lineage Explorer",
    category: "Compliance & Security",
    purpose: "Visualizes the life cycle and movement of data across the platform, mapping out how raw assay values and molecular files were transformed, query-filtered, and analyzed into final candidates.",
    business: "Allows teams to trace data discrepancies back to source systems, resolving data quality issues and avoiding wasted lab work.",
    scientific: "Guarantees reproducibility by mapping data flows from ELN imports to query engines, regression curves, and target structures.",
    navigation: "Open the 'Compliance Console' from the left sidebar and select the 'Data Lineage' tab.",
    screen_overview: "An interactive flowchart rendering node connections representing data objects (files, tables, queries, models) and edge arrows representing data operations (import, filter, fit, export).",
    components: [
      { name: "Lineage Canvas", description: "Interactive ReactFlow board where users pan, zoom, and select lineage nodes." },
      { name: "Node Inspector Panel", description: "Renders metadata for the selected node (e.g., date created, source system, execution parameters, owner)." },
      { name: "Drill-Down Button", description: "Opens the original service module that generated the data point (e.g., opens the specific query run)." },
      { name: "Source Trace Button", description: "Highlights the entire path of nodes back to the raw source data connector." }
    ],
    workflow: [
      "Open the Data Lineage Explorer.",
      "Select the target node 'Lead Candidate Assay Fit' on the canvas.",
      "Click 'Trace Source' in the inspector.",
      "Observe the highlighted upstream path showing: Raw SQL Database Connector -> Query Builder AST -> 4PL Model Input -> Final Curve Output.",
      "Double-click the 'Query Builder AST' node to inspect the original query rules."
    ],
    expected: "A visual flow diagram illustrating data history, and displaying transformation details in the sidebar panel.",
    errors: [
      { error: "Orphaned Node Reference", solution: "Occurs if an upstream raw data file was deleted from the server filesystem. The node appears yellow with a 'Missing Reference' warning." },
      { error: "Lineage Indexing Latency", solution: "New data runs might take up to a minute to index in the lineage database. Refresh the lineage canvas." }
    ],
    tips: "Export the lineage flowchart as an image and include it in IND filings to demonstrate raw data traceability."
  },
  {
    id: 14,
    name: "AI Scientist Copilot",
    category: "AI & Search",
    purpose: "An advanced natural language interface designed to interpret scientific questions, compile them to valid SQL or RDKit operations, query live databases, and return formatted tables, summaries, and structural charts.",
    business: "Accelerates data discovery and training times. Allows scientists to query complex informatics systems without writing queries or SQL.",
    scientific: "Leverages chemical and bioinformatics grounding rules to prevent model hallucinations, ensuring all answers represent actual database records.",
    navigation: "Click 'AI Scientist Copilot' in the sidebar or go to '/copilot'.",
    screen_overview: "A chat-style panel containing recent conversations, an input text area for entering questions, and a right-hand workspace displaying tables and RDKit structures generated by the AI.",
    components: [
      { name: "Chat Input Field", description: "A text area where scientists enter natural language queries (e.g. 'What compounds target EGFR?')." },
      { name: "Response Message Feed", description: "Displays the conversation log, detailing the AI's explanation, generated SQL, and citations." },
      { name: "Visual Results Panel", description: "Displays interactive data tables and molecular structure drawings resulting from the query." },
      { name: "Grounding Details Button", description: "Expands to show the validation checks performed on the SQL before execution." }
    ],
    workflow: [
      "Open the AI Scientist Copilot page.",
      "Type 'What compounds target EGFR?' in the input field.",
      "Click the 'Send' button or press Enter.",
      "Review the AI's explanation and inspect the generated SQL.",
      "Observe the resulting table of active compounds in the results panel.",
      "Ask a follow-up query: 'Filter this list for molecular weight less than 500'."
    ],
    expected: "A natural language summary, a table of compounds matching the target query, structural drawings, and an audit trail reference.",
    errors: [
      { error: "Hallucination Blocked", solution: "The AI generated SQL that failed structural verification. The query is automatically rejected, and a safe fallback query is executed." },
      { error: "Ambiguous Column Name", solution: "The query matches multiple columns in different tables. Clarify your question by specifying 'compound molecular weight' or 'assay values'." }
    ],
    tips: "Refer to the Prompts Library in the Copilot side panel for tips on structuring complex multi-table questions."
  },
  {
    id: 15,
    name: "Scientific Search",
    category: "AI & Search",
    purpose: "A unified search portal that integrates keyword indexing, semantic search, and chemical structure searches into a single query tool.",
    business: "Reduces time spent looking for documents, protocols, or compound records across multiple platforms.",
    scientific: "Combines text annotations (e.g., target names, PubMed references) with structural searches (SMILES) and sequence patterns.",
    navigation: "Accessible from the header search bar or by clicking the 'Search' icon in the left-hand navigation sidebar.",
    screen_overview: "A clean search page centered around a search box, with filtering options for Category (All, Compounds, Sequences, Assays, Workflows) and Source (LIMS, DB, ELN).",
    components: [
      { name: "Search Input Bar", description: "Presents a search box supporting keywords, SMILES, sequence motifs, and BOOLEAN search logic." },
      { name: "Facet Filter Panel", description: "Refines results by category, data source, date range, and owner." },
      { name: "Interactive Results List", description: "Displays matching records with preview snippets, chemical structures, and links to detail pages." },
      { name: "Export Search Results Button", description: "Exports search results to CSV or Excel formats." }
    ],
    workflow: [
      "Open Scientific Search.",
      "Enter the keyword 'EGFR' and click Search.",
      "Review the list of matching targets, compounds, and protocols.",
      "Select the 'Compounds' facet from the side panel to filter results.",
      "Double-click a compound card in the results to open its Compound Explorer page."
    ],
    expected: "Renders matching items across different modules, with direct navigation links to details pages.",
    errors: [
      { error: "Index Synchronization Lag", solution: "Newly added compounds may take up to 5 minutes to appear in keyword searches. Use direct search tools in the meantime." },
      { error: "Malformed Search Syntax", solution: "Incorrect Boolean syntax. Use quotes for exact phrases (e.g. 'EGFR assays') or separate terms with 'AND'." }
    ],
    tips: "Combine keywords with structure drawings to locate specific assay records for a particular chemical class."
  },
  {
    id: 16,
    name: "Project Management",
    category: "Data Management",
    purpose: "Organizes scientific studies, compounds, assays, and workflows into workspaces, facilitating collaboration within research teams.",
    business: "Protects sensitive research projects by restricting access to authorized project members.",
    scientific: "Maintains data organization across studies, linking targets to assays, compounds, and results to track progress.",
    navigation: "Accessible from the sidebar menu under the 'Projects' link.",
    screen_overview: "Displays active projects, recent updates, member lists, and study timelines.",
    components: [
      { name: "Project Grid Panel", description: "Cards showing project name, code (e.g., PROJ-EGFR-2026), status, and active member count." },
      { name: "Add Project Button", description: "Launches a dialog to create a project, set privacy levels, and invite team members." },
      { name: "Project Workspace Tabs", description: "Organizes project-specific resources: 'Compounds', 'Assays', 'Workflows', and 'Members'." },
      { name: "Timeline Chart", description: "Visualizes milestone deadlines and study durations." }
    ],
    workflow: [
      "Navigate to the Projects page.",
      "Click 'Create Project'.",
      "Enter the project name 'KRAS Inhibitor Lead Group'.",
      "Set the project visibility to 'Private - Invites Only'.",
      "Add team members and assign roles (e.g., Scientist, Admin).",
      "Click 'Save Project'."
    ],
    expected: "Creation of the project space, updated navigation sidebar, and automated invitations sent to team members.",
    errors: [
      { error: "Duplicate Project Code", solution: "Project code already exists. Enter a unique identifier for the study." },
      { error: "Insufficient User Rights", solution: "Only project administrators can modify project membership or settings." }
    ],
    tips: "Link all related queries and workflow runs to a project workspace to keep study data consolidated."
  },
  {
    id: 17,
    name: "User Administration",
    category: "Administration",
    purpose: "Provides user management capabilities, allowing administrators to invite users, activate/deactivate accounts, monitor active sessions, and assign system access levels.",
    business: "Maintains system security by ensuring only authorized personnel can access sensitive discovery data.",
    scientific: "Enforces regulatory compliance by ensuring user details are linked to electronic signatures and audit trails.",
    navigation: "Go to the Settings panel and select the 'User Admin' tab.",
    screen_overview: "A dashboard displaying the user directory, account status badges, and action buttons.",
    components: [
      { name: "User Directory Table", description: "Lists user name, email, role, status (Active, Suspended, Invited), and last login time." },
      { name: "Invite User Button", description: "Launches a modal to send email invitations and pre-assign roles." },
      { name: "Account Status Toggle", description: "Enables or disables accounts instantly." },
      { name: "Session Activity Monitor", description: "Displays active browser sessions with IP addresses and logout actions." }
    ],
    workflow: [
      "Open Settings and select the 'User Admin' tab.",
      "Click 'Invite User'.",
      "Enter the user's email: 'm.curie@analytix.com'.",
      "Select the 'Scientist' role from the dropdown.",
      "Click 'Send Invitation'."
    ],
    expected: "A notification confirming the invitation has been sent, and an entry added to the directory table with an 'Invited' status.",
    errors: [
      { error: "User Already Registered", solution: "Email address is already registered. Edit the existing user's profile to change their settings." },
      { error: "Domain Verification Failure", solution: "Email domain is not on the whitelist. Verify email address or contact security team." }
    ],
    tips: "Review the user directory monthly to deactivate inactive accounts and maintain license compliance."
  },
  {
    id: 18,
    name: "Role Based Access Control (RBAC)",
    category: "Administration",
    purpose: "Defines access control matrices that link roles (Admin, Scientist, Compliance Officer, Read-Only) to specific system permissions, ensuring users only access authorized modules.",
    business: "Prevents unauthorized data modification and protects IP, ensuring compliance with data security requirements.",
    scientific: "Prevents accidental modification of shared templates, assay records, and compliance logs by restricting access to authorized users.",
    navigation: "Go to the Settings panel and select the 'RBAC Control' tab.",
    screen_overview: "An interactive matrix mapping roles to system permissions, with custom role creation tools.",
    components: [
      { name: "RBAC Matrix Grid", description: "A grid where columns represent roles and rows represent system actions, with checkboxes to manage permissions." },
      { name: "Custom Role Creator", description: "Launches a panel to define a role name and select its permissions." },
      { name: "Policy Editor Panel", description: "Sets conditional access rules, such as login IP whitelists and access windows." },
      { name: "Save RBAC Map Button", description: "Saves the access control matrix and updates system permissions." }
    ],
    workflow: [
      "Open Settings and select the 'RBAC Control' tab.",
      "Locate the 'Scientist' role column in the matrix.",
      "Check the box for 'Metadata Schema Edit' to grant editing permissions.",
      "Uncheck the box for 'Audit Log Delete' to restrict deletion rights.",
      "Click 'Save RBAC Map' and enter your electronic signature password."
    ],
    expected: "An audit log entry documenting the permission change, and updated access rights applied to all affected accounts.",
    errors: [
      { error: "Permission Conflict", solution: "Invalid combination of permissions (e.g. read-only role with editing rights). Verify changes in the validator panel." },
      { error: "Cannot Demote Self", solution: "Administrators cannot revoke their own admin permissions. Have another admin perform the action." }
    ],
    tips: "Follow the principle of least privilege. Grant write permissions only when necessary for a user's role."
  },
  {
    id: 19,
    name: "Notifications & Alerts",
    category: "Administration",
    purpose: "A notification center that alerts users to workflow updates, data sync status, connection changes, and compliance reviews.",
    business: "Keeps project teams aligned on study progress, reducing delays in review and sign-off stages.",
    scientific: "Alerts researchers when docking simulations, ADMET calculations, or sequence alignments are complete.",
    navigation: "Accessible by clicking the 'Bell' icon in the top header, or going to the Settings page and selecting 'Alerts Config'.",
    screen_overview: "A list of recent notifications with category filters and configuration panels for email and Slack integrations.",
    components: [
      { name: "Notifications List", description: "A panel showing messages, source modules, and action links." },
      { name: "Integration Panel", description: "Configures webhook settings for Slack, Microsoft Teams, and email notifications." },
      { name: "Trigger Rules Table", description: "Lists notification rules, allowing users to select which events trigger alerts." },
      { name: "Mark All Read Button", description: "Clears all active notifications instantly." }
    ],
    workflow: [
      "Click the 'Bell' icon in the header.",
      "Select a notification showing 'Workflow Execution Complete' to view results.",
      "Go to settings to configure notifications.",
      "Toggle 'Email Alerts' to enabled for 'Compliance Verification Failures'.",
      "Click 'Save Notification Preferences'."
    ],
    expected: "Updated notification settings and confirmation that alerts will be delivered via the selected channels.",
    errors: [
      { error: "Delivery Failure", solution: "The email server or webhook returned an error. Verify notification settings in the Settings tab." },
      { error: "Notification Blocked", solution: "Browser notifications are blocked by user settings. Enable notifications in your browser settings." }
    ],
    tips: "Configure email digests for routine events to minimize inbox noise, while keeping real-time alerts enabled for critical compliance failures."
  },
  {
    id: 20,
    name: "Settings",
    category: "Administration",
    purpose: "The main settings panel containing configuration settings for user profiles, theme options, security preferences, database credentials, and network configurations.",
    business: "Enables administrators to configure the platform to meet organizational security and network requirements.",
    scientific: "Allows researchers to customize molecular drawing preferences, sequence alignment parameters, and search defaults.",
    navigation: "Select 'Settings' from the left sidebar or navigate to '/settings' (accessible via User Profile footer).",
    screen_overview: "A multi-section settings dashboard organized into: User Settings, Security & Auth, Connectors, and System Config.",
    components: [
      { name: "Password Policy Panel", description: "Sets password requirements, including minimum length, character types, and expiration rules." },
      { name: "SMTP Settings Form", description: "Configures email server details, including host, port, username, password, and encryption protocol." },
      { name: "Proxy Configuration Fields", description: "Sets proxy details for systems that require proxy access to external web services." },
      { name: "Database Maintenance Panel", description: "Allows administrators to run database optimization tasks, prune logs, and back up schemas." }
    ],
    workflow: [
      "Open Settings from the sidebar.",
      "Go to the 'Security & Auth' tab.",
      "Change password complexity requirement to 'Minimum 12 Characters'.",
      "Go to 'System Config' and enter SMTP server settings: SMTP Host 'smtp.analytix.com', Port '587'.",
      "Click 'Save Configurations' and enter your electronic signature password."
    ],
    expected: "Updated system settings and a confirmation message indicating configurations have been applied successfully.",
    errors: [
      { error: "Invalid SMTP Credentials", solution: "Connection to SMTP server failed. Verify hostname, port, and credentials." },
      { error: "Save Failed", solution: "Missing mandatory configuration values. Complete all required fields before saving." }
    ],
    tips: "Back up system configurations before making changes to settings or database connections."
  }
];

export const UserGuidePage: React.FC = () => {
  const [selectedModule, setSelectedModule] = useState<ModuleData>(docModules[0]);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filteredModules = useMemo(() => {
    if (!searchQuery.trim()) return docModules;
    const query = searchQuery.toLowerCase();
    return docModules.filter(
      (m) =>
        m.name.toLowerCase().includes(query) ||
        m.purpose.toLowerCase().includes(query) ||
        m.category.toLowerCase().includes(query)
    );
  }, [searchQuery]);

  const categories = ["Onboarding & Core", "Data Management", "Scientific Analytics", "Compliance & Security", "AI & Search", "Administration"];

  const handleDownload = (fileName: string) => {
    const link = document.createElement('a');
    link.href = `/docs/${fileName}`;
    link.download = fileName;
    link.click();
  };

  const handleOpenNewTab = (fileName: string) => {
    window.open(`/docs/${fileName}`, '_blank');
  };

  return (
    <div className="flex flex-1 h-[calc(100vh-4rem)] overflow-hidden bg-[#070b13] text-slate-100">
      {/* Sidebar Navigation */}
      <aside className="w-80 bg-[#0c1220] border-r border-[#1e293b] flex flex-col overflow-hidden select-none">
        {/* Search */}
        <div className="p-4 border-b border-[#1e293b] bg-[#090f1d]">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4.5 w-4.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search help articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#131b2e] border border-[#1e293b] rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500/50 focus:ring-1 focus:ring-sky-500/20 transition-all"
            />
          </div>
        </div>

        {/* Scrollable List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
          {categories.map(cat => {
            const catModules = filteredModules.filter(m => m.category === cat);
            if (catModules.length === 0) return null;

            return (
              <div key={cat} className="space-y-1">
                <h4 className="text-[10px] font-black uppercase tracking-wider text-slate-500 px-3 mb-1.5">{cat}</h4>
                <div className="space-y-0.5">
                  {catModules.map(m => {
                    const isSelected = selectedModule.id === m.id;
                    return (
                      <button
                        key={m.id}
                        onClick={() => setSelectedModule(m)}
                        className={`w-full text-left px-3 py-2 rounded-lg text-xs font-semibold flex items-center justify-between transition-all ${
                          isSelected
                            ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20 shadow-sm'
                            : 'text-slate-400 hover:bg-[#131b2e] hover:text-slate-200 border border-transparent'
                        }`}
                      >
                        <span className="truncate">{m.id}. {m.name}</span>
                        {isSelected && <ArrowRight className="h-3 w-3 shrink-0 ml-2" />}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}

          {filteredModules.length === 0 && (
            <div className="text-center py-8 text-slate-500 text-xs">
              No matching modules found.
            </div>
          )}
        </div>
      </aside>

      {/* Main Content Pane */}
      <main className="flex-1 flex flex-col overflow-hidden bg-[#080d17]">
        {/* Top toolbar */}
        <div className="h-16 px-8 border-b border-[#1e293b] flex items-center justify-between bg-[#0b111e] shrink-0 select-none">
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-400">Documentation</span>
            <span className="text-slate-600">/</span>
            <span className="text-slate-400 font-medium">{selectedModule.category}</span>
            <span className="text-slate-600">/</span>
            <span className="text-sky-400 font-bold">{selectedModule.name}</span>
          </div>

          <div className="flex items-center space-x-2">
            {/* Quick Actions */}
            <button
              onClick={() => handleOpenNewTab('AnalytiX_USER_MANUAL.pdf')}
              className="flex items-center space-x-1.5 bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/25 px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all shadow-sm"
              title="Open full User Manual PDF in a new tab"
            >
              <ExternalLink className="h-3.5 w-3.5" />
              <span>Open PDF</span>
            </button>
            <button
              onClick={() => handleDownload('AnalytiX_USER_MANUAL.pdf')}
              className="flex items-center space-x-1.5 bg-[#edf7f2] hover:bg-[#e1f0e7] text-[#0f766e] px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all shadow-sm border border-[#cedfd5]"
              title="Download Master User Manual PDF"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Download Manual</span>
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
          <div className="max-w-4xl mx-auto space-y-8">
            {/* Title & Badge */}
            <div className="space-y-3">
              <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-widest uppercase bg-sky-500/15 text-sky-400 border border-sky-500/30">
                {selectedModule.category}
              </div>
              <h1 className="text-3xl font-black tracking-tight text-white">{selectedModule.name}</h1>
              <p className="text-slate-350 text-sm leading-relaxed border-l-2 border-sky-500 pl-4 py-1 italic bg-sky-950/10">
                {selectedModule.purpose}
              </p>
            </div>

            {/* Business & Scientific Values */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-5 rounded-xl border border-emerald-500/10 bg-emerald-500/5 space-y-2">
                <div className="flex items-center space-x-2 text-emerald-450 font-bold text-xs uppercase tracking-wider">
                  <CheckCircle2 className="h-4 w-4" />
                  <span>Business Value</span>
                </div>
                <p className="text-slate-300 text-xs leading-relaxed">{selectedModule.business}</p>
              </div>

              <div className="p-5 rounded-xl border border-sky-500/10 bg-sky-500/5 space-y-2">
                <div className="flex items-center space-x-2 text-sky-400 font-bold text-xs uppercase tracking-wider">
                  <Cpu className="h-4 w-4" />
                  <span>Scientific Value</span>
                </div>
                <p className="text-slate-300 text-xs leading-relaxed">{selectedModule.scientific}</p>
              </div>
            </div>

            {/* Navigation & Layout */}
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2 border-b border-[#1e293b] pb-2">
                <BookMarked className="h-5 w-5 text-sky-400" />
                <span>Navigation & UI Layout</span>
              </h3>
              <div className="space-y-2 text-xs">
                <p className="text-slate-300"><span className="font-bold text-slate-200">Navigation: </span>{selectedModule.navigation}</p>
                <p className="text-slate-300"><span className="font-bold text-slate-200">Screen Overview: </span>{selectedModule.screen_overview}</p>
              </div>
            </div>

            {/* Component Reference Table */}
            <div className="space-y-3">
              <h3 className="text-sm font-black text-slate-400 uppercase tracking-wider">Interface Component Explanations</h3>
              <div className="border border-[#1e293b] rounded-xl overflow-hidden shadow-sm">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-[#0b111e] border-b border-[#1e293b] text-slate-300 font-bold">
                      <th className="px-4 py-3 w-1/3">UI Component</th>
                      <th className="px-4 py-3">Description & Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1e293b]">
                    {selectedModule.components.map((comp, idx) => (
                      <tr key={idx} className="hover:bg-[#0c1220] transition-colors">
                        <td className="px-4 py-3 font-bold text-slate-200">{comp.name}</td>
                        <td className="px-4 py-3 text-slate-400 leading-relaxed">{comp.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Step-by-Step Workflow */}
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2 border-b border-[#1e293b] pb-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-450" />
                <span>Step-by-Step Computational Workflow</span>
              </h3>
              <div className="space-y-3">
                {selectedModule.workflow.map((step, idx) => (
                  <div key={idx} className="flex items-start space-x-3.5">
                    <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-sky-500/10 text-sky-400 text-[10px] font-bold border border-sky-500/20">
                      {idx + 1}
                    </div>
                    <p className="text-xs text-slate-300 pt-0.5 leading-relaxed">{step}</p>
                  </div>
                ))}
              </div>
              <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1.5 mt-2">
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Expected Computational Output</span>
                <p className="text-xs text-emerald-400 font-semibold">{selectedModule.expected}</p>
              </div>
            </div>

            {/* Error Troubleshooting Reference */}
            <div className="space-y-3">
              <h3 className="text-sm font-black text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                <ShieldAlert className="h-4 w-4" />
                <span>Error Codes & Troubleshooting Reference</span>
              </h3>
              <div className="border border-rose-950/20 rounded-xl overflow-hidden shadow-sm">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-rose-950/15 border-b border-rose-950/20 text-rose-300 font-bold">
                      <th className="px-4 py-3 w-1/3">Error Scenario</th>
                      <th className="px-4 py-3">Resolution Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-rose-950/10">
                    {selectedModule.errors.map((err, idx) => (
                      <tr key={idx} className="hover:bg-rose-950/5 transition-colors">
                        <td className="px-4 py-3 font-bold text-rose-200">{err.error}</td>
                        <td className="px-4 py-3 text-slate-400 leading-relaxed">{err.solution}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Best Practices Alert Box */}
            <div className="p-5 rounded-xl border border-sky-500/10 bg-sky-950/15 space-y-2">
              <h4 className="text-xs font-bold text-sky-400 uppercase tracking-wider">Tips & Best Practices</h4>
              <p className="text-xs text-slate-350 leading-relaxed">{selectedModule.tips}</p>
            </div>

            {/* Downloads segment at page bottom */}
            <div className="pt-8 border-t border-[#1e293b] select-none">
              <h4 className="text-sm font-black text-slate-400 uppercase tracking-wider mb-4">Complete Documentation Suite PDFs</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                <button
                  onClick={() => handleOpenNewTab('AnalytiX_QUICK_START_GUIDE.pdf')}
                  className="flex items-center justify-between p-4 rounded-xl border border-[#1e293b] bg-[#0c1220] hover:bg-[#131b2e] text-left transition-all"
                >
                  <div className="space-y-1">
                    <span className="text-xs font-bold text-slate-200 block">Quick Start Guide</span>
                    <span className="text-[10px] text-slate-500 block">Workflow onboarding</span>
                  </div>
                  <Download className="h-4 w-4 text-slate-450 hover:text-slate-200" />
                </button>

                <button
                  onClick={() => handleOpenNewTab('AnalytiX_ADMIN_GUIDE.pdf')}
                  className="flex items-center justify-between p-4 rounded-xl border border-[#1e293b] bg-[#0c1220] hover:bg-[#131b2e] text-left transition-all"
                >
                  <div className="space-y-1">
                    <span className="text-xs font-bold text-slate-200 block">Admin Manual</span>
                    <span className="text-[10px] text-slate-500 block">RBAC & Connectors</span>
                  </div>
                  <Download className="h-4 w-4 text-slate-450 hover:text-slate-200" />
                </button>

                <button
                  onClick={() => handleOpenNewTab('AnalytiX_AI_COPILOT_GUIDE.pdf')}
                  className="flex items-center justify-between p-4 rounded-xl border border-[#1e293b] bg-[#0c1220] hover:bg-[#131b2e] text-left transition-all"
                >
                  <div className="space-y-1">
                    <span className="text-xs font-bold text-slate-200 block">AI Copilot Guide</span>
                    <span className="text-[10px] text-slate-500 block">Prompt engineering</span>
                  </div>
                  <Download className="h-4 w-4 text-slate-450 hover:text-slate-200" />
                </button>

                <button
                  onClick={() => handleOpenNewTab('AnalytiX_E2E_TEST_REPORT.pdf')}
                  className="flex items-center justify-between p-4 rounded-xl border border-[#1e293b] bg-[#0c1220] hover:bg-[#131b2e] text-left transition-all"
                >
                  <div className="space-y-1">
                    <span className="text-xs font-bold text-slate-200 block">E2E Test Report</span>
                    <span className="text-[10px] text-slate-500 block">Automated Verification</span>
                  </div>
                  <Download className="h-4 w-4 text-slate-450 hover:text-slate-200" />
                </button>
              </div>
            </div>

          </div>
        </div>
      </main>
    </div>
  );
};
