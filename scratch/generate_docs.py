import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Define output directories
DOCS_DIR = r"docs"
FRONTEND_DOCS_DIR = r"frontend\public\docs"

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(FRONTEND_DOCS_DIR, exist_ok=True)

# Custom NumberedCanvas for professional footers, headers, and dynamic page counts
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        # Skip for cover page
        if self._pageNumber == 1:
            return
        
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569")) # slate-600
        
        # Header
        self.drawString(54, 750, "AnalytiX Platform - Enterprise Documentation")
        self.setStrokeColor(colors.HexColor("#cbd5e1")) # slate-300
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer
        self.line(54, 45, 558, 45)
        self.drawString(54, 30, "CONFIDENTIAL - AnalytiX Biopharma Solutions")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 30, page_text)
        
        self.restoreState()

# Callback for first page (cover page) design
def draw_cover_background(canvas_obj, doc):
    canvas_obj.saveState()
    # Dark background banner (top half)
    canvas_obj.setFillColor(colors.HexColor("#0f766e")) # Deep teal
    canvas_obj.rect(0, 420, 612, 372, stroke=0, fill=1)
    
    # Bottom brand line
    canvas_obj.setStrokeColor(colors.HexColor("#0f766e"))
    canvas_obj.setLineWidth(4)
    canvas_obj.line(54, 110, 558, 110)
    
    canvas_obj.restoreState()

# Create standard stylesheet
def create_style_sheet():
    styles = getSampleStyleSheet()
    
    # Custom modifications or additions
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=colors.HexColor('#ffffff'),
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#99f6e4'), # Teal-200
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f766e'),
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#134e4a'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h3_style = ParagraphStyle(
        'SectionH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceBefore=4,
        spaceAfter=5
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceBefore=2,
        spaceAfter=2
    )
    
    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f1f5f9'),
        borderColor=colors.HexColor('#cbd5e1'),
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=6,
        spaceAfter=6
    )
    
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#0f766e'),
        backColor=colors.HexColor('#f0fdfa'),
        borderColor=colors.HexColor('#5eead4'),
        borderWidth=0.5,
        borderPadding=8,
        spaceBefore=6,
        spaceAfter=6
    )

    warning_style = ParagraphStyle(
        'WarningBox',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#b91c1c'),
        backColor=colors.HexColor('#fef2f2'),
        borderColor=colors.HexColor('#fca5a5'),
        borderWidth=0.5,
        borderPadding=8,
        spaceBefore=6,
        spaceAfter=6
    )
    
    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'h1': h1_style,
        'h2': h2_style,
        'h3': h3_style,
        'body': body_style,
        'bullet': bullet_style,
        'code': code_style,
        'callout': callout_style,
        'warning': warning_style
    }

def add_header_footer(canvas_obj, doc):
    pass  # Standard handling done in NumberedCanvas

# Setup details of all 20 modules
MODULES = [
    {
        "id": 1,
        "name": "Dashboard & Informatics Hub",
        "purpose": "Provides the primary administrative and scientific launchpad of the AnalytiX platform. Renders real-time platform key performance indicators (KPIs), active computational pipeline statuses, recent project activity, and immediate database connector health feeds.",
        "business": "Minimizes decision lag by providing operations and scientific managers a unified overview of all active drug discovery workloads, compute resource availability, and system throughput metrics.",
        "scientific": "Integrates heterogeneous study telemetry (e.g., active target structure counts, compound registration velocities, alignment queue sizes) to help researchers immediately identify platform usage and pipeline blockages.",
        "navigation": "Navigate to the dashboard by selecting the 'Dashboard' link from the sidebar menu (or accessing the '/' or '/dashboard' path).",
        "screen_overview": "Divided into three zones: a top-row KPI panel (4 metric cards), a middle section containing a split grid for 'Compute Pipeline Status' and 'System Feeds', and a right-hand quick shortcut sidebar.",
        "components": [
            ("Platform Health Card", "A visual status indicator reporting backend connection status, server response times, and active database connection pool counts."),
            ("Active Pipelines Panel", "A live table reporting active screening runs, workflow executions, and bioinformatics alignment queues with status badges."),
            ("Active User Activity Feed", "A real-time list of system audit actions completed by researchers (e.g., compound registrations, queries run)."),
            ("Quick Navigation Cards", "A set of tiles linking to Compound Explorer, Visual Query Builder, and Bioinformatics Hub.")
        ],
        "workflow": [
            "Log into the AnalytiX platform using your verified electronic credentials.",
            "Verify the 'Secure Session' indicator in the top header is green and active.",
            "Review the 'Platform Health Card' for active connector database configurations.",
            "Assess the running counts of compound libraries, active workflows, and sequence files in the KPI ribbon.",
            "Double-click on any active pipeline status card to drill down into the respective module detail page."
        ],
        "expected": "Immediate rendering of active metrics, live connection status of backend databases, and high-fidelity navigation links.",
        "errors": [
            ("Database Connectivity Latency", "If a service is restarting, a yellow 'LATENCY' badge appears. Check connection parameters in the Settings tab."),
            ("API Handshake Failed", "Red status badge. Verify VPN connections or consult your system administrator.")
        ],
        "tips": "Utilize the Dashboard as an operational health check. Keep the browser window open to receive real-time, event-driven updates from the message broker."
    },
    {
        "id": 2,
        "name": "Data Registry",
        "purpose": "Serves as the unified registration repository for all newly discovered or purchased chemical compounds, biological sequences, and assay structures. Enforces strict schema validations and uniqueness constraints before inserting records.",
        "business": "Protects IP integrity and ensures a single version of truth for molecular and biological inventory, preventing costly assay duplicates.",
        "scientific": "Ensures that SMILES and FASTA inputs are validated via cheminformatics/bioinformatics libraries (RDKit, BioPython) to prevent corrupted molecular structures from polluting database records.",
        "navigation": "Click the 'Data Registry' pill button in the top header navigation panel or access the '/metadata' catalog and click 'Register Entity'.",
        "screen_overview": "A multi-tab workspace with tabs for: 'Chemical Registration' (SMILES/MOL inputs), 'Sequence Registration' (FASTA formats), and 'Assay Data Loader' (CSV/Excel parsing).",
        "components": [
            ("SMILES Text Field", "Input area for SMILES strings with real-time chemical valence and sanity checks."),
            ("Structure Canvas Previewer", "Renders molecular structural formulas on the fly using vector graphics (SVGs) dynamically compiled by RDKit."),
            ("FASTA File Drag-Drop Area", "Accepts uploads of raw FASTA files containing biological sequences with automatic sequence type detection (DNA, RNA, Protein)."),
            ("Register Button", "Triggers synchronous backend validation, audits, database insertion, and electronic signature prompts.")
        ],
        "workflow": [
            "Navigate to the Data Registry via the header button.",
            "Select the 'Chemical Registration' tab.",
            "Paste the SMILES string 'CC(=O)NC1=CC=C(O)C=C1' (Acetaminophen) into the SMILES input field.",
            "Confirm the vector drawing matches the expected structural formula.",
            "Enter molecular metadata fields (e.g., Lot Number, Purity, Storage Condition).",
            "Click 'Register' and authenticate with your digital signature credentials."
        ],
        "expected": "A notification popup indicating 'Entity Registered successfully' with a unique internal identifier (e.g., GQC-100204) and corresponding audit log entry.",
        "errors": [
            ("Invalid SMILES Representation", "RDKit parse failure. Verify chemical structure and format syntax."),
            ("Duplicate Compound Detected", "An identical chemical structure is already present under another ID. The system highlights the existing ID link.")
        ],
        "tips": "For high-throughput screening libraries, use the batch upload template (CSV format) under the 'Assay Data Loader' tab to register up to 10,000 compounds at once."
    },
    {
        "id": 3,
        "name": "Metadata Catalog",
        "purpose": "A flexible, dynamic repository implemented via an Entity-Attribute-Value (EAV) database model that stores all properties, descriptors, annotations, and parameters for compounds, sequences, and assays without requiring hardcoded database migrations.",
        "business": "Enables rapid extension of the database schema as new discovery methodologies and properties emerge, reducing IT overhead.",
        "scientific": "Allows researchers to tag compounds with arbitrary custom attributes (e.g., custom IC50 limits, ADMET prediction metrics, gene expression scores) for subsequent visual filtering.",
        "navigation": "Select 'Metadata Catalog' from the left-hand navigation sidebar (or navigate directly to '/metadata').",
        "screen_overview": "Features an left-hand hierarchical taxonomy browser and a right-hand details table representing all active metadata definitions, datatypes, and validation constraints.",
        "components": [
            ("Taxonomy Tree View", "Displays folders and tags representing metadata classes (e.g., ADMET, Physicochemical, Assay Results)."),
            ("Attribute Table List", "Shows defined attributes (e.g., mw, clogp, ic50_nm, smiles) with datatype badges (Float, String, Structure)."),
            ("New Attribute Dialog", "A modal window allowing administrators to add new metadata fields with custom bounds and validation regex."),
            ("Search Metadata Box", "Filters attributes by name, category, or description.")
        ],
        "workflow": [
            "Access the Metadata Catalog from the sidebar.",
            "Search for the attribute 'clogp' using the Search box.",
            "Click on the 'clogp' row in the table to display validation limits, target ranges, and description fields.",
            "Click 'Edit Attribute' (requires Compliance Officer or Administrator role).",
            "Modify the minimum value constraint to -2.0 and maximum value to 9.0.",
            "Click 'Save Attributes' and review the change confirmation details."
        ],
        "expected": "Immediate propagation of the modified metadata bounds, updated database validation schema, and audit history entry.",
        "errors": [
            ("Schema Validation Mismatch", "Occurs when trying to change a data type of an attribute that already has active values. Delete or migrate values first."),
            ("Permission Denied", "Read-only access. Request Metadata administrator access permissions.")
        ],
        "tips": "Always define clear physical units (e.g., nM, g/mol, angstroms) in the description of metadata attributes to ensure clarity during query operations."
    },
    {
        "id": 4,
        "name": "Connector Management",
        "purpose": "Manages physical connections, credentials, schema definitions, and synchronization tasks for external databases (Snowflake, PostgreSQL, Oracle, SQL Server, MongoDB) and scientific systems (Benchling, LabWare ELN, LIMS).",
        "business": "Breaks down internal data silos by federating access to third-party databases, eliminating manual data export/import workflows.",
        "scientific": "Enables live integration of raw screening data from active robotic liquid-handlers and sequencing machines straight into the research workbench.",
        "navigation": "Click 'Data Connectors' or 'Enterprise Integrations' in the left-hand sidebar menu, or navigate to '/connectors'.",
        "screen_overview": "A dashboard displaying cards for each configured connector, connection status pills (Connected, Syncing, Offline), and buttons for initiating syncs or editing credentials.",
        "components": [
            ("Connector Inventory Grid", "Cards containing connector name, type (e.g., Snowflake), last sync timestamp, and status badges."),
            ("New Connector Button", "Launches a step-by-step wizard for database/API settings (host, port, DB, username, credentials)."),
            ("Schema Discovery View", "Renders the external database schema, tables, columns, and keys mapped during metadata discovery."),
            ("Sync Scheduler panel", "Configures cron jobs for automated metadata sync runs.")
        ],
        "workflow": [
            "Open the Connectors page from the sidebar.",
            "Click 'Add New Connector' (launches wizard).",
            "Choose 'PostgreSQL' from the connector types list.",
            "Enter connection parameters: Host 'localhost', Port '5432', Database 'assay_db', Username 'app_read'.",
            "Toggle 'Encrypted Credentials' to enabled, and enter Password.",
            "Click 'Test Connection' to verify network and credentials.",
            "Click 'Discover Schema' to map external tables.",
            "Click 'Save Connector'."
        ],
        "expected": "A new connector card is added to the dashboard, displaying a green 'CONNECTED' status, and schema details become queryable in the metadata catalog.",
        "errors": [
            ("Connection Timeout", "Verify database port accessibility through local firewall rules and VPN tunnels."),
            ("Authentication Failure", "Invalid password or database privileges. Request read access from database administrator.")
        ],
        "tips": "Use dedicated, read-only database accounts for all connectors to minimize security risks and audit footprints."
    },
    {
        "id": 5,
        "name": "Compound Explorer",
        "purpose": "A powerful chemical search and visualization dashboard designed to execute exact structures, substructures, and molecular similarity searches against millions of registered compounds using RDKit query engines.",
        "business": "Shortens compound screening loops, helping chemists identify relevant chemical space and structural analogs within minutes.",
        "scientific": "Allows researchers to execute structural searches with Tanimoto coefficient metrics and view structural overlays to identify pharmacophores.",
        "navigation": "Click 'Compound Explorer' in the left sidebar or go to '/compounds'.",
        "screen_overview": "Features an interactive JSME chemical structure drawer panel on the left, query configurations in the center, and a results grid showing structure cards on the right.",
        "components": [
            ("JSME Chemical Structure Drawer", "Web-based chemical sketcher to draw molecules, export SMILES, or paste MOL files."),
            ("Search Mode Dropdown", "Selects between 'Exact Structure', 'Substructure', or 'Similarity (Tanimoto)'."),
            ("Similarity Threshold Slider", "Controls the Tanimoto similarity threshold percentage (range: 50% to 100%)."),
            ("Results Structure Grid", "Renders structural formulas of matching compounds with key descriptors (MW, LogP, PSA, HBD, HBA) and checkboxes for exporting.")
        ],
        "workflow": [
            "Open Compound Explorer from the sidebar.",
            "In the JSME Structure Drawer, sketch a benzene ring and add an amide substituent.",
            "Select 'Substructure Search' from the dropdown.",
            "Click the 'Execute Search' button.",
            "Wait for results to render. Use the checkboxes to select molecules of interest.",
            "Click the 'Export to CSV' button to save results locally."
        ],
        "expected": "Renders a paginated grid of all compounds containing the sketched amide-benzene pharmacophore, along with live calculated physicochemical values.",
        "errors": [
            ("Empty Canvas Error", "No structure drawn. Draw a chemical scaffold or paste a SMILES string before executing structure search."),
            ("RDKit Initialization Failure", "WebAssembly file could not load. Reload the browser tab to restart the cheminformatics backend.")
        ],
        "tips": "When executing similarity searches, a threshold of 80% is the industry standard for finding meaningful lead candidates while filtering out noise."
    },
    {
        "id": 6,
        "name": "Bioinformatics Explorer",
        "purpose": "A comprehensive sequence analytics center designed to parse, align, cluster, and visualize biological sequences (DNA, RNA, proteins) using BioPython adapters and visual matrices.",
        "business": "Reduces dependency on disconnected command-line bioinformatics utilities, facilitating sequence-structure correlations in a single platform.",
        "scientific": "Allows biologists to identify motifs, run global/local sequence alignments (Needleman-Wunsch / Smith-Waterman), and build sequence similarity dendrograms.",
        "navigation": "Click 'Bioinformatics Hub' in the left-hand navigation sidebar (or go to '/bioinformatics').",
        "screen_overview": "A dashboard with cards linking to the 'Sequence Database', 'Sequence Alignment Studio', 'Sequence Clustering Center', and 'Sequence Explorer'.",
        "components": [
            ("Sequence Import Field", "Input text box for pasting sequences in FASTA/Raw formats, or uploading sequence files (.fasta, .gb)."),
            ("Alignment Workspace Panel", "Displays color-coded aligned sequences with consensus markers and gap statistics."),
            ("Clustering Tree / Dendrogram", "Visualizes hierarchical clustering results using interactive Plotly tree maps and clusters."),
            ("Motif Search Input", "Searches sequences for specific conservation patterns (e.g., DNA primer sequences or protein binding pockets).")
        ],
        "workflow": [
            "Open the Bioinformatics Hub and click 'Sequence Alignment Studio'.",
            "Paste two FASTA protein sequences in the input field.",
            "Select 'Global (Needleman-Wunsch)' alignment algorithm.",
            "Set gap opening penalty to -10 and gap extension to -1.",
            "Click 'Perform Alignment'.",
            "View the alignment output matrix and review the sequence identity score."
        ],
        "expected": "A side-by-side aligned sequence grid highlighting matching bases (green), substitutions (yellow), and insertions/deletions (red dashes).",
        "errors": [
            ("Unsupported Sequence Type", "Mixed sequence types (e.g. aligning protein with DNA). Ensure both sequences are of the same molecule type."),
            ("Fasta Format Error", "Missing header starting with '>' character. Wrap the sequence with correct FASTA metadata.")
        ],
        "tips": "Use local alignment for longer genomic sequences to identify small regions of high conservation without penalizing long mismatching ends."
    },
    {
        "id": 7,
        "name": "Query Builder",
        "purpose": "Provides a visual query interface to query complex, federated databases across chemical structures, biological targets, metadata attributes, and assay metrics without requiring SQL knowledge.",
        "business": "Empowers scientists to perform self-service data mining, reducing reliance on database administrators and data science queues.",
        "scientific": "Combines structural constraints (e.g., substructure matching) with numerical descriptors (e.g., molecular weight) and assay targets (e.g., target proteins) in a single query matrix.",
        "navigation": "Click 'Query Builder' or 'Visual Query Builder' in the sidebar or go to '/query-builder'.",
        "screen_overview": "A node-based query workspace with block categories (Filters, Entities, joins) on the left, a central canvas to arrange query blocks, and a query SQL/JSON review panel on the bottom.",
        "components": [
            ("Query Block Canvas", "A visual space where users drag and drop filter blocks (e.g., 'Molecular Weight < 500', 'IC50 < 10nM') and connect them with logical operators (AND, OR)."),
            ("Add Rule Dropdown", "Selects attributes from the Metadata Catalog to instantiate a new query block."),
            ("Query History Panel", "Accesses and loads queries run previously by the current researcher."),
            ("Execute Query Button", "Compiles the visual AST node graph to SQL, runs it against the federated engine, and redirects to the results table.")
        ],
        "workflow": [
            "Navigate to the Visual Query Builder.",
            "Drag a new 'Rule Block' into the canvas.",
            "Select 'molecular_weight' from the attribute dropdown, choose operator '<', and input value '500'.",
            "Click 'Add Group' to introduce an AND condition block.",
            "Add another rule with 'clogp' operator '<' and value '5.0'.",
            "Click 'Run Query' in the bottom toolbar."
        ],
        "expected": "Compilation of the query graph, database execution, and rendering of a table displaying matching compounds.",
        "errors": [
            ("Orphaned Node Error", "A logical block is unconnected on the canvas. Connect all query blocks with valid relational wires."),
            ("Query Timeout Error", "The query was too complex or returned too many rows. Refine rules to restrict chemical or metadata ranges.")
        ],
        "tips": "Save complex queries as Templates using the 'Save Template' button to share query configurations with other team members."
    },
    {
        "id": 8,
        "name": "Analytics Workbench",
        "purpose": "A comprehensive scientific data science sandbox equipped to perform 4-Parameter Logistic (4PL) regression for dose-response curves, Principal Component Analysis (PCA), t-SNE clustering, K-Means clustering, and Pearson correlation matrices.",
        "business": "Reduces licensing fees for third-party analysis packages by hosting advanced statistics directly on the server next to the data registry.",
        "scientific": "Enables researchers to identify structural clusters in high-dimensional screening data and generate publication-ready plots directly from queries.",
        "navigation": "Select 'Analytics Workbench' from the sidebar menu, or navigate to '/analytics-workbench'.",
        "screen_overview": "A split layout featuring statistical parameter settings on the left (e.g., dimensions, clusters, fit algorithms) and interactive, high-fidelity Plotly charts on the right.",
        "components": [
            ("Analysis Type Selector", "Dropdown to choose between 4PL Regression, PCA, t-SNE, K-Means, or Correlation Matrix."),
            ("Input Data Selector", "Allows selection of query results or registered assay tables as input datasets."),
            ("Interactive Plot Canvas", "Renders statistical charts (dose-response curves, scatter plots, Heatmaps) using Plotly with tooltips, zooming, and image export capabilities."),
            ("Export Plot Button", "Downloads high-resolution vector figures in PDF or PNG formats.")
        ],
        "workflow": [
            "Open the Analytics Workbench.",
            "Select the 'Dose-Response (4PL)' tab.",
            "Choose 'Assay Data Series 12' as the input dataset.",
            "Map 'Concentration (uM)' to the X-axis and 'Inhibition (%)' to the Y-axis.",
            "Click 'Fit 4PL Model'.",
            "Review the calculated EC50/IC50 value and hill slope coefficient."
        ],
        "expected": "A fitted Sigmoidal curve plotted over the concentration data points, with statistical metrics (R2, IC50) displayed in the summary card.",
        "errors": [
            ("Insufficient Data Points", "Fewer than 4 concentration points provided. 4PL models require at least 4 unique concentrations to fit."),
            ("Model Convergence Failure", "Data is too noisy or lacks a sigmoidal shape. Check concentrations or select a linear fit.")
        ],
        "tips": "Use PCA or t-SNE before clustering to reduce chemical descriptor dimensionality, allowing K-Means to identify more cohesive pharmacophore clusters."
    },
    {
        "id": 9,
        "name": "Workflow Automation Engine",
        "purpose": "A node-based drag-and-drop designer and engine that automates scientific pipelines, orchestrating data retrieval, ADMET prediction, molecular docking, and electronic sign-off into standard operating procedures.",
        "business": "Ensures process standardization and eliminates manual tasks, accelerating compound design cycles.",
        "scientific": "Automates multi-stage workflows such as: taking query output -> running ADMET predictions -> filtering by Lipinski rules -> running molecular docking -> saving results to the database.",
        "navigation": "Click 'Workflow Designer' in the left-hand sidebar menu, or navigate to '/workflows'.",
        "screen_overview": "A large grid canvas where node blocks representing tasks (Database Query, RDKit, Docking, Approval, E-Signature) are connected by directional wires representing execution flow.",
        "components": [
            ("Workflow Canvas", "The visual design area where execution pipelines are constructed and reviewed."),
            ("Node Toolbox", "A sidebar menu listing available scientific, logical, and database nodes."),
            ("Node Configurator Drawer", "Slide-out panel where properties of the selected node are configured."),
            ("Execute Pipeline Button", "Saves and initiates execution of the workflow definition, displaying live progress.")
        ],
        "workflow": [
            "Open Workflow Designer.",
            "Drag a 'Database Query' node and a 'Lipinski Filter' node onto the canvas.",
            "Connect the output of the Query node to the input of the Filter node.",
            "Drag a 'Molecular Docking' node and connect the Filter output to it.",
            "Click the 'Database Query' node, open the configurator, and select the query template 'EGFR Candidates'.",
            "Click 'Run Workflow' and track the green execution path."
        ],
        "expected": "A step-by-step progress tracking indicator, concluding with a run execution report showing results and a download link for docked structures.",
        "errors": [
            ("Relational Type Mismatch", "The output type of node A is incompatible with the input of node B. Verify data formats in the configurator."),
            ("Execution Timeout", "Molecular docking took longer than the timeout threshold. Adjust docking parameters to reduce grid size.")
        ],
        "tips": "Insert 'Approval / E-Signature' nodes before write operations to enforce regulatory compliance in automated workflows."
    },
    {
        "id": 10,
        "name": "Audit Trail & Compliance",
        "purpose": "Records all user actions, database mutations, configuration modifications, and signature approvals inside a secure ledger. Each log entry is cryptographically linked to the previous entry using SHA-256 hash chains, creating a tamper-evident audit history.",
        "business": "Ensures legal defense and audit readiness for FDA reviews, protecting clinical submissions from disqualification.",
        "scientific": "Enforces complete reproducibility of in silico experiments by tracing exactly who performed a computation, what parameters were used, and when it occurred.",
        "navigation": "Click 'Audit Trail' in the sidebar or go to '/admin/audit'.",
        "screen_overview": "Shows a table of historical system logs with filters for date range, user, action type, and status, and a prominent 'Verify Ledger Integrity' button.",
        "components": [
            ("Audit Logs Table", "Lists timestamp, user email, action, module, IP address, and cryptographic block hash."),
            ("Ledger Integrity Panel", "Displays the result of the SHA-256 chain verification, reporting 'VALID' or warning of unauthorized modification."),
            ("Action Type Filter", "Dropdown to isolate specific auditable events (e.g., LOGIN, DATA_INSERT, DELETE, E_SIGN)."),
            ("Export Audit Log Button", "Generates a signed CSV or PDF report of the current log selection.")
        ],
        "workflow": [
            "Navigate to the Audit Trail page.",
            "Filter actions by setting the 'Module' to 'Cheminformatics'.",
            "Select a specific log entry detailing a compound modification.",
            "Click the log entry to open the JSON detail payload showing 'Before' and 'After' states.",
            "Click 'Verify Ledger Integrity' to run the verification algorithm across the database table."
        ],
        "expected": "Verification report showing 'All audit ledger blocks successfully validated. Hash chain is unbroken.' with green checkmarks.",
        "errors": [
            ("Chain Integrity Warning", "Red alert showing a hash mismatch. Indicates a database record was altered outside the platform interface. Contact security team."),
            ("Signature Verification Failure", "Public keys do not match. Verify the user's compliance certificate.")
        ],
        "tips": "Schedule weekly ledger integrity checks to automatically run and email reports to the Compliance Officer."
    },
    {
        "id": 11,
        "name": "FDA 21 CFR Part 11 Compliance",
        "purpose": "Enforces specific regulations for electronic records and signatures, including session timeouts, credential double-entry, password expiration policies, and restricted admin actions.",
        "business": "Guarantees regulatory compliance for electronic records, enabling digital workflows to replace physical signatures.",
        "scientific": "Validates the digital authenticity of calculations and target selections, ensuring results can be included in FDA Investigational New Drug (IND) applications.",
        "navigation": "Access the 'Compliance Console' from the left sidebar and select the 'FDA Part 11' tab.",
        "screen_overview": "A dashboard displaying compliance checklists, policy configuration controls, and validation settings.",
        "components": [
            ("Session Timeout Field", "Configures inactivity duration (in minutes) before automatic session termination."),
            ("Double-Entry Toggle", "Enforces re-entering password for critical actions (e.g., compound approval, data export)."),
            ("Compliance Status Panel", "Real-time list of CFR Part 11 requirements showing green (Met) or red (Action required) markers."),
            ("Validation Report Builder", "Generates system validation logs for auditor inspection.")
        ],
        "workflow": [
            "Open the Compliance Console and go to the 'FDA Part 11' tab.",
            "Enable 'Double-Factor E-Signatures' for all metadata schema changes.",
            "Set the 'Inactivity Session Timeout' to 15 minutes.",
            "Click 'Apply Compliance Settings'.",
            "Test the setting by attempting to export a query dataset; verify that a password confirmation dialog appears."
        ],
        "expected": "Security configuration update, audited system event, and enforcement of security constraints across all user sessions.",
        "errors": [
            ("Session Terminated", "Session expired due to inactivity. Re-authenticate to resume work."),
            ("Verification Lockout", "Too many incorrect password entries during electronic signing. Account is locked for 30 minutes.")
        ],
        "tips": "Conduct monthly simulated compliance audits to verify that user permissions and activity logs meet FDA requirements."
    },
    {
        "id": 12,
        "name": "Electronic Signatures",
        "purpose": "A secure digital signing engine that prompts users to authenticate and select a reason (e.g., author, reviewer, approval) for critical actions, storing the signature in an immutable, audited ledger.",
        "business": "Enables completely paperless approvals, saving days in lead candidate selection and workflow validations.",
        "scientific": "Attaches a validated scientist signature to target validations, docking runs, and ADMET reports to confirm scientific peer review.",
        "navigation": "Prompts automatically when signing off on workflows, registering molecules, or exporting compliance reports.",
        "screen_overview": "A modal dialog overlay displaying the action details, signing reasons dropdown, password input field, and verification buttons.",
        "components": [
            ("Signer Profile Details", "Displays the current user's name, email, and digital certificate details."),
            ("Signing Reason Dropdown", "A mandatory selection of standard reasons: 'Author', 'Reviewer', 'Approval', or 'Sponsor'."),
            ("Electronic Signature Password Field", "Enforces password re-entry to validate the signature identity."),
            ("Submit Signature Button", "Applies cryptographic signature and appends it to the target entity.")
        ],
        "workflow": [
            "Initiate a critical action (e.g., click 'Approve Workflow' in the designer).",
            "Review the popup E-Signature modal.",
            "Select 'Approval' as the signing reason.",
            "Type your account password in the electronic password input field.",
            "Click 'Sign and Submit'.",
            "Verify the green 'Signature Applied' checkmark."
        ],
        "expected": "Successful execution of the signature, creation of an audit log containing the digital certificate details, and completion of the target action.",
        "errors": [
            ("Invalid Credentials", "Password incorrect. Re-enter password. Note: 3 failures locks the digital signing capability."),
            ("Expired Certificate", "User certificate is expired. Contact IT to renew your digital signing certificate.")
        ],
        "tips": "Always check that your digital signature certificate is updated before entering critical IND validation phases."
    },
    {
        "id": 13,
        "name": "Data Lineage Explorer",
        "purpose": "Visualizes the life cycle and movement of data across the platform, mapping out how raw assay values and molecular files were transformed, query-filtered, and analyzed into final candidates.",
        "business": "Allows teams to trace data discrepancies back to source systems, resolving data quality issues and avoiding wasted lab work.",
        "scientific": "Guarantees reproducibility by mapping data flows from ELN imports to query engines, regression curves, and target structures.",
        "navigation": "Open the 'Compliance Console' from the left sidebar and select the 'Data Lineage' tab.",
        "screen_overview": "An interactive flowchart rendering node connections representing data objects (files, tables, queries, models) and edge arrows representing data operations (import, filter, fit, export).",
        "components": [
            ("Lineage Canvas", "Interactive ReactFlow board where users pan, zoom, and select lineage nodes."),
            ("Node Inspector Panel", "Renders metadata for the selected node (e.g., date created, source system, execution parameters, owner)."),
            ("Drill-Down Button", "Opens the original service module that generated the data point (e.g., opens the specific query run)."),
            ("Source Trace Button", "Highlights the entire path of nodes back to the raw source data connector.")
        ],
        "workflow": [
            "Open the Data Lineage Explorer.",
            "Select the target node 'Lead Candidate Assay Fit' on the canvas.",
            "Click 'Trace Source' in the inspector.",
            "Observe the highlighted upstream path showing: Raw SQL Database Connector -> Query Builder AST -> 4PL Model Input -> Final Curve Output.",
            "Double-click the 'Query Builder AST' node to inspect the original query rules."
        ],
        "expected": "A visual flow diagram illustrating data history, and displaying transformation details in the sidebar panel.",
        "errors": [
            ("Orphaned Node Reference", "Occurs if an upstream raw data file was deleted from the server filesystem. The node appears yellow with a 'Missing Reference' warning."),
            ("Lineage Indexing Latency", "New data runs might take up to a minute to index in the lineage database. Refresh the lineage canvas.")
        ],
        "tips": "Export the lineage flowchart as an image and include it in IND filings to demonstrate raw data traceability."
    },
    {
        "id": 14,
        "name": "AI Scientist Copilot",
        "purpose": "An advanced natural language interface designed to interpret scientific questions, compile them to valid SQL or RDKit operations, query live databases, and return formatted tables, summaries, and structural charts.",
        "business": "Accelerates data discovery and training times. Allows scientists to query complex informatics systems without writing queries or SQL.",
        "scientific": "Leverages chemical and bioinformatics grounding rules to prevent model hallucinations, ensuring all answers represent actual database records.",
        "navigation": "Click 'AI Scientist Copilot' or 'Copilot' in the left-hand sidebar menu, or go to '/copilot'.",
        "screen_overview": "A chat-style panel containing recent conversations, an input text area for entering questions, and a right-hand workspace displaying tables and RDKit structures generated by the AI.",
        "components": [
            ("Chat Input Field", "A text area where scientists enter natural language queries (e.g. 'What compounds target EGFR?')."),
            ("Response Message Feed", "Displays the conversation log, detailing the AI's explanation, generated SQL, and citations."),
            ("Visual Results Panel", "Displays interactive data tables and molecular structure drawings resulting from the query."),
            ("Grounding Details Button", "Expands to show the validation checks performed on the SQL before execution.")
        ],
        "workflow": [
            "Open the AI Scientist Copilot page.",
            "Type 'What compounds target EGFR?' in the input field.",
            "Click the 'Send' button or press Enter.",
            "Review the AI's explanation and inspect the generated SQL.",
            "Observe the resulting table of active compounds in the results panel.",
            "Ask a follow-up query: 'Filter this list for molecular weight less than 500'."
        ],
        "expected": "A natural language summary, a table of compounds matching the target query, structural drawings, and an audit trail reference.",
        "errors": [
            ("Hallucination Blocked", "The AI generated SQL that failed structural verification. The query is automatically rejected, and a safe fallback query is executed."),
            ("Ambiguous Column Name", "The query matches multiple columns in different tables. Clarify your question by specifying 'compound molecular weight' or 'assay values'.")
        ],
        "tips": "Refer to the Prompts Library in the Copilot side panel for tips on structuring complex multi-table questions."
    },
    {
        "id": 15,
        "name": "Scientific Search",
        "purpose": "A unified search portal that integrates keyword indexing, semantic search, and chemical structure searches into a single query tool.",
        "business": "Reduces time spent looking for documents, protocols, or compound records across multiple platforms.",
        "scientific": "Combines text annotations (e.g., target names, PubMed references) with structural searches (SMILES) and sequence patterns.",
        "navigation": "Accessible from the header search bar or by clicking the 'Search' icon in the left-hand navigation sidebar.",
        "screen_overview": "A clean search page centered around a search box, with filtering options for Category (All, Compounds, Sequences, Assays, Workflows) and Source (LIMS, DB, ELN).",
        "components": [
            ("Search Input Bar", "Presents a search box supporting keywords, SMILES, sequence motifs, and BOOLEAN search logic."),
            ("Facet Filter Panel", "Refines results by category, data source, date range, and owner."),
            ("Interactive Results List", "Displays matching records with preview snippets, chemical structures, and links to detail pages."),
            ("Export Search Results Button", "Exports search results to CSV or Excel formats.")
        ],
        "workflow": [
            "Open Scientific Search.",
            "Enter the keyword 'EGFR' and click Search.",
            "Review the list of matching targets, compounds, and protocols.",
            "Select the 'Compounds' facet from the side panel to filter results.",
            "Double-click a compound card in the results to open its Compound Explorer page."
        ],
        "expected": "Renders matching items across different modules, with direct navigation links to details pages.",
        "errors": [
            ("Index Synchronization Lag", "Newly added compounds may take up to 5 minutes to appear in keyword searches. Use direct search tools in the meantime."),
            ("Malformed Search Syntax", "Incorrect Boolean syntax. Use quotes for exact phrases (e.g. 'EGFR assays') or separate terms with 'AND'." )
        ],
        "tips": "Combine keywords with structure drawings to locate specific assay records for a particular chemical class."
    },
    {
        "id": 16,
        "name": "Project Management",
        "purpose": "Organizes scientific studies, compounds, assays, and workflows into workspaces, facilitating collaboration within research teams.",
        "business": "Protects sensitive research projects by restricting access to authorized project members.",
        "scientific": "Maintains data organization across studies, linking targets to assays, compounds, and results to track progress.",
        "navigation": "Accessible from the sidebar menu under the 'Projects' link.",
        "screen_overview": "Displays active projects, recent updates, member lists, and study timelines.",
        "components": [
            ("Project Grid Panel", "Cards showing project name, code (e.g., PROJ-EGFR-2026), status, and active member count."),
            ("Add Project Button", "Launches a dialog to create a project, set privacy levels, and invite team members."),
            ("Project Workspace Tabs", "Organizes project-specific resources: 'Compounds', 'Assays', 'Workflows', and 'Members'."),
            ("Timeline Chart", "Visualizes milestone deadlines and study durations.")
        ],
        "workflow": [
            "Navigate to the Projects page.",
            "Click 'Create Project'.",
            "Enter the project name 'KRAS Inhibitor Lead Group'.",
            "Set the project visibility to 'Private - Invites Only'.",
            "Add team members and assign roles (e.g., Scientist, Admin).",
            "Click 'Save Project'."
        ],
        "expected": "Creation of the project space, updated navigation sidebar, and automated invitations sent to team members.",
        "errors": [
            ("Duplicate Project Code", "Project code already exists. Enter a unique identifier for the study."),
            ("Insufficient User Rights", "Only project administrators can modify project membership or settings.")
        ],
        "tips": "Link all related queries and workflow runs to a project workspace to keep study data consolidated."
    },
    {
        "id": 17,
        "name": "User Administration",
        "purpose": "Provides user management capabilities, allowing administrators to invite users, activate/deactivate accounts, monitor active sessions, and assign system access levels.",
        "business": "Maintains system security by ensuring only authorized personnel can access sensitive discovery data.",
        "scientific": "Enforces regulatory compliance by ensuring user details are linked to electronic signatures and audit trails.",
        "navigation": "Go to the Settings panel and select the 'User Admin' tab (requires Administrator role).",
        "screen_overview": "A dashboard displaying the user directory, account status badges, and action buttons.",
        "components": [
            ("User Directory Table", "Lists user name, email, role, status (Active, Suspended, Invited), and last login time."),
            ("Invite User Button", "Launches a modal to send email invitations and pre-assign roles."),
            ("Account Status Toggle", "Enables or disables accounts instantly."),
            ("Session Activity Monitor", "Displays active browser sessions with IP addresses and logout actions.")
        ],
        "workflow": [
            "Open Settings and select the 'User Admin' tab.",
            "Click 'Invite User'.",
            "Enter the user's email: 'm.curie@analytix.com'.",
            "Select the 'Scientist' role from the dropdown.",
            "Click 'Send Invitation'."
        ],
        "expected": "A notification confirming the invitation has been sent, and an entry added to the directory table with an 'Invited' status.",
        "errors": [
            ("User Already Registered", "Email address is already registered. Edit the existing user's profile to change their settings."),
            ("Domain Verification Failure", "Email domain is not on the whitelist. Verify email address or contact security team.")
        ],
        "tips": "Review the user directory monthly to deactivate inactive accounts and maintain license compliance."
    },
    {
        "id": 18,
        "name": "Role Based Access Control (RBAC)",
        "purpose": "Defines access control matrices that link roles (Admin, Scientist, Compliance Officer, Read-Only) to specific system permissions, ensuring users only access authorized modules.",
        "business": "Prevents unauthorized data modification and protects IP, ensuring compliance with data security requirements.",
        "scientific": "Prevents accidental modification of shared templates, assay records, and compliance logs by restricting access to authorized users.",
        "navigation": "Go to the Settings panel and select the 'RBAC Control' tab (requires Administrator role).",
        "screen_overview": "An interactive matrix mapping roles to system permissions, with custom role creation tools.",
        "components": [
            ("RBAC Matrix Grid", "A grid where columns represent roles and rows represent system actions, with checkboxes to manage permissions."),
            ("Custom Role Creator", "Launches a panel to define a role name and select its permissions."),
            ("Policy Editor Panel", "Sets conditional access rules, such as login IP whitelists and access windows."),
            ("Save RBAC Map Button", "Saves the access control matrix and updates system permissions.")
        ],
        "workflow": [
            "Open Settings and select the 'RBAC Control' tab.",
            "Locate the 'Scientist' role column in the matrix.",
            "Check the box for 'Metadata Schema Edit' to grant editing permissions.",
            "Uncheck the box for 'Audit Log Delete' to restrict deletion rights.",
            "Click 'Save RBAC Map' and enter your electronic signature password."
        ],
        "expected": "An audit log entry documenting the permission change, and updated access rights applied to all affected accounts.",
        "errors": [
            ("Permission Conflict", "Invalid combination of permissions (e.g. read-only role with editing rights). Verify changes in the validator panel."),
            ("Cannot Demote Self", "Administrators cannot revoke their own admin permissions. Have another admin perform the action.")
        ],
        "tips": "Follow the principle of least privilege. Grant write permissions only when necessary for a user's role."
    },
    {
        "id": 19,
        "name": "Notifications & Alerts",
        "purpose": "A notification center that alerts users to workflow updates, data sync status, connection changes, and compliance reviews.",
        "business": "Keeps project teams aligned on study progress, reducing delays in review and sign-off stages.",
        "scientific": "Alerts researchers when docking simulations, ADMET calculations, or sequence alignments are complete.",
        "navigation": "Accessible by clicking the 'Bell' icon in the top header, or going to the Settings page and selecting 'Alerts Config'.",
        "screen_overview": "A list of recent notifications with category filters and configuration panels for email and Slack integrations.",
        "components": [
            ("Notifications List", "A panel showing messages, source modules, and action links."),
            ("Integration Panel", "Configures webhook settings for Slack, Microsoft Teams, and email notifications."),
            ("Trigger Rules Table", "Lists notification rules, allowing users to select which events trigger alerts."),
            ("Mark All Read Button", "Clears all active notifications instantly.")
        ],
        "workflow": [
            "Click the 'Bell' icon in the header.",
            "Select a notification showing 'Workflow Execution Complete' to view results.",
            "Go to settings to configure notifications.",
            "Toggle 'Email Alerts' to enabled for 'Compliance Verification Failures'.",
            "Click 'Save Notification Preferences'."
        ],
        "expected": "Updated notification settings and confirmation that alerts will be delivered via the selected channels.",
        "errors": [
            ("Delivery Failure", "The email server or webhook returned an error. Verify notification settings in the Settings tab."),
            ("Notification Blocked", "Browser notifications are blocked by user settings. Enable notifications in your browser settings.")
        ],
        "tips": "Configure email digests for routine events to minimize inbox noise, while keeping real-time alerts enabled for critical compliance failures."
    },
    {
        "id": 20,
        "name": "Settings",
        "purpose": "The main settings panel containing configuration settings for user profiles, theme options, security preferences, database credentials, and network configurations.",
        "business": "Enables administrators to configure the platform to meet organizational security and network requirements.",
        "scientific": "Allows researchers to customize molecular drawing preferences, sequence alignment parameters, and search defaults.",
        "navigation": "Select 'Settings' from the left sidebar or navigate to '/settings' (accessible via User Profile footer).",
        "screen_overview": "A multi-section settings dashboard organized into: User Settings, Security & Auth, Connectors, and System Config.",
        "components": [
            ("Password Policy Panel", "Sets password requirements, including minimum length, character types, and expiration rules."),
            ("SMTP Settings Form", "Configures email server details, including host, port, username, password, and encryption protocol."),
            ("Proxy Configuration Fields", "Sets proxy details for systems that require proxy access to external web services."),
            ("Database Maintenance Panel", "Allows administrators to run database optimization tasks, prune logs, and back up schemas.")
        ],
        "workflow": [
            "Open Settings from the sidebar.",
            "Go to the 'Security & Auth' tab.",
            "Change password complexity requirement to 'Minimum 12 Characters'.",
            "Go to 'System Config' and enter SMTP server settings: SMTP Host 'smtp.analytix.com', Port '587'.",
            "Click 'Save Configurations' and enter your electronic signature password."
        ],
        "expected": "Updated system settings and a confirmation message indicating configurations have been applied successfully.",
        "errors": [
            ("Invalid SMTP Credentials", "Connection to SMTP server failed. Verify hostname, port, and credentials."),
            ("Save Failed", "Missing mandatory configuration values. Complete all required fields before saving.")
        ],
        "tips": "Back up system configurations before making changes to settings or database connections."
    }
]

# Additional content sections for manuals
INTRO_TEXT = """The AnalytiX Platform is a state-of-the-art enterprise informatics and in silico drug discovery suite. It integrates advanced cheminformatics, bioinformatics, federated data queries, and AI-driven scientific assistance into a single unified platform. 

This document serves as the official operational manual and compliance reference for AnalytiX. It details all 20 active platform modules, illustrating their purpose, business value, scientific value, user interface layout, step-by-step workflows, expected results, common errors, troubleshooting, and best practices.

Designed for both research scientists and system administrators, this manual provides the instructions necessary to operate the platform in a validated FDA 21 CFR Part 11 compliant environment."""

ROLES_AND_PERMISSIONS = """Access to the AnalytiX platform is governed by Role-Based Access Control (RBAC) to ensure security and compliance with FDA 21 CFR Part 11 guidelines. The system defines three primary default roles:

1. **Administrator (Admin)**: Full control over system configurations, user administration, connector management, RBAC settings, and database maintenance.
2. **Scientist**: Full access to research modules, including Data Registry, Compound Explorer, Bioinformatics Hub, Query Builder, Analytics Workbench, Workflow Designer, and AI Scientist Copilot.
3. **Compliance Officer**: Special access to the Audit Trail, Compliance Console, electronic signature verification, and system validation reports."""

GLOSSARY_TERMS = [
    ("SMILES", "Simplified Molecular-Input Line-Entry System. A line notation for describing the structure of chemical species using short ASCII strings."),
    ("FASTA", "A text-based format for representing either nucleotide sequences or peptide sequences, in which nucleotides or amino acids are represented using single-letter codes."),
    ("RDKit", "An open-source cheminformatics and machine learning software toolkit written in C++ and Python."),
    ("4PL Regression", "4-Parameter Logistic regression. A mathematical model used to analyze sigmoidal dose-response curves in biological assays."),
    ("FDA 21 CFR Part 11", "Title 21 of the Code of Federal Regulations; Electronic Records; Electronic Signatures. Enforces requirements for closed and open systems to ensure record authenticity."),
    ("Tanimoto Coefficient", "A statistical metric used to quantify the similarity between two molecular fingerprints, ranging from 0.0 (completely different) to 1.0 (identical)."),
    ("EAV Model", "Entity-Attribute-Value model. A database design pattern used to represent entity properties dynamically without modifying the database schema."),
    ("AST Graph", "Abstract Syntax Tree. A tree representation of the abstract syntactic structure of source code or visual queries."),
    ("SHA-256", "Secure Hash Algorithm 2. A cryptographic hash function that generates a unique 256-bit signature for data block verification."),
    ("IND", "Investational New Drug. An application filed with the FDA to obtain authorization for clinical testing of a new drug candidate.")
]

TROUBLESHOOTING_FAQS = [
    ("How do I resolve 'RDKit Parse Error' when registering a compound?", "Ensure the SMILES string you entered has valid chemical valency and correct formatting. Use the JSME sketcher to draw the structure and automatically generate the SMILES string."),
    ("Why can't I see the 'User Admin' or 'RBAC Control' tabs in Settings?", "These tabs are restricted to users with the Administrator role. Contact your system administrator to request access if required."),
    ("What should I do if the 'Ledger Integrity' check reports a warning?", "Contact your Compliance Officer or security team immediately. A warning indicates that audit logs have been altered outside the platform interface."),
    ("How do I download a workflow run execution report?", "When a workflow run completes, click the 'Export Report' button in the execution drawer to download a PDF report containing the run logs and results."),
    ("Why did my molecular docking workflow run time out?", "Molecular docking tasks can be computationally intensive. Open the node configuration drawer and reduce the docking grid size or adjust execution parameters.")
]

# Generate Markdown Document
def generate_markdown():
    filepath = os.path.join(DOCS_DIR, "AnalytiX_USER_MANUAL.md")
    print(f"Generating Markdown Manual: {filepath}")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# AnalytiX PLATFORM\n")
        f.write("## ENTERPRISE INFORMATICS & DISCOVERY PLATFORM USER MANUAL\n\n")
        
        f.write("### Document Suite v4.0.0\n")
        f.write("**Classification**: CONFIDENTIAL\n")
        f.write("**Regulatory Status**: FDA 21 CFR Part 11 Compliant Environment\n")
        f.write("**Last Updated**: June 2026\n\n")
        
        f.write("---\n\n")
        f.write("## 1. Introduction & Overview\n")
        f.write(INTRO_TEXT + "\n\n")
        
        f.write("---\n\n")
        f.write("## 2. Platform Architecture Overview\n")
        f.write("The AnalytiX platform is built using a modern, scalable, microservice-based architecture designed for high availability and strict data isolation. It features nine custom PostgreSQL database schemas (`gen_auth`, `metadata`, `query`, `connector`, `audit`, `lineage`, `bio`, `workflow`, `ai`) managed by independent microservices. The services communicate asynchronously via a message broker and expose secure REST APIs to the React-based frontend dashboard. All transactions are logged to a cryptographically chained audit ledger to maintain data integrity.\n\n")
        
        f.write("---\n\n")
        f.write("## 3. User Roles & Permissions\n")
        f.write(ROLES_AND_PERMISSIONS + "\n\n")
        
        f.write("---\n\n")
        f.write("## 4. Platform Modules Detail\n\n")
        
        for m in MODULES:
            f.write(f"### Module {m['id']}: {m['name']}\n")
            f.write(f"#### Purpose\n{m['purpose']}\n\n")
            f.write(f"#### Business Value\n{m['business']}\n\n")
            f.write(f"#### Scientific Value\n{m['scientific']}\n\n")
            f.write(f"#### Navigation Instructions\n{m['navigation']}\n\n")
            f.write(f"#### Screen Overview\n{m['screen_overview']}\n\n")
            f.write("#### Component Explanations\n")
            for name, desc in m['components']:
                f.write(f"- **{name}**: {desc}\n")
            f.write("\n")
            
            f.write("#### Step-by-Step Workflow Steps\n")
            for step in m['workflow']:
                f.write(f"1. {step}\n")
            f.write("\n")
            
            f.write(f"#### Expected Results\n{m['expected']}\n\n")
            
            f.write("#### Common Errors & Troubleshooting\n")
            for err, res in m['errors']:
                f.write(f"- **{err}**: {res}\n")
            f.write("\n")
            
            f.write(f"#### Tips & Best Practices\n{m['tips']}\n\n")
            f.write("---\n\n")
            
        f.write("## 5. AI Scientist Copilot Prompt Guide\n")
        f.write("The AI Scientist Copilot interprets natural language questions to query live databases using ground validation rules. Key prompt examples include:\n\n")
        f.write("1. *\"What compounds target EGFR?\"*\n")
        f.write("   - **Description**: Retrieves registered compounds and their activity status against the EGFR target protein.\n\n")
        f.write("2. *\"Show compounds with MW < 500 and LogP < 5\"*\n")
        f.write("   - **Description**: Filters compounds by physicochemical properties matching Lipinski's Rule of 5.\n\n")
        f.write("3. *\"Summarize assay results\"*\n")
        f.write("   - **Description**: Returns statistical summaries, compound counts, and active hits across recent assays.\n\n")
        f.write("4. *\"Find compounds active against KRAS\"*\n")
        f.write("   - **Description**: Performs a database query for compounds with active status or low IC50 values against KRAS.\n\n")
        f.write("5. *\"Show workflow execution history\"*\n")
        f.write("   - **Description**: Lists recent scientific workflow runs, execution status, and owner details.\n\n")
        
        f.write("---\n\n")
        f.write("## 6. Scientific Analytics Documentation\n")
        f.write("The platform provides statistics and metrics across multiple categories:\n")
        f.write("- **Dashboard KPIs**: System throughput, compound registration counts, active pipelines, and server response times.\n")
        f.write("- **Compound Analytics**: Physicochemical distribution, Tanimoto molecular similarity metrics, and R-group scaffold distributions.\n")
        f.write("- **Assay Analytics**: Sigmoidal curves, EC50/IC50 calculations, hill slopes, and assay performance metrics.\n")
        f.write("- **Bioinformatics Analytics**: Global/local alignment scores, sequence identity matrices, and hierarchical clustering dendrograms.\n")
        f.write("- **Workflow Analytics**: Workflow execution durations, node success rates, and parallel pipeline throughput.\n")
        f.write("- **Audit Analytics**: Log volume tracking, user action distributions, and compliance verification run statistics.\n")
        f.write("- **AI Usage Analytics**: Copilot query counts, SQL validation success rates, and user feedback distributions.\n\n")
        
        f.write("---\n\n")
        f.write("## 7. Compliance & FDA Validation\n")
        f.write("To maintain system integrity and comply with FDA regulations:\n")
        f.write("- **Audit Logs**: Cryptographically chained audit logs trace system activity.\n")
        f.write("- **Electronic Signatures**: Double-entry credentials require users to re-enter their passwords and select a reason for approvals.\n")
        f.write("- **Version Control**: Changes to workflows, queries, and metadata schema require version bumps.\n")
        f.write("- **Record Integrity**: SHA-256 hash chains verify that records are not altered outside the system.\n")
        f.write("- **Data Lineage**: Tracks files, data transformations, and queries back to source systems.\n")
        f.write("- **FDA 21 CFR Part 11**: Implements security controls, inactivity timeouts, and electronic signatures.\n\n")
        
        f.write("---\n\n")
        f.write("## 8. Troubleshooting FAQs\n")
        for q, a in TROUBLESHOOTING_FAQS:
            f.write(f"**Q: {q}**\n*A: {a}*\n\n")
            
        f.write("---\n\n")
        f.write("## 9. Platform Glossary\n")
        for term, definition in GLOSSARY_TERMS:
            f.write(f"- **{term}**: {definition}\n")

# PDF Generation Utilities
def build_cover_page(story, styles, title, subtitle):
    story.append(Spacer(1, 120))
    story.append(Paragraph(title.upper(), styles['title']))
    story.append(Paragraph(subtitle, styles['subtitle']))
    story.append(Spacer(1, 160))
    
    # Metadata block on cover page
    meta_text = """
    <b>Document Type:</b> Official Technical Operations Guide<br/>
    <b>Version:</b> 4.0.0 (Production Release)<br/>
    <b>Regulatory Status:</b> FDA 21 CFR Part 11 Compliant Environment<br/>
    <b>Author:</b> AnalytiX Biopharma Solutions Division<br/>
    <b>Classification:</b> CONFIDENTIAL
    """
    story.append(Paragraph(meta_text, styles['body']))
    story.append(PageBreak())

def build_pdf_document(filepath, title, subtitle, content_generator_func):
    print(f"Building PDF: {filepath}")
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = create_style_sheet()
    story = []
    
    # Build Cover Page
    build_cover_page(story, styles, title, subtitle)
    
    # Generate content flowables
    content_generator_func(story, styles)
    
    # Build document with cover page background callback and NumberedCanvas
    doc.build(story, onFirstPage=draw_cover_background, canvasmaker=NumberedCanvas)

# Content Generators for different PDFs
def generate_user_manual_content(story, styles):
    story.append(Paragraph("1. Introduction & Overview", styles['h1']))
    story.append(Paragraph(INTRO_TEXT, styles['body']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("1.1 Document Control & Version History", styles['h2']))
    story.append(Paragraph("The system maintenance ledger records modifications to this manual:", styles['body']))
    
    history_data = [
        ["Version", "Date", "Author", "Changes Summary"],
        ["1.0.0", "Jan 2025", "S. Kurapati", "Initial system documentation template."],
        ["2.0.0", "Jun 2025", "S. Kurapati", "Added cheminformatics and bioinformatics modules."],
        ["3.0.0", "Dec 2025", "S. Kurapati", "Added compliance, E-Signatures, and data lineage."],
        ["4.0.0", "Jun 2026", "Compliance Div", "FDA 21 CFR Part 11 alignment and AI Scientist prompts."]
    ]
    history_table = Table(history_data, colWidths=[60, 80, 100, 260])
    history_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f766e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#ffffff')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(history_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("2. Platform Architecture Overview", styles['h1']))
    story.append(Paragraph("AnalytiX platform implements a modern, secure, and distributed architecture. It isolates application domains across nine distinct PostgreSQL database schemas managed by independent microservices. Below is a summary of the schemas and ports:", styles['body']))
    
    arch_data = [
        ["Service Module", "Port", "Schema Name", "Data Objects / Primary Tables"],
        ["Authentication Service", "8001", "gen_auth", "users, roles, permissions, audit_auth"],
        ["Metadata Catalog Service", "8002", "metadata", "entities, values, attribute_fields (EAV)"],
        ["Query Builder Service", "8003", "query", "query_history, query_templates"],
        ["Cheminformatics Service", "8004", "cheminformatics", "compounds, structures, chemical_scaffolds"],
        ["Connector Service", "8005", "connector", "connectors, schemas, schedules"],
        ["Audit & Compliance Service", "8006", "audit", "audit_logs, electronic_signatures"],
        ["Data Lineage Service", "8007", "lineage", "lineage_nodes, lineage_edges"],
        ["Bioinformatics Service", "8008", "bio", "sequences, alignments, clusters"],
        ["Workflow Automation Service", "8009", "workflow", "workflow_definitions, workflow_runs"],
        ["AI Scientist Copilot Service", "8010", "ai", "chat_sessions, chat_messages, SQL_grounding"]
    ]
    arch_table = Table(arch_data, colWidths=[130, 45, 80, 245])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#ffffff')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("3. User Roles & Permissions", styles['h1']))
    story.append(Paragraph(ROLES_AND_PERMISSIONS, styles['body']))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("4. Platform Modules Detail", styles['h1']))
    story.append(Paragraph("This section provides a detailed operational breakdown of all 20 modules.", styles['body']))
    
    for m in MODULES:
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Module {m['id']}: {m['name']}", styles['h2']))
        story.append(Paragraph(f"<b>Purpose:</b> {m['purpose']}", styles['body']))
        
        # Values callout block
        val_text = f"<b>Business Value:</b> {m['business']}<br/><b>Scientific Value:</b> {m['scientific']}"
        story.append(Paragraph(val_text, styles['callout']))
        
        story.append(Paragraph(f"<b>Navigation Instructions:</b> {m['navigation']}", styles['body']))
        story.append(Paragraph(f"<b>Screen Overview:</b> {m['screen_overview']}", styles['body']))
        
        # Components table
        comp_data = [["Component / UI Element", "Description & Functional Actions"]]
        for name, desc in m['components']:
            comp_data.append([name, desc])
        comp_table = Table(comp_data, colWidths=[150, 350])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8.5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Component Explanation:</b>", styles['h3']))
        story.append(comp_table)
        story.append(Spacer(1, 6))
        
        # Step-by-Step Workflow
        story.append(Paragraph("<b>Step-by-Step Workflow Steps:</b>", styles['h3']))
        for i, step in enumerate(m['workflow'], 1):
            story.append(Paragraph(f"{i}. {step}", styles['bullet']))
        
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Expected Results:</b> {m['expected']}", styles['body']))
        
        # Troubleshooting block
        err_data = [["Common Error Scenario", "Troubleshooting Solution"]]
        for name, desc in m['errors']:
            err_data.append([name, desc])
        err_table = Table(err_data, colWidths=[150, 350])
        err_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fef2f2')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#991b1b')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8.5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#fca5a5')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Errors & Troubleshooting:</b>", styles['h3']))
        story.append(err_table)
        story.append(Spacer(1, 6))
        
        story.append(Paragraph(f"<b>Tips & Best Practices:</b> {m['tips']}", styles['body']))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceBefore=8, spaceAfter=8))
        
    story.append(PageBreak())
    
    # AI scientist copilot section
    story.append(Paragraph("5. AI Scientist Copilot Prompt Guide", styles['h1']))
    story.append(Paragraph("The AI Scientist Copilot translates natural language questions into database operations using grounding rules. This section lists prompt examples and how they are parsed by the system:", styles['body']))
    
    copilot_prompts = [
        ("What compounds target EGFR?", "Runs a join query between compounds and assay targets, returning a list of chemical structures and their corresponding IC50 values against the epidermal growth factor receptor."),
        ("Show compounds with MW < 500 and LogP < 5", "Performs a visual query filtering the database for drug-like small molecules matching key criteria of Lipinski's Rule of 5."),
        ("Summarize assay results", "Aggregates screening data to report standard metrics (e.g., active hits, average IC50, total compounds tested) across recent assay runs."),
        ("Find compounds active against KRAS", "Queries the database for compounds exhibiting active status or low nanomolar potency against KRAS targets."),
        ("Show workflow execution history", "Retrieves log entries from the workflow schema, listing the history of scientific pipeline runs, durations, and execution statuses.")
    ]
    for prompt, desc in copilot_prompts:
        story.append(Paragraph(f"<b>Prompt:</b> <i>\"{prompt}\"</i>", styles['h3']))
        story.append(Paragraph(f"<b>System Parsing & Grounding:</b> {desc}", styles['body']))
        story.append(Spacer(1, 4))
        
    story.append(PageBreak())
    
    # Scientific analytics section
    story.append(Paragraph("6. Scientific Analytics Workbench Documentation", styles['h1']))
    story.append(Paragraph("The Analytics Workbench provides advanced statistical modeling tools. It processes query results and performs calculations, including 4-Parameter Logistic (4PL) regression, Principal Component Analysis (PCA), and molecular similarity matrices.", styles['body']))
    
    story.append(Paragraph("6.1 Analytics Metrics Reference Table", styles['h2']))
    
    analytics_data = [
        ["Analytics Category", "Core Metrics", "Scientific Calculations", "Visualization Outputs"],
        ["Dashboard KPIs", "System throughput, compound velocity", "Aggregate counts, daily rates", "Time-series charts"],
        ["Compound Analytics", "MW, LogP, Tanimoto similarity", "Molecular descriptors, fingerprint similarity", "Scatter plots, similarity matrices"],
        ["Assay Analytics", "EC50, IC50, Hill slope, R2", "4PL curve fitting, non-linear regression", "Sigmoidal response curves"],
        ["Bioinformatics", "Alignment scores, sequence identity", "Smith-Waterman score, clustering distance", "Heatmaps, dendrograms"],
        ["Workflow", "Execution duration, node success rate", "Percent completion, average runtime", "Flow progress timelines"],
        ["Audit & Compliance", "Log counts, ledger status", "Verification calculations, hash check", "Audit charts, integrity bars"],
        ["AI Usage", "Query volume, validation rate", "Accuracy percentage, prompt count", "Usage charts, token volumes"]
    ]
    analytics_table = Table(analytics_data, colWidths=[100, 110, 150, 140])
    analytics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f766e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#ffffff')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(analytics_table)
    story.append(Spacer(1, 15))
    
    story.append(PageBreak())
    
    # Compliance section
    story.append(Paragraph("7. Compliance & FDA Validation", styles['h1']))
    story.append(Paragraph("Operating in a regulated pharmaceutical environment requires compliance with FDA 21 CFR Part 11 regulations. AnalytiX enforces these rules across the system.", styles['body']))
    
    compliance_rules = [
        ("Audit Logs Chaining", "All logs are secured using SHA-256 hash chains. Modifying a log entry invalidates the chain, alerting system administrators during ledger checks."),
        ("Electronic Signatures Double-Factor", "Critical actions (e.g., compound approval, data export) require users to re-enter their passwords and specify a reason for signing."),
        ("Version Control", "Workflows, query templates, and metadata structures are versioned. Previous versions are archived to maintain audit trails."),
        ("Data Lineage Traceability", "The system logs transformation steps, mapping files and query metrics back to source connectors for full traceability.")
    ]
    for title, desc in compliance_rules:
        story.append(Paragraph(f"<b>{title}:</b> {desc}", styles['body']))
        story.append(Spacer(1, 4))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("8. Troubleshooting FAQs", styles['h1']))
    for q, a in TROUBLESHOOTING_FAQS:
        story.append(Paragraph(f"<b>Q: {q}</b>", styles['h3']))
        story.append(Paragraph(f"<i>A: {a}</i>", styles['body']))
        story.append(Spacer(1, 4))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("9. Platform Glossary", styles['h1']))
    for term, definition in GLOSSARY_TERMS:
        story.append(Paragraph(f"<b>{term}</b>: {definition}", styles['body']))
        story.append(Spacer(1, 2))

def generate_quick_start_content(story, styles):
    story.append(Paragraph("1. Platform Onboarding", styles['h1']))
    story.append(Paragraph("Welcome to the AnalytiX platform. This Quick Start Guide gets you set up and running scientific queries and AI prompts within 10 minutes.", styles['body']))
    
    story.append(Paragraph("2. Initial Login & Session Setup", styles['h2']))
    story.append(Paragraph("1. Open your web browser and navigate to the platform URL.<br/>2. Log in using your email address and credentials.<br/>3. Verify that the 'SECURE SESSION' indicator is active in the top right corner.", styles['body']))
    
    story.append(Paragraph("3. Running Your First Structure Search", styles['h2']))
    story.append(Paragraph("1. Open the sidebar and click on <b>Compound Explorer</b>.<br/>2. In the chemical structure drawer, sketch your target molecule (or paste a SMILES string).<br/>3. Select the search mode (Exact, Substructure, or Similarity).<br/>4. Click the 'Execute Search' button.<br/>5. Review matching compound records in the results grid.", styles['body']))
    
    story.append(Paragraph("4. Using the AI Scientist Copilot", styles['h2']))
    story.append(Paragraph("1. Click <b>AI Scientist Copilot</b> in the sidebar.<br/>2. In the chat input field, type: <i>\"What compounds target EGFR?\"</i> and press Enter.<br/>3. The copilot retrieves matching compounds from the database, displays their structures, and lists active assay values.", styles['body']))
    
    story.append(Paragraph("5. Basic Troubleshooting Quick-Fixes", styles['h2']))
    story.append(Paragraph("- <b>Blank Screen on Startup:</b> Clear your browser cache and refresh the page to reload the chemical structure drawer modules.<br/>- <b>Session Expired Message:</b> Your session will automatically log out after 15 minutes of inactivity to comply with security requirements. Re-enter your credentials to resume work.", styles['body']))

def generate_admin_content(story, styles):
    story.append(Paragraph("1. System Administration & Configuration Guidelines", styles['h1']))
    story.append(Paragraph("This administrative guide details configuration settings, user access controls, and database connector setups for the AnalytiX platform.", styles['body']))
    
    story.append(Paragraph("2. User Management & Onboarding", styles['h2']))
    story.append(Paragraph("1. Navigate to Settings and select the <b>User Admin</b> tab.<br/>2. Click 'Invite User'.<br/>3. Enter the user's corporate email address and pre-assign a system role (Scientist, Admin, Compliance Officer).<br/>4. The user receives an email containing login instructions.", styles['body']))
    
    story.append(Paragraph("3. Role-Based Access Control (RBAC) Administration", styles['h2']))
    story.append(Paragraph("Access permissions are managed using the permission matrix in the <b>RBAC Control</b> tab. Assign write access only to users who require editing rights for metadata schemas or connector configurations.", styles['body']))
    
    story.append(Paragraph("4. Configuring Data Connectors", styles['h2']))
    story.append(Paragraph("1. Go to the <b>Data Connectors</b> page.<br/>2. Click 'Add New Connector'.<br/>3. Select the target database type (e.g., Snowflake, Oracle) and enter the host, port, database name, and credentials.<br/>4. Click 'Test Connection'.<br/>5. Click 'Discover Schema' to map database tables to the platform.", styles['body']))
    
    story.append(Paragraph("5. Audit Log Ledger Verification", styles['h2']))
    story.append(Paragraph("Maintain compliance by verifying the integrity of the audit logs. In the <b>Audit Trail</b> module, click 'Verify Ledger Integrity' to run verification scripts across the hash-chained database records.", styles['body']))

def generate_ai_copilot_content(story, styles):
    story.append(Paragraph("1. AI Scientist Copilot Operations Guide", styles['h1']))
    story.append(Paragraph("The AI Scientist Copilot is an advanced natural language interface designed to query chemical databases, structural libraries, and assay records using grounding rules.", styles['body']))
    
    story.append(Paragraph("2. Grounding Rules & Hallucination Prevention", styles['h2']))
    story.append(Paragraph("To prevent model hallucinations, the copilot validates all generated SQL queries against a strict schema mapping before execution. Queries that fail validation are automatically blocked.", styles['body']))
    
    story.append(Paragraph("3. Scientific Prompt Examples Library", styles['h2']))
    
    prompts_data = [
        ["Natural Language Prompt", "Target Database Fields", "Expected Query Outputs"],
        ["'What compounds target EGFR?'", "compounds, assay_targets, ic50", "Table of active compounds and IC50 potency metrics against EGFR."],
        ["'Show compounds with MW < 500 and LogP < 5'", "molecular_weight, clogp, smiles", "List of small molecule candidates matching Lipinski's Rule of 5."],
        ["'Summarize assay results'", "assay_runs, results, inhibition", "Statistical summaries, average inhibition, and active hit counts across assays."],
        ["'Find compounds active against KRAS'", "compounds, target_proteins, active_status", "Potent candidates with low nanomolar activity against KRAS targets."],
        ["'Show workflow execution history'", "workflow_definitions, workflow_runs", "Log history of automated pipeline executions and runtime statistics."]
    ]
    prompts_table = Table(prompts_data, colWidths=[150, 150, 200])
    prompts_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f766e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#ffffff')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(prompts_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("4. Formatting and Exporting Copilot Data", styles['h2']))
    story.append(Paragraph("Search results generated by the copilot can be exported directly. Use the 'Export to CSV' button on the results panel to save target compound tables and descriptors locally.", styles['body']))

# Execution block
if __name__ == "__main__":
    # 1. Master MD User Manual
    generate_markdown()
    
    # 2. Master PDF User Manual
    master_pdf_path = os.path.join(DOCS_DIR, "AnalytiX_USER_MANUAL.pdf")
    build_pdf_document(
        master_pdf_path,
        "AnalytiX Platform",
        "Enterprise Informatics & Discovery Platform - Comprehensive User Manual",
        generate_user_manual_content
    )
    
    # Copy master PDF to public assets folder in frontend
    shutil.copy(master_pdf_path, os.path.join(FRONTEND_DOCS_DIR, "AnalytiX_USER_MANUAL.pdf"))
    print(f"Copied Master PDF to frontend public: {os.path.join(FRONTEND_DOCS_DIR, 'AnalytiX_USER_MANUAL.pdf')}")
    
    # 3. Quick Start Guide PDF
    build_pdf_document(
        os.path.join(DOCS_DIR, "AnalytiX_QUICK_START_GUIDE.pdf"),
        "AnalytiX Quick Start Guide",
        "Rapid Onboarding Guide & Key Scientific Workflows",
        generate_quick_start_content
    )
    
    # 4. Admin Guide PDF
    build_pdf_document(
        os.path.join(DOCS_DIR, "AnalytiX_ADMIN_GUIDE.pdf"),
        "AnalytiX Admin Guide",
        "System Administration, RBAC Configuration, & Connector Setup",
        generate_admin_content
    )
    
    # 5. AI Scientist Copilot Guide PDF
    build_pdf_document(
        os.path.join(DOCS_DIR, "AnalytiX_AI_COPILOT_GUIDE.pdf"),
        "AnalytiX AI Copilot Guide",
        "Natural Language Querying, Grounding, & Scientific Prompting Guide",
        generate_ai_copilot_content
    )
    
    print("All documents generated successfully!")
