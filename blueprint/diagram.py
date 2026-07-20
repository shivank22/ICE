#!/usr/bin/env python3
"""Render the Vanilla Agentic Framework diagrams as icon-based PNGs.

Outputs:
    architecture.png  - layered architecture with Azure service icons
    pipeline.png      - skill pipeline / artifact flow

Run:
    python3 diagram.py
"""
from diagrams import Cluster, Diagram, Edge
from diagrams.azure.compute import ContainerInstances, KubernetesServices
from diagrams.azure.database import DatabaseForPostgresqlServers
from diagrams.azure.general import CostManagement, Files
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.integration import APIManagement, LogicApps, ServiceBus
from diagrams.azure.ml import CognitiveServices
from diagrams.azure.monitor import LogAnalyticsWorkspaces
from diagrams.azure.network import ApplicationGateway
from diagrams.azure.web import AppServices
from diagrams.onprem.client import Users
from diagrams.programming.framework import React

GRAPH_ATTR = {
    "fontsize": "22",
    "bgcolor": "white",
    "pad": "0.4",
    "splines": "spline",
    "nodesep": "0.6",
    "ranksep": "0.8",
}

with Diagram(
    "Vanilla Agentic Framework - Layered Architecture",
    filename="architecture",
    outformat="png",
    show=False,
    direction="LR",
    graph_attr=GRAPH_ATTR,
):
    users = Users("Stakeholders\n& Platform Users")

    with Cluster("Access Layer"):
        web = React("Web (Guided Wizard)")
        gateway = ApplicationGateway("Gateway\n(Auth, RBAC, SSE)")
        entra = ActiveDirectory("Entra ID")

    with Cluster("Orchestration Layer"):
        job = AppServices("job-service")
        orch = AppServices("agent-orchestrator\n(LangGraph + Deep Agents)")

    with Cluster("Skill & Knowledge Layer"):
        knowledge = AppServices("knowledge-service")
        langfuse = CognitiveServices("Langfuse\n(skill prompts + traces)")
        pg = DatabaseForPostgresqlServers("Postgres + pgvector\n(semantic / episodic memory)")

    with Cluster("Execution Layer"):
        loader = APIManagement("skill-loader\n(central mount authority)")
        prov = KubernetesServices("sandbox-provisioner")
        runners = ContainerInstances("Ephemeral Runners")
        workspace = Files("Runner Workspace\n(artifacts)")

    with Cluster("Evaluation Layer"):
        finops = CostManagement("finops-engine")
        logs = LogAnalyticsWorkspaces("Traces & Logs")

    with Cluster("Engagement Layer"):
        adaption = LogicApps("adaption-engine\n(emails, SLA nudges)")
        bus = ServiceBus("Message Bus")

    users >> Edge(label="HTTPS") >> web >> gateway
    gateway >> Edge(label="auth") >> entra
    gateway >> Edge(label="jobs / SSE") >> job >> orch
    orch >> Edge(label="request mounts") >> loader
    loader >> Edge(label="resolve skills") >> knowledge
    knowledge >> langfuse
    knowledge >> pg
    loader >> Edge(label="spawn + mount") >> prov >> runners
    orch >> Edge(label="agents use mounted skills") >> runners
    runners >> Edge(label="write artifacts") >> workspace
    orch >> Edge(label="traces") >> logs
    logs >> Edge(label="usage + cost") >> finops
    job >> Edge(label="lifecycle events") >> bus >> adaption
    adaption >> Edge(label="email stakeholders") >> users

with Diagram(
    "Skill Pipeline - Artifacts to Final Deliverable Document",
    filename="pipeline",
    outformat="png",
    show=False,
    direction="LR",
    graph_attr=GRAPH_ATTR,
):
    owner = Users("User\n(Engagement ID)")

    with Cluster("Skill 1: Research"):
        s1 = ContainerInstances("Research Runner\n(guided wizard)")
        a1 = Files("Research\nFindings")

    with Cluster("Skill 2: Planning"):
        s2 = ContainerInstances("Planning\nRunner")
        a2 = Files("Plan &\nRecommendation")

    hitl = Users("HITL Approval")

    with Cluster("Skill 3: Execution"):
        s3 = ContainerInstances("Execution Runner")
        a3 = Files("Execution\nReport")

    with Cluster("Skill 4: Reporting"):
        s4 = ContainerInstances("Reporting Runner")
        a4 = Files("Summary\nArtifact")

    add = Files("Final Deliverable\nDocument")
    finops = CostManagement("finops-engine\n(cost per run)")
    adaption = LogicApps("adaption-engine\n(stakeholder updates)")

    owner >> s1 >> a1 >> s2 >> a2 >> Edge(label="approve / revise") >> hitl
    hitl >> s3 >> a3 >> s4 >> a4 >> add
    s2 >> Edge(style="dashed", label="cost") >> finops
    s4 >> Edge(style="dashed", label="cost") >> finops
    add >> Edge(style="dashed", label="notify") >> adaption
