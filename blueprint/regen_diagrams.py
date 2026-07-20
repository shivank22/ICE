#!/usr/bin/env python3
"""Regenerate docs/02-06 and 10 .drawio diagrams with overlap-free layouts.

Every edge gets explicit exit/entry points and waypoints so no line ever
crosses a node box, and every edge label sits over free whitespace with a
white background.
"""
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"

BLUE = "fillColor=#dae8fc;strokeColor=#6c8ebf;"
GREEN = "fillColor=#d5e8d4;strokeColor=#82b366;"
PURPLE = "fillColor=#e1d5e7;strokeColor=#9673a6;"
YELLOW = "fillColor=#fff2cc;strokeColor=#d6b656;"
ORANGE = "fillColor=#ffe6cc;strokeColor=#d79b00;"
RED = "fillColor=#f8cecc;strokeColor=#b85450;"
GREY = "fillColor=#f5f5f5;strokeColor=#666666;"

BOX = "rounded=1;whiteSpace=wrap;html=1;fontSize=11;fontStyle=1;"
CYL = "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=10;fontSize=11;"
DOC = "shape=document;whiteSpace=wrap;html=1;boundedLbl=1;fontSize=11;"
RHOMB = "rhombus;whiteSpace=wrap;html=1;fontSize=11;fontStyle=1;"
NOTE = ("rounded=0;whiteSpace=wrap;html=1;align=left;verticalAlign=top;"
        "fontSize=10;spacingLeft=6;spacingTop=4;" + GREY)
TITLE = ("text;html=1;strokeColor=none;fillColor=none;align=center;"
         "verticalAlign=middle;fontStyle=1;fontSize=16;fontColor=#1a1a2e;")
BG = ("rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fontSize=12;"
      "fillColor=none;strokeColor=#999999;dashed=1;spacingTop=2;")


def esc(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;")
            .replace("<", "&lt;").replace(">", "&gt;").replace("\n", "&#xa;"))


class D:
    def __init__(self, did, name, w, h):
        self.did, self.name, self.w, self.h = did, name, w, h
        self.cells = []
        self.geo = {}

    def node(self, nid, label, x, y, w, h, style):
        self.geo[nid] = (x, y, w, h)
        self.cells.append(
            f'        <mxCell id="{nid}" value="{esc(label)}" style="{style}" '
            f'vertex="1" parent="1">\n          <mxGeometry x="{x}" y="{y}" '
            f'width="{w}" height="{h}" as="geometry" />\n        </mxCell>')

    def edge(self, eid, src, dst, label="", exit_at=None, entry_at=None,
             points=None, dashed=False, color=None, lpos=None, lx=None, ly=None):
        # lpos: -1..1 position of the label along the edge (0 = midpoint).
        # lx/ly are accepted for backward compat and ignored.
        style = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;"
                 "endFill=1;strokeWidth=1;fontSize=10;labelBackgroundColor=#ffffff;")
        if dashed:
            style += "dashed=1;"
        if color:
            style += f"strokeColor={color};"
        if exit_at:
            style += f"exitX={exit_at[0]};exitY={exit_at[1]};exitDx=0;exitDy=0;"
        if entry_at:
            style += f"entryX={entry_at[0]};entryY={entry_at[1]};entryDx=0;entryDy=0;"
        pts = ""
        if points:
            arr = "".join(f'<mxPoint x="{x}" y="{y}" />' for x, y in points)
            pts = f"<Array as=\"points\">{arr}</Array>"
        geo = f'<mxGeometry relative="1" as="geometry">{pts}</mxGeometry>'
        if label and lpos is not None:
            geo = (f'<mxGeometry x="{lpos}" relative="1" as="geometry">{pts}'
                   f'</mxGeometry>')
        val = f' value="{esc(label)}"' if label else ""
        self.cells.append(
            f'        <mxCell id="{eid}"{val} style="{style}" edge="1" parent="1" '
            f'source="{src}" target="{dst}">\n          {geo}\n        </mxCell>')

    def write(self, path):
        body = "\n".join(self.cells)
        xml = f'''<mxfile host="app.diagrams.net" agent="Agentic Framework Architecture" version="22.1.0" type="device">
  <diagram id="{self.did}" name="{esc(self.name)}">
    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.w}" pageHeight="{self.h}" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
{body}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
'''
        Path(path).write_text(xml)
        print("wrote", path)


# ---------------------------------------------------------------- 02
d = D("af-ms-map", "Microservice Map", 1460, 720)
d.node("title", "Agentic Framework — Microservice Map\n(all deployable components)", 300, 10, 800, 50, TITLE)
d.node("bgc", "Clients", 40, 90, 220, 240, BG)
d.node("web", "web\n(guided wizard UI)", 70, 130, 160, 50, BOX + BLUE)
d.node("mcp", "mcp", 70, 190, 160, 40, BOX + BLUE)
d.node("cli", "cli", 70, 240, 160, 40, BOX + BLUE)
d.node("gw", "gateway\nAuth · RBAC · REST · SSE", 340, 150, 160, 70, BOX + YELLOW)
d.node("bgm", "Deployable Microservices", 580, 80, 620, 430, BG)
d.node("job", "job-service", 620, 130, 140, 50, BOX + GREEN)
d.node("know", "knowledge-service", 620, 230, 140, 50, BOX + PURPLE)
d.node("orch", "agent-orchestrator\nLangGraph + Deep Agents", 800, 130, 150, 50, BOX + GREEN)
d.node("finops", "finops-engine", 820, 330, 150, 50, BOX + ORANGE)
d.node("adapt", "adaption-engine", 820, 410, 150, 50, BOX + ORANGE)
d.node("loader", "skill-loader\n(central mount hub)", 1010, 130, 160, 60, BOX + PURPLE)
d.node("prov", "sandbox-provisioner", 1010, 230, 160, 50, BOX + GREEN)
d.node("pg", "Postgres\n+ pgvector", 620, 560, 140, 60, CYL + GREY)
d.node("lf", "Langfuse\nSkills + Traces", 790, 560, 140, 60, CYL + GREY)
d.node("bus", "Message Bus", 960, 560, 140, 60, CYL + GREY)
d.node("runners", "Ephemeral Runners\nResearch · Execution · Reporting", 1180, 560, 220, 60, BOX + YELLOW)
d.node("note", "skill-loader resolves skills, calls sandbox-provisioner,\nmounts skills onto runners; agents use mounted skills.", 40, 560, 260, 80, NOTE)
d.edge("e1", "web", "gw", exit_at=(1, .5), entry_at=(0, .3))
d.edge("e2", "mcp", "gw", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e3", "cli", "gw", exit_at=(1, .5), entry_at=(0, .7))
d.edge("e4", "gw", "job", exit_at=(1, .3), entry_at=(0, .5), points=[(540, 171), (540, 155)])
d.edge("e5", "gw", "know", exit_at=(1, .7), entry_at=(0, .5), points=[(550, 199), (550, 255)])
d.edge("e6", "gw", "finops", exit_at=(.4, 1), entry_at=(0, .5), points=[(404, 355)])
d.edge("e7", "gw", "adapt", exit_at=(.7, 1), entry_at=(0, .5), points=[(452, 435)])
d.edge("e8", "job", "orch", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e9", "orch", "loader", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e10", "loader", "know", "resolve skills", dashed=True,
       exit_at=(.25, 1), entry_at=(.5, 0), points=[(1050, 210), (690, 210)], lx=870, ly=210)
d.edge("e11", "loader", "prov", "spawn", exit_at=(.75, 1), entry_at=(.75, 0), lx=1130, ly=210)
d.edge("e12", "prov", "runners", "create runners", exit_at=(.5, 1), entry_at=(.5, 0),
       points=[(1090, 530), (1290, 530)], lx=1190, ly=530)
d.edge("e13", "loader", "runners", "mount skills", color="#9673a6",
       exit_at=(1, .5), entry_at=(.32, 0), points=[(1250, 160), (1250, 540), (1250, 540)], lx=1250, ly=350)
d.edge("e14", "orch", "runners", "agents use skills", dashed=True,
       exit_at=(.5, 1), entry_at=(.14, 0), points=[(875, 540), (1211, 540)], lpos=-0.45)
d.edge("e15", "know", "pg", exit_at=(.5, 1), entry_at=(.5, 0))
d.edge("e16", "know", "lf", exit_at=(.79, 1), entry_at=(.46, 0), points=[(731, 520), (855, 520)])
d.edge("e17", "lf", "finops", "token costs", dashed=True,
       exit_at=(0, .5), entry_at=(0, .5), points=[(795, 590), (795, 355)], lpos=-0.4)
d.edge("e18", "job", "bus", "events", exit_at=(0, .5), entry_at=(.5, 0),
       points=[(600, 155), (600, 535), (1030, 535)], lx=950, ly=535)
d.edge("e19", "bus", "adapt", exit_at=(.2, 0), entry_at=(.35, 1),
       points=[(988, 480), (872, 480)])
d.write(DOCS / "02-microservices-map.drawio")

# ---------------------------------------------------------------- 03
d = D("af-sys", "Agentic Framework System Overview", 1400, 760)
d.node("title", "Agentic Framework — System Overview (Platforms + Engines + Runners)", 200, 10, 1000, 40, TITLE)
d.node("bga", "Access Platform", 40, 80, 260, 300, BG)
d.node("web", "Web UI\nguided wizard", 70, 130, 200, 50, BOX + BLUE)
d.node("mcp", "MCP", 70, 200, 200, 40, BOX + BLUE)
d.node("cli", "CLI", 70, 260, 200, 40, BOX + BLUE)
d.node("gw", "API Gateway", 360, 180, 150, 60, BOX + YELLOW)
d.node("bge", "Execution Platform", 570, 80, 360, 300, BG)
d.node("job", "job-service", 600, 130, 120, 50, BOX + GREEN)
d.node("orch", "agent-orchestrator", 760, 130, 140, 50, BOX + GREEN)
d.node("loader", "skill-loader", 600, 230, 120, 50, BOX + PURPLE)
d.node("prov", "sandbox-provisioner", 760, 230, 140, 50, BOX + GREEN)
d.node("bgk", "Skill & Knowledge Platform", 990, 80, 360, 300, BG)
d.node("know", "knowledge-service", 1020, 130, 140, 50, BOX + PURPLE)
d.node("pg", "Postgres + pgvector", 1020, 230, 140, 60, CYL + GREY)
d.node("lf", "Langfuse", 1190, 230, 130, 60, CYL + GREY)
d.node("bgr", "Ephemeral Runners", 570, 450, 500, 140, BG)
d.node("r1", "Research", 600, 500, 100, 50, BOX + YELLOW)
d.node("r2", "Execution", 720, 500, 100, 50, BOX + YELLOW)
d.node("r3", "Reporting", 840, 500, 100, 50, BOX + YELLOW)
d.node("r4", "Custom\n(optional)", 955, 500, 90, 50, BOX + YELLOW)
d.node("ext", "External\nsystems / APIs / data", 1130, 475, 220, 90, NOTE)
d.node("bgn", "Engines", 40, 450, 260, 220, BG)
d.node("finops", "finops-engine\ncost per agent run", 70, 500, 200, 60, BOX + ORANGE)
d.node("adapt", "adaption-engine\ntracks + email", 70, 580, 200, 60, BOX + ORANGE)
d.node("own", "Stakeholders", 380, 590, 140, 60, "ellipse;whiteSpace=wrap;html=1;fontSize=11;fontStyle=1;" + BLUE)
d.edge("e1", "web", "gw", exit_at=(1, .5), entry_at=(0, .2))
d.edge("e2", "mcp", "gw", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e3", "cli", "gw", exit_at=(1, .5), entry_at=(0, .8))
d.edge("e4", "gw", "job", exit_at=(1, .3), entry_at=(0, .5), points=[(540, 198), (540, 155)])
d.edge("e5", "job", "orch", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e6", "orch", "loader", exit_at=(.2, 1), entry_at=(1, .3), points=[(788, 245)])
d.edge("e7", "loader", "prov", "spawn", exit_at=(1, .7), entry_at=(0, .7), lx=740, ly=265)
d.edge("e8", "loader", "know", "resolve skills + facts", dashed=True,
       exit_at=(.5, 1), entry_at=(0, .7), points=[(660, 410), (1005, 410), (1005, 165)], lpos=0.35)
d.edge("e9", "know", "pg", exit_at=(.35, 1), entry_at=(.5, 0))
d.edge("e10", "know", "lf", exit_at=(1, .5), entry_at=(.5, 0), points=[(1255, 155)])
d.edge("e11", "prov", "runners_anchor", dashed=False) if False else None
d.edge("e11", "prov", "r3", "spawn runners", exit_at=(.6, 1), entry_at=(.5, 0),
       points=[(844, 420), (890, 420)], lpos=-0.5)
d.edge("e12", "loader", "r1", "mount skills", color="#9673a6",
       exit_at=(.15, 1), entry_at=(.5, 0), points=[(618, 430), (650, 430)], lx=618, ly=350)
d.edge("e13", "orch", "r2", "agents use mounted skills", dashed=True,
       exit_at=(1, .5), entry_at=(1, 0), points=[(955, 155), (955, 470), (820, 470)], lpos=0.42)
d.edge("e14", "r4", "ext", exit_at=(1, .5), entry_at=(0, .5), dashed=True)
d.edge("e15", "gw", "finops", exit_at=(.3, 1), entry_at=(1, .5), points=[(405, 530)])
d.edge("e16", "gw", "adapt", exit_at=(.6, 1), entry_at=(1, .25), points=[(450, 595)])
d.edge("e17", "adapt", "own", "email", exit_at=(1, .75), entry_at=(0, .5), lx=330, ly=625)
d.write(DOCS / "03-system-overview.drawio")

# ---------------------------------------------------------------- 04
d = D("af-sk", "Skill & Knowledge Platform", 1300, 720)
d.node("title", "Agentic Framework — Skill & Knowledge Platform", 200, 10, 900, 40, TITLE)
d.node("agents", "agent-orchestrator\n+ runners (agents)", 40, 140, 160, 70, BOX + GREEN)
d.node("know", "knowledge-service\nretrieval · CRUD · review", 320, 140, 170, 70, BOX + PURPLE)
d.node("bgs", "Stores", 580, 80, 400, 340, BG)
d.node("lf", "Langfuse\nPROCEDURAL skills\n(production label)", 620, 120, 170, 80, CYL + GREY)
d.node("pg", "Postgres + pgvector\nSEMANTIC + EPISODIC", 620, 240, 170, 80, CYL + GREY)
d.node("sem", "Semantic memory\norg facts · standards", 820, 240, 140, 50, BOX + BLUE)
d.node("epi", "Episodic memory\npast runs", 820, 310, 140, 50, BOX + BLUE)
d.node("bgf", "Four Framework Skills (procedural, in Langfuse)", 40, 300, 400, 220, BG)
d.node("s1", "1. Research", 70, 340, 160, 40, BOX + YELLOW)
d.node("s2", "2. Planning", 250, 340, 160, 40, BOX + YELLOW)
d.node("s3", "3. Execution", 70, 400, 160, 40, BOX + YELLOW)
d.node("s4", "4. Reporting", 250, 400, 160, 40, BOX + YELLOW)
d.node("noteb", "Procedural = Langfuse\nSemantic + Episodic = Postgres\nskill-loader fetches production skills via knowledge-service", 70, 455, 340, 50, NOTE)
d.node("bgl", "Skill Update Loop", 580, 470, 680, 190, BG)
d.node("refl", "Reflection\nmine episodes", 620, 530, 150, 60, BOX + ORANGE)
d.node("cr", "change_request", 830, 530, 150, 60, DOC + PURPLE)
d.node("hitl", "Human reviewer\nHITL", 1040, 520, 170, 80, RHOMB + RED)
d.edge("e1", "agents", "know", "retrieve skills\n+ facts + episodes", exit_at=(1, .3), entry_at=(0, .3), lx=260, ly=140)
d.edge("e2", "agents", "know", "write episode", dashed=True,
       exit_at=(1, .8), entry_at=(0, .8), lx=260, ly=215)
d.edge("e3", "know", "lf", "prod prompts", exit_at=(1, .3), entry_at=(0, .5), points=[(540, 161), (540, 160)], lx=555, ly=145)
d.edge("e4", "know", "pg", "facts + episodes", exit_at=(1, .8), entry_at=(0, .5), points=[(540, 196), (540, 280)], lx=555, ly=280)
d.edge("e5", "pg", "sem", exit_at=(1, .3), entry_at=(0, .5), dashed=True)
d.edge("e6", "pg", "epi", exit_at=(1, .8), entry_at=(0, .5), dashed=True, points=[(805, 304), (805, 335)])
d.edge("e7", "pg", "refl", "episodes", exit_at=(.5, 1), entry_at=(.5, 0), lx=705, ly=440)
d.edge("e8", "refl", "cr", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e9", "cr", "hitl", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e10", "hitl", "lf", "approve skill", exit_at=(.5, 0), entry_at=(1, .5),
       points=[(1125, 160)], lx=960, ly=160)
d.edge("e11", "hitl", "pg", "approve fact", exit_at=(.75, 0), entry_at=(1, .8),
       points=[(1168, 440), (810, 440)], points_after=None, lx=990, ly=440) if False else None
d.edge("e11", "hitl", "epi", "approve fact", exit_at=(.75, 0), entry_at=(1, .5),
       points=[(1168, 335)], lx=1070, ly=335)
d.write(DOCS / "04-skill-knowledge-platform.drawio")

# ---------------------------------------------------------------- 05
d = D("af-exec", "Execution & Skill Mount", 1460, 640)
d.node("title", "Agentic Framework — Execution: skill-loader mounts skills onto ephemeral runners", 200, 10, 1000, 40, TITLE)
d.node("job", "job-service", 40, 120, 130, 50, BOX + GREEN)
d.node("orch", "agent-orchestrator\nDeep Agents", 230, 120, 150, 50, BOX + GREEN)
d.node("loader", "skill-loader\n(central mount hub)", 460, 115, 160, 60, BOX + PURPLE)
d.node("prov", "sandbox-provisioner", 690, 120, 160, 50, BOX + GREEN)
d.node("know", "knowledge-service", 460, 260, 160, 50, BOX + PURPLE)
d.node("lf", "Langfuse\ncentralized skills", 690, 250, 140, 65, CYL + GREY)
d.node("bgr", "Ephemeral Runner", 920, 80, 360, 300, BG)
d.node("rc", "Runner container\n(no skills baked in)", 950, 130, 300, 50, BOX + YELLOW)
d.node("mb", "Mounted skill bundle\n(from registry)", 950, 210, 300, 50, BOX + PURPLE)
d.node("ag", "Agents use\nmounted skills", 950, 290, 300, 50, BOX + GREEN)
d.node("art", "Skill Artifact\n(output)", 1310, 280, 130, 70, DOC + PURPLE)
d.node("note", "1. Orchestrator asks skill-loader: prepare runtime(skill_key)\n2. skill-loader resolves skills via knowledge + Langfuse\n3. skill-loader asks sandbox-provisioner to spawn runner\n4. skill-loader mounts centralized skill bundle onto runner\n5. Agents on runner execute using mounted skills\n6. Phase produces skill artifact → job-service", 40, 470, 560, 130, NOTE)
d.edge("e1", "job", "orch", "run phase", exit_at=(1, .5), entry_at=(0, .5), lx=200, ly=130)
d.edge("e2", "orch", "loader", "prepare runtime", exit_at=(1, .5), entry_at=(0, .5), lx=420, ly=130)
d.edge("e3", "loader", "know", "resolve skills", exit_at=(.5, 1), entry_at=(.5, 0), lx=540, ly=220)
d.edge("e4", "know", "lf", "prod prompts", exit_at=(1, .5), entry_at=(0, .5), lx=655, ly=270)
d.edge("e5", "loader", "prov", "spawn runner", exit_at=(1, .5), entry_at=(0, .5), lx=655, ly=130)
d.edge("e6", "prov", "rc", "create", exit_at=(1, .5), entry_at=(0, .5), lx=890, ly=140)
d.edge("e7", "loader", "mb", "mount skill bundle", color="#9673a6",
       exit_at=(.75, 1), entry_at=(0, .5), points=[(580, 235), (580, 235)], lx=770, ly=222)
d.edge("e8", "orch", "ag", "agents execute using mounted skills", dashed=True,
       exit_at=(.5, 1), entry_at=(0, .5), points=[(305, 330), (890, 330), (890, 315)], lx=600, ly=330)
d.edge("e9", "ag", "art", "emit artifact", exit_at=(1, .5), entry_at=(0, .5), lx=1285, ly=300)
d.edge("e10", "art", "job", "artifact → job-service", dashed=True,
       exit_at=(.5, 1), entry_at=(.5, 1), points=[(1375, 420), (105, 420)], lx=740, ly=420)
d.write(DOCS / "05-execution-runners.drawio")

# ---------------------------------------------------------------- 06
d = D("af-wiz", "Guided Wizard", 1160, 660)
d.node("title", "Agentic Framework — Guided Wizard (Skill 1: Research) — Interactive", 130, 10, 900, 40, TITLE)
d.node("u", "User opens an\nengagement", 40, 120, 130, 70, "ellipse;whiteSpace=wrap;html=1;fontSize=11;fontStyle=1;" + BLUE)
d.node("ui", "Web UI\nGuided wizard steps", 230, 120, 150, 70, BOX + BLUE)
d.node("gw", "gateway\n+ SSE", 440, 120, 130, 70, BOX + YELLOW)
d.node("orch", "agent-orchestrator\n+ Research skill\n(mounted)", 630, 110, 170, 90, BOX + GREEN)
d.node("rn", "Research runner\nlive enrich (optional)", 860, 120, 160, 70, BOX + YELLOW)
d.node("bgw", "Wizard collaboration", 230, 300, 660, 150, BG)
d.node("w1", "1. Confirm scope\n& stakeholders", 260, 360, 140, 60, BOX + BLUE)
d.node("w2", "2. Gather context\n& dependencies", 420, 360, 140, 60, BOX + BLUE)
d.node("w3", "3. Review inputs\n& constraints", 580, 360, 140, 60, BOX + BLUE)
d.node("w4", "4. User confirms\nfindings", 740, 360, 140, 60, BOX + GREEN)
d.node("art", "Research Findings\nArtifact", 950, 350, 150, 80, DOC + PURPLE)
d.node("note", "Not a silent batch pull — user and agent collaborate.\nLangGraph checkpoints wizard progress; UI gets SSE updates.", 230, 510, 460, 60, NOTE)
d.edge("e1", "u", "ui", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e2", "ui", "gw", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e3", "gw", "orch", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e4", "orch", "rn", dashed=True, exit_at=(1, .5), entry_at=(0, .5))
d.edge("e5", "orch", "w1", "drives steps", dashed=True,
       exit_at=(.5, 1), entry_at=(.5, 0), points=[(715, 270), (330, 270)], lx=520, ly=270)
d.edge("e6", "w1", "w2", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e7", "w2", "w3", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e8", "w3", "w4", exit_at=(1, .5), entry_at=(0, .5))
d.edge("e9", "w4", "art", exit_at=(1, .5), entry_at=(0, .5))
d.write(DOCS / "06-discovery-wizard.drawio")

# ---------------------------------------------------------------- 10
d = D("af-layers", "Logical Layers", 1240, 580)
d.node("title", "Agentic Framework — Logical Layers & Frameworks", 170, 10, 900, 40, TITLE)
d.node("c1", "Connectivity Layer\nweb · mcp · cli · gateway\n(+ adaption email outbound)", 40, 90, 220, 90, BOX + BLUE)
d.node("c3", "Orchestrator Framework\njob-service\nagent-orchestrator\nLangGraph + Deep Agents", 340, 90, 220, 90, BOX + GREEN)
d.node("c4", "Execution Framework\nsandbox-provisioner\nephemeral runners\nskill-loader (mount)", 640, 90, 220, 90, BOX + YELLOW)
d.node("c2", "Context Layer\nknowledge-service\nLangfuse skills\nPostgres memory", 340, 250, 220, 90, BOX + PURPLE)
d.node("c5", "Evaluation Framework\nLangfuse traces\nfinops-engine\nvalidation hooks", 640, 390, 280, 90, BOX + ORANGE)
d.node("mapnote", "Physical platforms\nAccess ← Connectivity\nSkill & Knowledge ← Context\nExecution ← Orchestrator + Execution + Evaluation\nAdaption Engine spans Connectivity (email) + job events", 40, 250, 260, 130, NOTE)
d.node("n10", "Layers = logical separation of concerns.\nMicroservices map to layers (see catalogue).", 40, 420, 260, 60, NOTE)
d.edge("e1", "c1", "c3", "jobs / SSE", exit_at=(1, .5), entry_at=(0, .5), lx=300, ly=125)
d.edge("e2", "c3", "c2", "load context", exit_at=(.5, 1), entry_at=(.5, 0), lx=450, ly=215)
d.edge("e3", "c3", "c4", "run phases", exit_at=(1, .5), entry_at=(0, .5), lx=600, ly=125)
d.edge("e4", "c4", "c2", "via skill-loader", dashed=True,
       exit_at=(.3, 1), entry_at=(1, .5), points=[(706, 295)], lx=640, ly=295)
d.edge("e5", "c3", "c5", "traces", dashed=True,
       exit_at=(1, .8), entry_at=(0, .5), points=[(600, 162), (600, 435)], lx=600, ly=360)
d.edge("e6", "c4", "c5", "cost + traces", dashed=True,
       exit_at=(.5, 1), entry_at=(.5, 0), lx=750, ly=300)
d.write(DOCS / "10-logical-fabrics.drawio")
