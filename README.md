<div align="center">

# ⚡ ScaleFlow
### Distributed Task Execution Engine

A production-grade distributed task orchestration system built for horizontal scalability, automatic load balancing, and fault tolerance.

![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61dafb?style=for-the-badge&logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ed?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)



</div>

---

## 📖 About The Project

**ScaleFlow** is a robust engine designed to handle heavy background processing loads. Unlike simple cron jobs, ScaleFlow distributes tasks across multiple containerized worker nodes, ensuring that your application remains responsive even under heavy load. It features a real-time React dashboard for monitoring queue depths, worker health, and task throughput.

## ✨ Key Features

* **🌐 Distributed Architecture** — Seamlessly scale horizontally by adding more worker nodes.
* **📨 FIFO Message Queue** — Reliable Redis-based queuing guarantees task ordering.
* **💾 Persistent State** — PostgreSQL ensures no task data is lost, even during crashes.
* **📊 Real-time Monitoring** — Live dashboard built with React & Recharts.
* **🛡️ Fault Tolerance** — Automatic retries and "dead letter" handling.
* **🐳 Container Native** — Fully orchestrated with Docker Compose.

---

## 🛠️ Tech Stack

ScaleFlow is built using modern, industry-standard technologies to ensure reliability and performance.

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) | Lightweight WSGI web application framework |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white) | Primary relational database for task storage |
| **Queue** | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white) | In-memory data structure store for message brokering |
| **Frontend** | ![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB) | Dynamic user interface for the monitoring dashboard |
| **DevOps** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) | Containerization for consistent development/production envs |
| **ORM** | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white) | Python SQL toolkit and Object Relational Mapper |

---

## 🏗️ System Architecture

The system utilizes a producer-consumer model where the API produces tasks and multiple worker nodes consume them concurrently.

```text
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │─────▶│  Flask API   │─────▶│ PostgreSQL  │
│ UI (React)  │      │  (Producer)  │      │ (Persistence)│
└─────────────┘      └──────┬───────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Redis Queue  │
                     │  (Broker)    │
                     └──────┬───────┘
                            │
             ┌──────────────┼─────────────┐
             ▼              ▼             ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │ Worker 1│    │ Worker 2│    │ Worker 3│
        └─────────┘    └─────────┘    └─────────┘
