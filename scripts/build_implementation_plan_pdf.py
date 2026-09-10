from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)


OUT = Path("output/pdf/floodflow_prototype_implementation_plan.pdf")
OUT.parent.mkdir(parents=True, exist_ok=True)

NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#1677FF")
TEAL = colors.HexColor("#0E9F9A")
LIGHT = colors.HexColor("#F3F7FB")
MID = colors.HexColor("#D9E5F2")
TEXT = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")
ORANGE = colors.HexColor("#F59E0B")
GREEN = colors.HexColor("#16855B")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=28, leading=34, textColor=colors.white, alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=12, leading=17, textColor=colors.HexColor("#D9E5F2"), alignment=TA_CENTER))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, spaceBefore=4, spaceAfter=9))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=BLUE, spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13, textColor=TEXT, spaceAfter=5))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.8, leading=10.5, textColor=MUTED, spaceAfter=3))
styles.add(ParagraphStyle(name="CodeLike", parent=styles["BodyText"], fontName="Courier", fontSize=7.5, leading=10, textColor=NAVY, backColor=LIGHT, borderColor=MID, borderWidth=0.5, borderPadding=6, spaceBefore=3, spaceAfter=6))
styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=NAVY, backColor=colors.HexColor("#E8F1FF"), borderColor=BLUE, borderWidth=0.8, borderPadding=8, spaceBefore=5, spaceAfter=9))


def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def bullets(items):
    return [P("• " + x) for x in items]


def table(data, widths=None, header=True):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    cmds = [
        ("GRID", (0, 0), (-1, -1), 0.35, MID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        cmds += [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    for row in range(1 if header else 0, len(data)):
        if row % 2 == 0:
            cmds.append(("BACKGROUND", (0, row), (-1, row), LIGHT))
    t.setStyle(TableStyle(cmds))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(MID)
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, "FloodFlow | Prototype implementation handoff")
    canvas.drawRightString(192 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.circle(32 * mm, 245 * mm, 22 * mm, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.circle(176 * mm, 60 * mm, 35 * mm, fill=1, stroke=0)
    canvas.restoreState()


class Doc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(filename, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=17 * mm, bottomMargin=19 * mm)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        def page_decorator(canvas, doc):
            if doc.page == 1:
                cover(canvas, doc)
            else:
                footer(canvas, doc)
        self.addPageTemplates([PageTemplate(id="all", frames=frame, onPage=page_decorator)])


story = []

# Cover
story += [Spacer(1, 68 * mm), P("FloodFlow", "CoverTitle"), P("Urban Flood Nowcasting System", "CoverSub"), Spacer(1, 8 * mm), P("Prototype implementation plan and multi-agent handoff guide", "CoverSub"), Spacer(1, 54 * mm), P("Chennai-wide map | Velachery–Pallikaranai–Medavakkam predictive pilot", "CoverSub"), P("Version 1.0 | 23 August 2026", "CoverSub"), PageBreak()]

story += [P("1. Purpose and boundaries", "H1x"), P("FloodFlow is a professional, mobile-responsive web dashboard that shows all of Chennai on an OpenStreetMap-based map, while running detailed flood prediction for the Velachery–Pallikaranai–Medavakkam pilot area. The prototype uses static and synthetic inputs through a live simulator so the same APIs can later accept real IMD, radar, municipal, and OSM feeds."), P("The goal of this plan is to split implementation into independent parts. Each part has a clear output and a handoff contract so another agent can continue without reconstructing the project context."), P("Prototype truth rule: real flood history and hotspot data are used for reference and validation; synthetic DEM, roads, rainfall, land cover, and drainage data are labelled and never presented as real measurements.", "Callout"), P("Coverage behavior", "H2x"), *bullets(["Show all of Chennai in the map.", "Show the pilot coverage boundary as a subtle overlay.", "Run predictive layers only where model data exists.", "Outside coverage, show the base map and a clear 'predictive model unavailable' message."]), PageBreak()]

story += [P("2. End-to-end technical flow", "H1x"), P("The runtime flow is:"), P("Data providers → validation → simulator/live ingestion → runoff model → DEM surface flow → drainage graph → rolling state → flood depth/risk → database → WebSocket/API → dashboard and safe routing", "CodeLike"), P("The frontend must not know whether data is synthetic or real. It calls stable API contracts. Only the backend provider changes when a real source is connected."), P("Core stack", "H2x"), table([[P("Layer", "Smallx"), P("Technology", "Smallx"), P("Responsibility", "Smallx")], [P("Frontend"), P("React + TypeScript + Vite"), P("Dashboard, auth, forms, responsive UI")], [P("Map"), P("MapLibre GL JS + OSM-compatible tiles"), P("Map, animated layers, routes")], [P("Backend"), P("FastAPI + Python"), P("APIs, simulator, auth, orchestration")], [P("Geospatial"), P("GeoPandas, Shapely, Rasterio"), P("Vectors, geometry, DEM/raster processing")], [P("Model"), P("NumPy + NetworkX; optional XGBoost"), P("Runoff, flow, drainage, risk correction")], [P("Database"), P("Neon PostgreSQL + PostGIS"), P("Users, reports, predictions, spatial data")], [P("Routing"), P("OSRM initially"), P("Flood-aware route calculation")]], [30*mm, 52*mm, 92*mm]), PageBreak()]

parts = [
    ("Part 0 - Project foundation and conventions", "Create the repository skeleton, environment configuration, README, linting, and a shared data-provenance convention.", ["Create frontend/, backend/, data/, database/, docs/, scripts/.", "Define .env.example and never commit secrets.", "Define source_type: real, synthetic, simulated.", "Define the pilot bbox and WGS84 input convention.", "Add a health endpoint and a minimal frontend shell."], "Output: a runnable skeleton with /health and a documented start command."),
    ("Part 1 - Data audit and cleaning", "Make every current dataset loadable and produce a machine-readable inventory.", ["Validate GeoJSON, CSV, and ASCII DEM files.", "Ignore explanatory drainage comment rows.", "Check node/edge references and duplicate IDs.", "Normalize CRS metadata and coordinate order.", "Write processed clean files without modifying originals.", "Record real versus synthetic status."], "Output: data/processed plus validation_report.json. Handoff: all later parts consume processed data only."),
    ("Part 2 - Neon/PostGIS database and seed data", "Create the database schema and load spatial/vector seed data.", ["Enable PostGIS.", "Create users, roles, sessions, reports, roads, wards, drainage, hotspots, facilities, forecast_runs, flood_predictions, and audit_logs.", "Add geometry indexes and timestamps.", "Seed real history/hotspots and synthetic prototype layers.", "Add is_synthetic and source_name to relevant tables."], "Output: migrations, seed script, and a repeatable database setup command."),
    ("Part 3 - Provider interfaces and static providers", "Build replaceable provider interfaces for every input source.", ["Implement RainfallProvider, DEMProvider, RoadProvider, LandcoverProvider, DrainageProvider, FloodHistoryProvider, and EmergencyFacilityProvider.", "Implement local synthetic/static providers first.", "Return typed records with source metadata.", "Add provider-level tests."], "Output: the model can request data without reading files directly. Handoff: future IMD/OSM connectors implement the same interfaces."),
    ("Part 4 - Simulator and rolling time engine", "Make static files behave like live feeds.", ["Implement 15-minute simulation steps.", "Support start, pause, reset, advance, and playback speed.", "Read observed plus forecast rainfall separately.", "Persist simulator time and run ID.", "Publish updates through WebSocket."], "Output: /api/simulator and a stream of timestamped rainfall updates."),
    ("Part 5 - Baseline flood model", "Implement the explainable physics-inspired prediction engine.", ["Convert rainfall to runoff using land-cover coefficients.", "Use DEM cells to estimate downhill accumulation.", "Attach runoff to nearby roads and drainage nodes.", "Build the directed drainage graph.", "Compare inflow with edge capacity.", "Carry storage/utilization state across timesteps.", "Emit depth, utilization, risk, confidence, and provenance."], "Output: deterministic flood_predictions for Now, +15m, +30m, +1h, +2h, and +3h."),
    ("Part 6 - Optional ML correction layer", "Add ML only after the baseline is stable and measurable.", ["Create features: rainfall, cumulative rainfall, elevation, slope, land cover, drainage utilization, distance to drain, history, and public reports.", "Start with XGBoost or LightGBM for flood probability/risk correction.", "Use time-based and spatial validation splits.", "Never treat synthetic labels as real-world accuracy evidence.", "Keep physics output and ML output visible separately."], "Output: optional ml_flood_probability and final_risk fields. Do not block the demo if ML is unavailable."),
    ("Part 7 - FastAPI APIs and access control", "Expose stable APIs for the frontend and protect admin operations.", ["Implement rainfall, flood, drainage, reports, facilities, routes, simulator, auth, and admin routers.", "Use Pydantic schemas and consistent error responses.", "Implement guest, user, operator, admin, and super-admin roles.", "Use password hashing and secure HTTP-only sessions.", "Audit simulator, dataset, report, and user-management actions."], "Output: documented API with protected admin endpoints and a demo admin account."),
    ("Part 8 - Dashboard shell and map", "Build the professional responsive interface.", ["Use React, TypeScript, MapLibre, and responsive CSS.", "Show all of Chennai on the base map.", "Add pilot coverage boundary.", "Add layer controls, legend, search, location button, and status badge.", "Use mobile bottom sheets instead of desktop side panels."], "Output: a polished map-first dashboard that works at phone and desktop widths."),
    ("Part 9 - Map animations and forecast UX", "Turn model outputs into clear, meaningful visual feedback.", ["Animate rainfall intensity.", "Animate flood polygons expanding through timeline steps.", "Color roads by predicted depth.", "Animate drainage flow arrows and overloaded nodes.", "Add Play/Pause forecast and Now/+15m/+30m/+1h/+2h/+3h controls.", "Always show synthetic/live status and forecast confidence."], "Output: a judge-ready flood progression demonstration tied to actual model values."),
    ("Part 10 - Emergency facilities and safe routing", "Provide practical flood-aware escape routes.", ["Load hospitals, fire stations, police stations, and shelters.", "Find nearby facilities using spatial queries.", "Apply road penalties or block roads above thresholds.", "Rank routes by safe travel time, not distance alone.", "Display route, avoided roads, depth warnings, and limitations."], "Output: Find Nearest Safe Hospital and custom safe-route flows."),
    ("Part 11 - Public reports and profile", "Add useful public participation without contaminating the model.", ["Allow guests to view; require login to submit reports.", "Collect GPS, depth category, road status, photo, and timestamp.", "Show reports separately as Observed, not Predicted.", "Add confirmation, expiry, moderation, and confidence scoring.", "Add profile, saved locations, alert preferences, and My Reports."], "Output: mobile-first flood reporting and an admin verification queue."),
    ("Part 12 - Validation, demo, and handoff", "Prove the prototype works and document its limits.", ["Compare predictions with real flood-history records and known hotspots.", "Report hits, false alarms, misses, and depth limitations.", "Test simulator restart, API errors, mobile layout, and permissions.", "Create a seeded demo scenario and a two-minute presentation script.", "Document the exact next real-data replacement steps."], "Output: reproducible demo, validation report, and final handoff package."),
]

for title, goal, actions, output in parts:
    story += [P(title, "H1x"), P("Goal: " + goal), P("Implementation checklist", "H2x"), *bullets(actions), P(output, "Callout"), P("Continuity contract", "H2x"), P("The next agent should begin by reading the previous part's output, running its verification command, and preserving all existing provider/API contracts. Do not replace real data with synthetic data; add synthetic fallbacks only under explicit synthetic names."), PageBreak()]

story += [P("3. Database outline", "H1x"), P("Neon/PostGIS is appropriate once reports, users, predictions, and emergency facilities are part of the product. Large DEM/radar rasters should remain files or object storage, with metadata in the database."), table([[P("Table", "Smallx"), P("Purpose", "Smallx")], [P("users / sessions"), P("Users, roles, secure sessions")], [P("roads / wards"), P("Spatial map and routing layers")], [P("drainage_nodes / drainage_edges"), P("Network structure and state")], [P("rainfall_observations / forecasts"), P("Input time series and provenance")], [P("forecast_runs / flood_predictions"), P("Reproducible outputs by lead time")], [P("public_flood_reports"), P("Crowd observations and moderation")], [P("emergency_facilities"), P("Hospitals, fire, police, shelters")], [P("audit_logs"), P("Admin and operational traceability")]], [52*mm, 122*mm]), PageBreak()]

story += [P("4. Definition of done", "H1x"), P("The prototype is complete when a user can open the full-Chennai map, start the simulator, watch rainfall and flood-risk animations change through the 0–3 hour timeline, inspect drainage stress, find a flood-aware route to a hospital, submit a public flood report, and see clear real/synthetic labels."), P("Technical acceptance", "H2x"), *bullets(["Backend starts with one documented command.", "Frontend starts and is usable on phone and desktop.", "Static providers can be swapped without changing model APIs.", "Simulator produces deterministic results from the same seed.", "Admin-only actions are blocked server-side for public users.", "Every prediction includes forecast time, confidence, and provenance.", "No synthetic layer is labelled as real in the UI or database."]), P("Suggested execution order", "H2x"), P("Build Parts 0–5 first for a complete technical demo. Add Parts 7–10 for the polished public-facing product. Add Parts 6 and 11–12 after the core flow is stable."), P("Next agent handoff template", "H2x"), P("Completed part: ____<br/>Files changed: ____<br/>Verification command: ____<br/>Known issues: ____<br/>Next part to implement: ____<br/>Do not redo: ____", "CodeLike")]

doc = Doc(str(OUT))
doc.handle_nextPageTemplate = lambda *args, **kwargs: None
doc.build(story)
print(OUT)
