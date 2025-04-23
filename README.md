# Delegation Management System

A comprehensive web application designed to simplify and automate the management of corporate business-travel delegations. Built with Python and Flask, this system offers role-based access control, real-time notifications, and a fully documented database schema and UML diagrams for easy maintenance and future extension.

---

## Table of Contents

1. Introduction
2. Features
3. Technology Stack
4. Usage
5. Entity-Relationship Diagram
6. UML - Use Case Diagram
7. Future Work

---

## Introduction

In a modern corporate environment, efficient delegation management is critical. This project delivers a **Delegation Management System** that:

- Centralizes business-trip planning and approvals
- Automates notifications and audit logging
- Provides digital transformation to reduce manual overhead
- Supports distinct user roles: **Administrator**, **Manager**, and **Employee**

The application is backed by a relational SQLite database and features a responsive Flask-based web interface.

---

## Features

- **Role-Based Access Control**: Secure login and permissions for Administrators, Managers, and Employees
- **Delegation Lifecycle Management**: Create, view, modify, cancel, and delete delegations
- **Participant Assignment**: Managers assign employees to delegations; employees can accept or decline
- **Delegation Requests**: Employees request new delegations or joining existing ones
- **Notifications**: Real-time alerts for delegation events and assignment changes
- **Audit Trail**: All actions logged for accountability and compliance

---


## Technology Stack

- **Language**: Python 3.10+
- **Web Framework**: Flask 3.1+
- **Database**: SQLite v3.39.0+
- **Frontend**: HTML5, CSS3, Bootstrap (optional)
- **Development Environment**: PyCharm Professional 2023.1+

---

## Usage

1. **Register or log in** as Administrator, Manager, or Employee.
2. **Manager Dashboard**: Create or edit delegations, assign participants, manage transport and schedule.
3. **Employee Dashboard**: View assigned delegations, accept/decline requests, submit new delegation requests.
4. **Notifications**: Check real-time alerts for assignment changes and cancellations.
5. **Audit Logs**: Administrators can review all delegation events and user actions.

---

## Entity-Relationship Diagram

![obraz](https://github.com/user-attachments/assets/1e17ca7f-267b-4c93-9adb-7070fe514596)


---

## UML - Use Case Diagram

![obraz](https://github.com/user-attachments/assets/b5449595-fd28-4804-9fe3-bffbb664fefa)


---

## Future Work

- Integrate with external travel booking APIs
- Role-based dashboards with analytics
- Advanced reporting and export to PDF/Excel
- Multi-language support and mobile-friendly UI

