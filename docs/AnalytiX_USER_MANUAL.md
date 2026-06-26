# AnalytiX PLATFORM
## ENTERPRISE INFORMATICS & DISCOVERY PLATFORM USER MANUAL

### Document Suite v4.0.0
**Classification**: CONFIDENTIAL
**Regulatory Status**: FDA 21 CFR Part 11 Compliant Environment
**Last Updated**: June 2026

---

## 1. Introduction & Overview
The AnalytiX Platform is a state-of-the-art enterprise informatics and in silico drug discovery suite. It integrates advanced cheminformatics, bioinformatics, federated data queries, and AI-driven scientific assistance into a single unified platform. 

This document serves as the official operational manual and compliance reference for AnalytiX. It details all 20 active platform modules, illustrating their purpose, business value, scientific value, user interface layout, step-by-step workflows, expected results, common errors, troubleshooting, and best practices.

Designed for both research scientists and system administrators, this manual provides the instructions necessary to operate the platform in a validated FDA 21 CFR Part 11 compliant environment.

---

## 2. Platform Architecture Overview
The AnalytiX platform is built using a modern, scalable, microservice-based architecture designed for high availability and strict data isolation. It features nine custom PostgreSQL database schemas (`gen_auth`, `metadata`, `query`, `connector`, `audit`, `lineage`, `bio`, `workflow`, `ai`) managed by independent microservices. The services communicate asynchronously via a message broker and expose secure REST APIs to the React-based frontend dashboard. All transactions are logged to a cryptographically chained audit ledger to maintain data integrity.

---

## 3. User Roles & Permissions
Access to the AnalytiX platform is governed by Role-Based Access Control (RBAC) to ensure security and compliance with FDA 21 CFR Part 11 guidelines. The system defines three primary default roles:

1. **Administrator (Admin)**: Full control over system configurations, user administration, connector management, RBAC settings, and database maintenance.
2. **Scientist**: Full access to research modules, including Data Registry, Compound Explorer, Bioinformatics Hub, Query Builder, Analytics Workbench, Workflow Designer, and AI Scientist Copilot.
3. **Compliance Officer**: Special access to the Audit Trail, Compliance Console, electronic signature verification, and system validation reports.

---

## 4. Platform Modules Detail

### Module 1: Dashboard & Informatics Hub
#### Purpose
Provides the primary administrative and scientific launchpad of the AnalytiX platform. Renders real-time platform key performance indicators (KPIs), active computational pipeline statuses, recent project activity, and immediate database connector health feeds.

#### Business Value
Minimizes decision lag by providing operations and scientific managers a unified overview of all active drug discovery workloads, compute resource availability, and system throughput metrics.

#### Scientific Value
Integrates heterogeneous study telemetry (e.g., active target structure counts, compound registration velocities, alignment queue sizes) to help researchers immediately identify platform usage and pipeline blockages.

#### Navigation Instructions
Navigate to the dashboard by selecting the 'Dashboard' link from the sidebar menu (or accessing the '/' or '/dashboard' path).

#### Screen Overview
Divided into three zones: a top-row KPI panel (4 metric cards), a middle section containing a split grid for 'Compute Pipeline Status' and 'System Feeds', and a right-hand quick shortcut sidebar.

#### Component Explanations
- **Platform Health Card**: A visual status indicator reporting backend connection status, server response times, and active database connection pool counts.
- **Active Pipelines Panel**: A live table reporting active screening runs, workflow executions, and bioinformatics alignment queues with status badges.
- **Active User Activity Feed**: A real-time list of system audit actions completed by researchers (e.g., compound registrations, queries run).
- **Quick Navigation Cards**: A set of tiles linking to Compound Explorer, Visual Query Builder, and Bioinformatics Hub.

#### Step-by-Step Workflow Steps
1. Log into the AnalytiX platform using your verified electronic credentials.
1. Verify the 'Secure Session' indicator in the top header is green and active.
1. Review the 'Platform Health Card' for active connector database configurations.
1. Assess the running counts of compound libraries, active workflows, and sequence files in the KPI ribbon.
1. Double-click on any active pipeline status card to drill down into the respective module detail page.

#### Expected Results
Immediate rendering of active metrics, live connection status of backend databases, and high-fidelity navigation links.

#### Common Errors & Troubleshooting
- **Database Connectivity Latency**: If a service is restarting, a yellow 'LATENCY' badge appears. Check connection parameters in the Settings tab.
- **API Handshake Failed**: Red status badge. Verify VPN connections or consult your system administrator.

#### Tips & Best Practices
Utilize the Dashboard as an operational health check. Keep the browser window open to receive real-time, event-driven updates from the message broker.

---

### Module 2: Data Registry
#### Purpose
Serves as the unified registration repository for all newly discovered or purchased chemical compounds, biological sequences, and assay structures. Enforces strict schema validations and uniqueness constraints before inserting records.

#### Business Value
Protects IP integrity and ensures a single version of truth for molecular and biological inventory, preventing costly assay duplicates.

#### Scientific Value
Ensures that SMILES and FASTA inputs are validated via cheminformatics/bioinformatics libraries (RDKit, BioPython) to prevent corrupted molecular structures from polluting database records.

#### Navigation Instructions
Click the 'Data Registry' pill button in the top header navigation panel or access the '/metadata' catalog and click 'Register Entity'.

#### Screen Overview
A multi-tab workspace with tabs for: 'Chemical Registration' (SMILES/MOL inputs), 'Sequence Registration' (FASTA formats), and 'Assay Data Loader' (CSV/Excel parsing).

#### Component Explanations
- **SMILES Text Field**: Input area for SMILES strings with real-time chemical valence and sanity checks.
- **Structure Canvas Previewer**: Renders molecular structural formulas on the fly using vector graphics (SVGs) dynamically compiled by RDKit.
- **FASTA File Drag-Drop Area**: Accepts uploads of raw FASTA files containing biological sequences with automatic sequence type detection (DNA, RNA, Protein).
- **Register Button**: Triggers synchronous backend validation, audits, database insertion, and electronic signature prompts.

#### Step-by-Step Workflow Steps
1. Navigate to the Data Registry via the header button.
1. Select the 'Chemical Registration' tab.
1. Paste the SMILES string 'CC(=O)NC1=CC=C(O)C=C1' (Acetaminophen) into the SMILES input field.
1. Confirm the vector drawing matches the expected structural formula.
1. Enter molecular metadata fields (e.g., Lot Number, Purity, Storage Condition).
1. Click 'Register' and authenticate with your digital signature credentials.

#### Expected Results
A notification popup indicating 'Entity Registered successfully' with a unique internal identifier (e.g., GQC-100204) and corresponding audit log entry.

#### Common Errors & Troubleshooting
- **Invalid SMILES Representation**: RDKit parse failure. Verify chemical structure and format syntax.
- **Duplicate Compound Detected**: An identical chemical structure is already present under another ID. The system highlights the existing ID link.

#### Tips & Best Practices
For high-throughput screening libraries, use the batch upload template (CSV format) under the 'Assay Data Loader' tab to register up to 10,000 compounds at once.

---

### Module 3: Metadata Catalog
#### Purpose
A flexible, dynamic repository implemented via an Entity-Attribute-Value (EAV) database model that stores all properties, descriptors, annotations, and parameters for compounds, sequences, and assays without requiring hardcoded database migrations.

#### Business Value
Enables rapid extension of the database schema as new discovery methodologies and properties emerge, reducing IT overhead.

#### Scientific Value
Allows researchers to tag compounds with arbitrary custom attributes (e.g., custom IC50 limits, ADMET prediction metrics, gene expression scores) for subsequent visual filtering.

#### Navigation Instructions
Select 'Metadata Catalog' from the left-hand navigation sidebar (or navigate directly to '/metadata').

#### Screen Overview
Features an left-hand hierarchical taxonomy browser and a right-hand details table representing all active metadata definitions, datatypes, and validation constraints.

#### Component Explanations
- **Taxonomy Tree View**: Displays folders and tags representing metadata classes (e.g., ADMET, Physicochemical, Assay Results).
- **Attribute Table List**: Shows defined attributes (e.g., mw, clogp, ic50_nm, smiles) with datatype badges (Float, String, Structure).
- **New Attribute Dialog**: A modal window allowing administrators to add new metadata fields with custom bounds and validation regex.
- **Search Metadata Box**: Filters attributes by name, category, or description.

#### Step-by-Step Workflow Steps
1. Access the Metadata Catalog from the sidebar.
1. Search for the attribute 'clogp' using the Search box.
1. Click on the 'clogp' row in the table to display validation limits, target ranges, and description fields.
1. Click 'Edit Attribute' (requires Compliance Officer or Administrator role).
1. Modify the minimum value constraint to -2.0 and maximum value to 9.0.
1. Click 'Save Attributes' and review the change confirmation details.

#### Expected Results
Immediate propagation of the modified metadata bounds, updated database validation schema, and audit history entry.

#### Common Errors & Troubleshooting
- **Schema Validation Mismatch**: Occurs when trying to change a data type of an attribute that already has active values. Delete or migrate values first.
- **Permission Denied**: Read-only access. Request Metadata administrator access permissions.

#### Tips & Best Practices
Always define clear physical units (e.g., nM, g/mol, angstroms) in the description of metadata attributes to ensure clarity during query operations.

---

### Module 4: Connector Management
#### Purpose
Manages physical connections, credentials, schema definitions, and synchronization tasks for external databases (Snowflake, PostgreSQL, Oracle, SQL Server, MongoDB) and scientific systems (Benchling, LabWare ELN, LIMS).

#### Business Value
Breaks down internal data silos by federating access to third-party databases, eliminating manual data export/import workflows.

#### Scientific Value
Enables live integration of raw screening data from active robotic liquid-handlers and sequencing machines straight into the research workbench.

#### Navigation Instructions
Click 'Data Connectors' or 'Enterprise Integrations' in the left-hand sidebar menu, or navigate to '/connectors'.

#### Screen Overview
A dashboard displaying cards for each configured connector, connection status pills (Connected, Syncing, Offline), and buttons for initiating syncs or editing credentials.

#### Component Explanations
- **Connector Inventory Grid**: Cards containing connector name, type (e.g., Snowflake), last sync timestamp, and status badges.
- **New Connector Button**: Launches a step-by-step wizard for database/API settings (host, port, DB, username, credentials).
- **Schema Discovery View**: Renders the external database schema, tables, columns, and keys mapped during metadata discovery.
- **Sync Scheduler panel**: Configures cron jobs for automated metadata sync runs.

#### Step-by-Step Workflow Steps
1. Open the Connectors page from the sidebar.
1. Click 'Add New Connector' (launches wizard).
1. Choose 'PostgreSQL' from the connector types list.
1. Enter connection parameters: Host 'localhost', Port '5432', Database 'assay_db', Username 'app_read'.
1. Toggle 'Encrypted Credentials' to enabled, and enter Password.
1. Click 'Test Connection' to verify network and credentials.
1. Click 'Discover Schema' to map external tables.
1. Click 'Save Connector'.

#### Expected Results
A new connector card is added to the dashboard, displaying a green 'CONNECTED' status, and schema details become queryable in the metadata catalog.

#### Common Errors & Troubleshooting
- **Connection Timeout**: Verify database port accessibility through local firewall rules and VPN tunnels.
- **Authentication Failure**: Invalid password or database privileges. Request read access from database administrator.

#### Tips & Best Practices
Use dedicated, read-only database accounts for all connectors to minimize security risks and audit footprints.

---

### Module 5: Compound Explorer
#### Purpose
A powerful chemical search and visualization dashboard designed to execute exact structures, substructures, and molecular similarity searches against millions of registered compounds using RDKit query engines.

#### Business Value
Shortens compound screening loops, helping chemists identify relevant chemical space and structural analogs within minutes.

#### Scientific Value
Allows researchers to execute structural searches with Tanimoto coefficient metrics and view structural overlays to identify pharmacophores.

#### Navigation Instructions
Click 'Compound Explorer' in the left sidebar or go to '/compounds'.

#### Screen Overview
Features an interactive JSME chemical structure drawer panel on the left, query configurations in the center, and a results grid showing structure cards on the right.

#### Component Explanations
- **JSME Chemical Structure Drawer**: Web-based chemical sketcher to draw molecules, export SMILES, or paste MOL files.
- **Search Mode Dropdown**: Selects between 'Exact Structure', 'Substructure', or 'Similarity (Tanimoto)'.
- **Similarity Threshold Slider**: Controls the Tanimoto similarity threshold percentage (range: 50% to 100%).
- **Results Structure Grid**: Renders structural formulas of matching compounds with key descriptors (MW, LogP, PSA, HBD, HBA) and checkboxes for exporting.

#### Step-by-Step Workflow Steps
1. Open Compound Explorer from the sidebar.
1. In the JSME Structure Drawer, sketch a benzene ring and add an amide substituent.
1. Select 'Substructure Search' from the dropdown.
1. Click the 'Execute Search' button.
1. Wait for results to render. Use the checkboxes to select molecules of interest.
1. Click the 'Export to CSV' button to save results locally.

#### Expected Results
Renders a paginated grid of all compounds containing the sketched amide-benzene pharmacophore, along with live calculated physicochemical values.

#### Common Errors & Troubleshooting
- **Empty Canvas Error**: No structure drawn. Draw a chemical scaffold or paste a SMILES string before executing structure search.
- **RDKit Initialization Failure**: WebAssembly file could not load. Reload the browser tab to restart the cheminformatics backend.

#### Tips & Best Practices
When executing similarity searches, a threshold of 80% is the industry standard for finding meaningful lead candidates while filtering out noise.

---

### Module 6: Bioinformatics Explorer
#### Purpose
A comprehensive sequence analytics center designed to parse, align, cluster, and visualize biological sequences (DNA, RNA, proteins) using BioPython adapters and visual matrices.

#### Business Value
Reduces dependency on disconnected command-line bioinformatics utilities, facilitating sequence-structure correlations in a single platform.

#### Scientific Value
Allows biologists to identify motifs, run global/local sequence alignments (Needleman-Wunsch / Smith-Waterman), and build sequence similarity dendrograms.

#### Navigation Instructions
Click 'Bioinformatics Hub' in the left-hand navigation sidebar (or go to '/bioinformatics').

#### Screen Overview
A dashboard with cards linking to the 'Sequence Database', 'Sequence Alignment Studio', 'Sequence Clustering Center', and 'Sequence Explorer'.

#### Component Explanations
- **Sequence Import Field**: Input text box for pasting sequences in FASTA/Raw formats, or uploading sequence files (.fasta, .gb).
- **Alignment Workspace Panel**: Displays color-coded aligned sequences with consensus markers and gap statistics.
- **Clustering Tree / Dendrogram**: Visualizes hierarchical clustering results using interactive Plotly tree maps and clusters.
- **Motif Search Input**: Searches sequences for specific conservation patterns (e.g., DNA primer sequences or protein binding pockets).

#### Step-by-Step Workflow Steps
1. Open the Bioinformatics Hub and click 'Sequence Alignment Studio'.
1. Paste two FASTA protein sequences in the input field.
1. Select 'Global (Needleman-Wunsch)' alignment algorithm.
1. Set gap opening penalty to -10 and gap extension to -1.
1. Click 'Perform Alignment'.
1. View the alignment output matrix and review the sequence identity score.

#### Expected Results
A side-by-side aligned sequence grid highlighting matching bases (green), substitutions (yellow), and insertions/deletions (red dashes).

#### Common Errors & Troubleshooting
- **Unsupported Sequence Type**: Mixed sequence types (e.g. aligning protein with DNA). Ensure both sequences are of the same molecule type.
- **Fasta Format Error**: Missing header starting with '>' character. Wrap the sequence with correct FASTA metadata.

#### Tips & Best Practices
Use local alignment for longer genomic sequences to identify small regions of high conservation without penalizing long mismatching ends.

---

### Module 7: Query Builder
#### Purpose
Provides a visual query interface to query complex, federated databases across chemical structures, biological targets, metadata attributes, and assay metrics without requiring SQL knowledge.

#### Business Value
Empowers scientists to perform self-service data mining, reducing reliance on database administrators and data science queues.

#### Scientific Value
Combines structural constraints (e.g., substructure matching) with numerical descriptors (e.g., molecular weight) and assay targets (e.g., target proteins) in a single query matrix.

#### Navigation Instructions
Click 'Query Builder' or 'Visual Query Builder' in the sidebar or go to '/query-builder'.

#### Screen Overview
A node-based query workspace with block categories (Filters, Entities, joins) on the left, a central canvas to arrange query blocks, and a query SQL/JSON review panel on the bottom.

#### Component Explanations
- **Query Block Canvas**: A visual space where users drag and drop filter blocks (e.g., 'Molecular Weight < 500', 'IC50 < 10nM') and connect them with logical operators (AND, OR).
- **Add Rule Dropdown**: Selects attributes from the Metadata Catalog to instantiate a new query block.
- **Query History Panel**: Accesses and loads queries run previously by the current researcher.
- **Execute Query Button**: Compiles the visual AST node graph to SQL, runs it against the federated engine, and redirects to the results table.

#### Step-by-Step Workflow Steps
1. Navigate to the Visual Query Builder.
1. Drag a new 'Rule Block' into the canvas.
1. Select 'molecular_weight' from the attribute dropdown, choose operator '<', and input value '500'.
1. Click 'Add Group' to introduce an AND condition block.
1. Add another rule with 'clogp' operator '<' and value '5.0'.
1. Click 'Run Query' in the bottom toolbar.

#### Expected Results
Compilation of the query graph, database execution, and rendering of a table displaying matching compounds.

#### Common Errors & Troubleshooting
- **Orphaned Node Error**: A logical block is unconnected on the canvas. Connect all query blocks with valid relational wires.
- **Query Timeout Error**: The query was too complex or returned too many rows. Refine rules to restrict chemical or metadata ranges.

#### Tips & Best Practices
Save complex queries as Templates using the 'Save Template' button to share query configurations with other team members.

---

### Module 8: Analytics Workbench
#### Purpose
A comprehensive scientific data science sandbox equipped to perform 4-Parameter Logistic (4PL) regression for dose-response curves, Principal Component Analysis (PCA), t-SNE clustering, K-Means clustering, and Pearson correlation matrices.

#### Business Value
Reduces licensing fees for third-party analysis packages by hosting advanced statistics directly on the server next to the data registry.

#### Scientific Value
Enables researchers to identify structural clusters in high-dimensional screening data and generate publication-ready plots directly from queries.

#### Navigation Instructions
Select 'Analytics Workbench' from the sidebar menu, or navigate to '/analytics-workbench'.

#### Screen Overview
A split layout featuring statistical parameter settings on the left (e.g., dimensions, clusters, fit algorithms) and interactive, high-fidelity Plotly charts on the right.

#### Component Explanations
- **Analysis Type Selector**: Dropdown to choose between 4PL Regression, PCA, t-SNE, K-Means, or Correlation Matrix.
- **Input Data Selector**: Allows selection of query results or registered assay tables as input datasets.
- **Interactive Plot Canvas**: Renders statistical charts (dose-response curves, scatter plots, Heatmaps) using Plotly with tooltips, zooming, and image export capabilities.
- **Export Plot Button**: Downloads high-resolution vector figures in PDF or PNG formats.

#### Step-by-Step Workflow Steps
1. Open the Analytics Workbench.
1. Select the 'Dose-Response (4PL)' tab.
1. Choose 'Assay Data Series 12' as the input dataset.
1. Map 'Concentration (uM)' to the X-axis and 'Inhibition (%)' to the Y-axis.
1. Click 'Fit 4PL Model'.
1. Review the calculated EC50/IC50 value and hill slope coefficient.

#### Expected Results
A fitted Sigmoidal curve plotted over the concentration data points, with statistical metrics (R2, IC50) displayed in the summary card.

#### Common Errors & Troubleshooting
- **Insufficient Data Points**: Fewer than 4 concentration points provided. 4PL models require at least 4 unique concentrations to fit.
- **Model Convergence Failure**: Data is too noisy or lacks a sigmoidal shape. Check concentrations or select a linear fit.

#### Tips & Best Practices
Use PCA or t-SNE before clustering to reduce chemical descriptor dimensionality, allowing K-Means to identify more cohesive pharmacophore clusters.

---

### Module 9: Workflow Automation Engine
#### Purpose
A node-based drag-and-drop designer and engine that automates scientific pipelines, orchestrating data retrieval, ADMET prediction, molecular docking, and electronic sign-off into standard operating procedures.

#### Business Value
Ensures process standardization and eliminates manual tasks, accelerating compound design cycles.

#### Scientific Value
Automates multi-stage workflows such as: taking query output -> running ADMET predictions -> filtering by Lipinski rules -> running molecular docking -> saving results to the database.

#### Navigation Instructions
Click 'Workflow Designer' in the left-hand sidebar menu, or navigate to '/workflows'.

#### Screen Overview
A large grid canvas where node blocks representing tasks (Database Query, RDKit, Docking, Approval, E-Signature) are connected by directional wires representing execution flow.

#### Component Explanations
- **Workflow Canvas**: The visual design area where execution pipelines are constructed and reviewed.
- **Node Toolbox**: A sidebar menu listing available scientific, logical, and database nodes.
- **Node Configurator Drawer**: Slide-out panel where properties of the selected node are configured.
- **Execute Pipeline Button**: Saves and initiates execution of the workflow definition, displaying live progress.

#### Step-by-Step Workflow Steps
1. Open Workflow Designer.
1. Drag a 'Database Query' node and a 'Lipinski Filter' node onto the canvas.
1. Connect the output of the Query node to the input of the Filter node.
1. Drag a 'Molecular Docking' node and connect the Filter output to it.
1. Click the 'Database Query' node, open the configurator, and select the query template 'EGFR Candidates'.
1. Click 'Run Workflow' and track the green execution path.

#### Expected Results
A step-by-step progress tracking indicator, concluding with a run execution report showing results and a download link for docked structures.

#### Common Errors & Troubleshooting
- **Relational Type Mismatch**: The output type of node A is incompatible with the input of node B. Verify data formats in the configurator.
- **Execution Timeout**: Molecular docking took longer than the timeout threshold. Adjust docking parameters to reduce grid size.

#### Tips & Best Practices
Insert 'Approval / E-Signature' nodes before write operations to enforce regulatory compliance in automated workflows.

---

### Module 10: Audit Trail & Compliance
#### Purpose
Records all user actions, database mutations, configuration modifications, and signature approvals inside a secure ledger. Each log entry is cryptographically linked to the previous entry using SHA-256 hash chains, creating a tamper-evident audit history.

#### Business Value
Ensures legal defense and audit readiness for FDA reviews, protecting clinical submissions from disqualification.

#### Scientific Value
Enforces complete reproducibility of in silico experiments by tracing exactly who performed a computation, what parameters were used, and when it occurred.

#### Navigation Instructions
Click 'Audit Trail' in the sidebar or go to '/admin/audit'.

#### Screen Overview
Shows a table of historical system logs with filters for date range, user, action type, and status, and a prominent 'Verify Ledger Integrity' button.

#### Component Explanations
- **Audit Logs Table**: Lists timestamp, user email, action, module, IP address, and cryptographic block hash.
- **Ledger Integrity Panel**: Displays the result of the SHA-256 chain verification, reporting 'VALID' or warning of unauthorized modification.
- **Action Type Filter**: Dropdown to isolate specific auditable events (e.g., LOGIN, DATA_INSERT, DELETE, E_SIGN).
- **Export Audit Log Button**: Generates a signed CSV or PDF report of the current log selection.

#### Step-by-Step Workflow Steps
1. Navigate to the Audit Trail page.
1. Filter actions by setting the 'Module' to 'Cheminformatics'.
1. Select a specific log entry detailing a compound modification.
1. Click the log entry to open the JSON detail payload showing 'Before' and 'After' states.
1. Click 'Verify Ledger Integrity' to run the verification algorithm across the database table.

#### Expected Results
Verification report showing 'All audit ledger blocks successfully validated. Hash chain is unbroken.' with green checkmarks.

#### Common Errors & Troubleshooting
- **Chain Integrity Warning**: Red alert showing a hash mismatch. Indicates a database record was altered outside the platform interface. Contact security team.
- **Signature Verification Failure**: Public keys do not match. Verify the user's compliance certificate.

#### Tips & Best Practices
Schedule weekly ledger integrity checks to automatically run and email reports to the Compliance Officer.

---

### Module 11: FDA 21 CFR Part 11 Compliance
#### Purpose
Enforces specific regulations for electronic records and signatures, including session timeouts, credential double-entry, password expiration policies, and restricted admin actions.

#### Business Value
Guarantees regulatory compliance for electronic records, enabling digital workflows to replace physical signatures.

#### Scientific Value
Validates the digital authenticity of calculations and target selections, ensuring results can be included in FDA Investigational New Drug (IND) applications.

#### Navigation Instructions
Access the 'Compliance Console' from the left sidebar and select the 'FDA Part 11' tab.

#### Screen Overview
A dashboard displaying compliance checklists, policy configuration controls, and validation settings.

#### Component Explanations
- **Session Timeout Field**: Configures inactivity duration (in minutes) before automatic session termination.
- **Double-Entry Toggle**: Enforces re-entering password for critical actions (e.g., compound approval, data export).
- **Compliance Status Panel**: Real-time list of CFR Part 11 requirements showing green (Met) or red (Action required) markers.
- **Validation Report Builder**: Generates system validation logs for auditor inspection.

#### Step-by-Step Workflow Steps
1. Open the Compliance Console and go to the 'FDA Part 11' tab.
1. Enable 'Double-Factor E-Signatures' for all metadata schema changes.
1. Set the 'Inactivity Session Timeout' to 15 minutes.
1. Click 'Apply Compliance Settings'.
1. Test the setting by attempting to export a query dataset; verify that a password confirmation dialog appears.

#### Expected Results
Security configuration update, audited system event, and enforcement of security constraints across all user sessions.

#### Common Errors & Troubleshooting
- **Session Terminated**: Session expired due to inactivity. Re-authenticate to resume work.
- **Verification Lockout**: Too many incorrect password entries during electronic signing. Account is locked for 30 minutes.

#### Tips & Best Practices
Conduct monthly simulated compliance audits to verify that user permissions and activity logs meet FDA requirements.

---

### Module 12: Electronic Signatures
#### Purpose
A secure digital signing engine that prompts users to authenticate and select a reason (e.g., author, reviewer, approval) for critical actions, storing the signature in an immutable, audited ledger.

#### Business Value
Enables completely paperless approvals, saving days in lead candidate selection and workflow validations.

#### Scientific Value
Attaches a validated scientist signature to target validations, docking runs, and ADMET reports to confirm scientific peer review.

#### Navigation Instructions
Prompts automatically when signing off on workflows, registering molecules, or exporting compliance reports.

#### Screen Overview
A modal dialog overlay displaying the action details, signing reasons dropdown, password input field, and verification buttons.

#### Component Explanations
- **Signer Profile Details**: Displays the current user's name, email, and digital certificate details.
- **Signing Reason Dropdown**: A mandatory selection of standard reasons: 'Author', 'Reviewer', 'Approval', or 'Sponsor'.
- **Electronic Signature Password Field**: Enforces password re-entry to validate the signature identity.
- **Submit Signature Button**: Applies cryptographic signature and appends it to the target entity.

#### Step-by-Step Workflow Steps
1. Initiate a critical action (e.g., click 'Approve Workflow' in the designer).
1. Review the popup E-Signature modal.
1. Select 'Approval' as the signing reason.
1. Type your account password in the electronic password input field.
1. Click 'Sign and Submit'.
1. Verify the green 'Signature Applied' checkmark.

#### Expected Results
Successful execution of the signature, creation of an audit log containing the digital certificate details, and completion of the target action.

#### Common Errors & Troubleshooting
- **Invalid Credentials**: Password incorrect. Re-enter password. Note: 3 failures locks the digital signing capability.
- **Expired Certificate**: User certificate is expired. Contact IT to renew your digital signing certificate.

#### Tips & Best Practices
Always check that your digital signature certificate is updated before entering critical IND validation phases.

---

### Module 13: Data Lineage Explorer
#### Purpose
Visualizes the life cycle and movement of data across the platform, mapping out how raw assay values and molecular files were transformed, query-filtered, and analyzed into final candidates.

#### Business Value
Allows teams to trace data discrepancies back to source systems, resolving data quality issues and avoiding wasted lab work.

#### Scientific Value
Guarantees reproducibility by mapping data flows from ELN imports to query engines, regression curves, and target structures.

#### Navigation Instructions
Open the 'Compliance Console' from the left sidebar and select the 'Data Lineage' tab.

#### Screen Overview
An interactive flowchart rendering node connections representing data objects (files, tables, queries, models) and edge arrows representing data operations (import, filter, fit, export).

#### Component Explanations
- **Lineage Canvas**: Interactive ReactFlow board where users pan, zoom, and select lineage nodes.
- **Node Inspector Panel**: Renders metadata for the selected node (e.g., date created, source system, execution parameters, owner).
- **Drill-Down Button**: Opens the original service module that generated the data point (e.g., opens the specific query run).
- **Source Trace Button**: Highlights the entire path of nodes back to the raw source data connector.

#### Step-by-Step Workflow Steps
1. Open the Data Lineage Explorer.
1. Select the target node 'Lead Candidate Assay Fit' on the canvas.
1. Click 'Trace Source' in the inspector.
1. Observe the highlighted upstream path showing: Raw SQL Database Connector -> Query Builder AST -> 4PL Model Input -> Final Curve Output.
1. Double-click the 'Query Builder AST' node to inspect the original query rules.

#### Expected Results
A visual flow diagram illustrating data history, and displaying transformation details in the sidebar panel.

#### Common Errors & Troubleshooting
- **Orphaned Node Reference**: Occurs if an upstream raw data file was deleted from the server filesystem. The node appears yellow with a 'Missing Reference' warning.
- **Lineage Indexing Latency**: New data runs might take up to a minute to index in the lineage database. Refresh the lineage canvas.

#### Tips & Best Practices
Export the lineage flowchart as an image and include it in IND filings to demonstrate raw data traceability.

---

### Module 14: AI Scientist Copilot
#### Purpose
An advanced natural language interface designed to interpret scientific questions, compile them to valid SQL or RDKit operations, query live databases, and return formatted tables, summaries, and structural charts.

#### Business Value
Accelerates data discovery and training times. Allows scientists to query complex informatics systems without writing queries or SQL.

#### Scientific Value
Leverages chemical and bioinformatics grounding rules to prevent model hallucinations, ensuring all answers represent actual database records.

#### Navigation Instructions
Click 'AI Scientist Copilot' or 'Copilot' in the left-hand sidebar menu, or go to '/copilot'.

#### Screen Overview
A chat-style panel containing recent conversations, an input text area for entering questions, and a right-hand workspace displaying tables and RDKit structures generated by the AI.

#### Component Explanations
- **Chat Input Field**: A text area where scientists enter natural language queries (e.g. 'What compounds target EGFR?').
- **Response Message Feed**: Displays the conversation log, detailing the AI's explanation, generated SQL, and citations.
- **Visual Results Panel**: Displays interactive data tables and molecular structure drawings resulting from the query.
- **Grounding Details Button**: Expands to show the validation checks performed on the SQL before execution.

#### Step-by-Step Workflow Steps
1. Open the AI Scientist Copilot page.
1. Type 'What compounds target EGFR?' in the input field.
1. Click the 'Send' button or press Enter.
1. Review the AI's explanation and inspect the generated SQL.
1. Observe the resulting table of active compounds in the results panel.
1. Ask a follow-up query: 'Filter this list for molecular weight less than 500'.

#### Expected Results
A natural language summary, a table of compounds matching the target query, structural drawings, and an audit trail reference.

#### Common Errors & Troubleshooting
- **Hallucination Blocked**: The AI generated SQL that failed structural verification. The query is automatically rejected, and a safe fallback query is executed.
- **Ambiguous Column Name**: The query matches multiple columns in different tables. Clarify your question by specifying 'compound molecular weight' or 'assay values'.

#### Tips & Best Practices
Refer to the Prompts Library in the Copilot side panel for tips on structuring complex multi-table questions.

---

### Module 15: Scientific Search
#### Purpose
A unified search portal that integrates keyword indexing, semantic search, and chemical structure searches into a single query tool.

#### Business Value
Reduces time spent looking for documents, protocols, or compound records across multiple platforms.

#### Scientific Value
Combines text annotations (e.g., target names, PubMed references) with structural searches (SMILES) and sequence patterns.

#### Navigation Instructions
Accessible from the header search bar or by clicking the 'Search' icon in the left-hand navigation sidebar.

#### Screen Overview
A clean search page centered around a search box, with filtering options for Category (All, Compounds, Sequences, Assays, Workflows) and Source (LIMS, DB, ELN).

#### Component Explanations
- **Search Input Bar**: Presents a search box supporting keywords, SMILES, sequence motifs, and BOOLEAN search logic.
- **Facet Filter Panel**: Refines results by category, data source, date range, and owner.
- **Interactive Results List**: Displays matching records with preview snippets, chemical structures, and links to detail pages.
- **Export Search Results Button**: Exports search results to CSV or Excel formats.

#### Step-by-Step Workflow Steps
1. Open Scientific Search.
1. Enter the keyword 'EGFR' and click Search.
1. Review the list of matching targets, compounds, and protocols.
1. Select the 'Compounds' facet from the side panel to filter results.
1. Double-click a compound card in the results to open its Compound Explorer page.

#### Expected Results
Renders matching items across different modules, with direct navigation links to details pages.

#### Common Errors & Troubleshooting
- **Index Synchronization Lag**: Newly added compounds may take up to 5 minutes to appear in keyword searches. Use direct search tools in the meantime.
- **Malformed Search Syntax**: Incorrect Boolean syntax. Use quotes for exact phrases (e.g. 'EGFR assays') or separate terms with 'AND'.

#### Tips & Best Practices
Combine keywords with structure drawings to locate specific assay records for a particular chemical class.

---

### Module 16: Project Management
#### Purpose
Organizes scientific studies, compounds, assays, and workflows into workspaces, facilitating collaboration within research teams.

#### Business Value
Protects sensitive research projects by restricting access to authorized project members.

#### Scientific Value
Maintains data organization across studies, linking targets to assays, compounds, and results to track progress.

#### Navigation Instructions
Accessible from the sidebar menu under the 'Projects' link.

#### Screen Overview
Displays active projects, recent updates, member lists, and study timelines.

#### Component Explanations
- **Project Grid Panel**: Cards showing project name, code (e.g., PROJ-EGFR-2026), status, and active member count.
- **Add Project Button**: Launches a dialog to create a project, set privacy levels, and invite team members.
- **Project Workspace Tabs**: Organizes project-specific resources: 'Compounds', 'Assays', 'Workflows', and 'Members'.
- **Timeline Chart**: Visualizes milestone deadlines and study durations.

#### Step-by-Step Workflow Steps
1. Navigate to the Projects page.
1. Click 'Create Project'.
1. Enter the project name 'KRAS Inhibitor Lead Group'.
1. Set the project visibility to 'Private - Invites Only'.
1. Add team members and assign roles (e.g., Scientist, Admin).
1. Click 'Save Project'.

#### Expected Results
Creation of the project space, updated navigation sidebar, and automated invitations sent to team members.

#### Common Errors & Troubleshooting
- **Duplicate Project Code**: Project code already exists. Enter a unique identifier for the study.
- **Insufficient User Rights**: Only project administrators can modify project membership or settings.

#### Tips & Best Practices
Link all related queries and workflow runs to a project workspace to keep study data consolidated.

---

### Module 17: User Administration
#### Purpose
Provides user management capabilities, allowing administrators to invite users, activate/deactivate accounts, monitor active sessions, and assign system access levels.

#### Business Value
Maintains system security by ensuring only authorized personnel can access sensitive discovery data.

#### Scientific Value
Enforces regulatory compliance by ensuring user details are linked to electronic signatures and audit trails.

#### Navigation Instructions
Go to the Settings panel and select the 'User Admin' tab (requires Administrator role).

#### Screen Overview
A dashboard displaying the user directory, account status badges, and action buttons.

#### Component Explanations
- **User Directory Table**: Lists user name, email, role, status (Active, Suspended, Invited), and last login time.
- **Invite User Button**: Launches a modal to send email invitations and pre-assign roles.
- **Account Status Toggle**: Enables or disables accounts instantly.
- **Session Activity Monitor**: Displays active browser sessions with IP addresses and logout actions.

#### Step-by-Step Workflow Steps
1. Open Settings and select the 'User Admin' tab.
1. Click 'Invite User'.
1. Enter the user's email: 'm.curie@analytix.com'.
1. Select the 'Scientist' role from the dropdown.
1. Click 'Send Invitation'.

#### Expected Results
A notification confirming the invitation has been sent, and an entry added to the directory table with an 'Invited' status.

#### Common Errors & Troubleshooting
- **User Already Registered**: Email address is already registered. Edit the existing user's profile to change their settings.
- **Domain Verification Failure**: Email domain is not on the whitelist. Verify email address or contact security team.

#### Tips & Best Practices
Review the user directory monthly to deactivate inactive accounts and maintain license compliance.

---

### Module 18: Role Based Access Control (RBAC)
#### Purpose
Defines access control matrices that link roles (Admin, Scientist, Compliance Officer, Read-Only) to specific system permissions, ensuring users only access authorized modules.

#### Business Value
Prevents unauthorized data modification and protects IP, ensuring compliance with data security requirements.

#### Scientific Value
Prevents accidental modification of shared templates, assay records, and compliance logs by restricting access to authorized users.

#### Navigation Instructions
Go to the Settings panel and select the 'RBAC Control' tab (requires Administrator role).

#### Screen Overview
An interactive matrix mapping roles to system permissions, with custom role creation tools.

#### Component Explanations
- **RBAC Matrix Grid**: A grid where columns represent roles and rows represent system actions, with checkboxes to manage permissions.
- **Custom Role Creator**: Launches a panel to define a role name and select its permissions.
- **Policy Editor Panel**: Sets conditional access rules, such as login IP whitelists and access windows.
- **Save RBAC Map Button**: Saves the access control matrix and updates system permissions.

#### Step-by-Step Workflow Steps
1. Open Settings and select the 'RBAC Control' tab.
1. Locate the 'Scientist' role column in the matrix.
1. Check the box for 'Metadata Schema Edit' to grant editing permissions.
1. Uncheck the box for 'Audit Log Delete' to restrict deletion rights.
1. Click 'Save RBAC Map' and enter your electronic signature password.

#### Expected Results
An audit log entry documenting the permission change, and updated access rights applied to all affected accounts.

#### Common Errors & Troubleshooting
- **Permission Conflict**: Invalid combination of permissions (e.g. read-only role with editing rights). Verify changes in the validator panel.
- **Cannot Demote Self**: Administrators cannot revoke their own admin permissions. Have another admin perform the action.

#### Tips & Best Practices
Follow the principle of least privilege. Grant write permissions only when necessary for a user's role.

---

### Module 19: Notifications & Alerts
#### Purpose
A notification center that alerts users to workflow updates, data sync status, connection changes, and compliance reviews.

#### Business Value
Keeps project teams aligned on study progress, reducing delays in review and sign-off stages.

#### Scientific Value
Alerts researchers when docking simulations, ADMET calculations, or sequence alignments are complete.

#### Navigation Instructions
Accessible by clicking the 'Bell' icon in the top header, or going to the Settings page and selecting 'Alerts Config'.

#### Screen Overview
A list of recent notifications with category filters and configuration panels for email and Slack integrations.

#### Component Explanations
- **Notifications List**: A panel showing messages, source modules, and action links.
- **Integration Panel**: Configures webhook settings for Slack, Microsoft Teams, and email notifications.
- **Trigger Rules Table**: Lists notification rules, allowing users to select which events trigger alerts.
- **Mark All Read Button**: Clears all active notifications instantly.

#### Step-by-Step Workflow Steps
1. Click the 'Bell' icon in the header.
1. Select a notification showing 'Workflow Execution Complete' to view results.
1. Go to settings to configure notifications.
1. Toggle 'Email Alerts' to enabled for 'Compliance Verification Failures'.
1. Click 'Save Notification Preferences'.

#### Expected Results
Updated notification settings and confirmation that alerts will be delivered via the selected channels.

#### Common Errors & Troubleshooting
- **Delivery Failure**: The email server or webhook returned an error. Verify notification settings in the Settings tab.
- **Notification Blocked**: Browser notifications are blocked by user settings. Enable notifications in your browser settings.

#### Tips & Best Practices
Configure email digests for routine events to minimize inbox noise, while keeping real-time alerts enabled for critical compliance failures.

---

### Module 20: Settings
#### Purpose
The main settings panel containing configuration settings for user profiles, theme options, security preferences, database credentials, and network configurations.

#### Business Value
Enables administrators to configure the platform to meet organizational security and network requirements.

#### Scientific Value
Allows researchers to customize molecular drawing preferences, sequence alignment parameters, and search defaults.

#### Navigation Instructions
Select 'Settings' from the left sidebar or navigate to '/settings' (accessible via User Profile footer).

#### Screen Overview
A multi-section settings dashboard organized into: User Settings, Security & Auth, Connectors, and System Config.

#### Component Explanations
- **Password Policy Panel**: Sets password requirements, including minimum length, character types, and expiration rules.
- **SMTP Settings Form**: Configures email server details, including host, port, username, password, and encryption protocol.
- **Proxy Configuration Fields**: Sets proxy details for systems that require proxy access to external web services.
- **Database Maintenance Panel**: Allows administrators to run database optimization tasks, prune logs, and back up schemas.

#### Step-by-Step Workflow Steps
1. Open Settings from the sidebar.
1. Go to the 'Security & Auth' tab.
1. Change password complexity requirement to 'Minimum 12 Characters'.
1. Go to 'System Config' and enter SMTP server settings: SMTP Host 'smtp.analytix.com', Port '587'.
1. Click 'Save Configurations' and enter your electronic signature password.

#### Expected Results
Updated system settings and a confirmation message indicating configurations have been applied successfully.

#### Common Errors & Troubleshooting
- **Invalid SMTP Credentials**: Connection to SMTP server failed. Verify hostname, port, and credentials.
- **Save Failed**: Missing mandatory configuration values. Complete all required fields before saving.

#### Tips & Best Practices
Back up system configurations before making changes to settings or database connections.

---

## 5. AI Scientist Copilot Prompt Guide
The AI Scientist Copilot interprets natural language questions to query live databases using ground validation rules. Key prompt examples include:

1. *"What compounds target EGFR?"*
   - **Description**: Retrieves registered compounds and their activity status against the EGFR target protein.

2. *"Show compounds with MW < 500 and LogP < 5"*
   - **Description**: Filters compounds by physicochemical properties matching Lipinski's Rule of 5.

3. *"Summarize assay results"*
   - **Description**: Returns statistical summaries, compound counts, and active hits across recent assays.

4. *"Find compounds active against KRAS"*
   - **Description**: Performs a database query for compounds with active status or low IC50 values against KRAS.

5. *"Show workflow execution history"*
   - **Description**: Lists recent scientific workflow runs, execution status, and owner details.

---

## 6. Scientific Analytics Documentation
The platform provides statistics and metrics across multiple categories:
- **Dashboard KPIs**: System throughput, compound registration counts, active pipelines, and server response times.
- **Compound Analytics**: Physicochemical distribution, Tanimoto molecular similarity metrics, and R-group scaffold distributions.
- **Assay Analytics**: Sigmoidal curves, EC50/IC50 calculations, hill slopes, and assay performance metrics.
- **Bioinformatics Analytics**: Global/local alignment scores, sequence identity matrices, and hierarchical clustering dendrograms.
- **Workflow Analytics**: Workflow execution durations, node success rates, and parallel pipeline throughput.
- **Audit Analytics**: Log volume tracking, user action distributions, and compliance verification run statistics.
- **AI Usage Analytics**: Copilot query counts, SQL validation success rates, and user feedback distributions.

---

## 7. Compliance & FDA Validation
To maintain system integrity and comply with FDA regulations:
- **Audit Logs**: Cryptographically chained audit logs trace system activity.
- **Electronic Signatures**: Double-entry credentials require users to re-enter their passwords and select a reason for approvals.
- **Version Control**: Changes to workflows, queries, and metadata schema require version bumps.
- **Record Integrity**: SHA-256 hash chains verify that records are not altered outside the system.
- **Data Lineage**: Tracks files, data transformations, and queries back to source systems.
- **FDA 21 CFR Part 11**: Implements security controls, inactivity timeouts, and electronic signatures.

---

## 8. Troubleshooting FAQs
**Q: How do I resolve 'RDKit Parse Error' when registering a compound?**
*A: Ensure the SMILES string you entered has valid chemical valency and correct formatting. Use the JSME sketcher to draw the structure and automatically generate the SMILES string.*

**Q: Why can't I see the 'User Admin' or 'RBAC Control' tabs in Settings?**
*A: These tabs are restricted to users with the Administrator role. Contact your system administrator to request access if required.*

**Q: What should I do if the 'Ledger Integrity' check reports a warning?**
*A: Contact your Compliance Officer or security team immediately. A warning indicates that audit logs have been altered outside the platform interface.*

**Q: How do I download a workflow run execution report?**
*A: When a workflow run completes, click the 'Export Report' button in the execution drawer to download a PDF report containing the run logs and results.*

**Q: Why did my molecular docking workflow run time out?**
*A: Molecular docking tasks can be computationally intensive. Open the node configuration drawer and reduce the docking grid size or adjust execution parameters.*

---

## 9. Platform Glossary
- **SMILES**: Simplified Molecular-Input Line-Entry System. A line notation for describing the structure of chemical species using short ASCII strings.
- **FASTA**: A text-based format for representing either nucleotide sequences or peptide sequences, in which nucleotides or amino acids are represented using single-letter codes.
- **RDKit**: An open-source cheminformatics and machine learning software toolkit written in C++ and Python.
- **4PL Regression**: 4-Parameter Logistic regression. A mathematical model used to analyze sigmoidal dose-response curves in biological assays.
- **FDA 21 CFR Part 11**: Title 21 of the Code of Federal Regulations; Electronic Records; Electronic Signatures. Enforces requirements for closed and open systems to ensure record authenticity.
- **Tanimoto Coefficient**: A statistical metric used to quantify the similarity between two molecular fingerprints, ranging from 0.0 (completely different) to 1.0 (identical).
- **EAV Model**: Entity-Attribute-Value model. A database design pattern used to represent entity properties dynamically without modifying the database schema.
- **AST Graph**: Abstract Syntax Tree. A tree representation of the abstract syntactic structure of source code or visual queries.
- **SHA-256**: Secure Hash Algorithm 2. A cryptographic hash function that generates a unique 256-bit signature for data block verification.
- **IND**: Investational New Drug. An application filed with the FDA to obtain authorization for clinical testing of a new drug candidate.
