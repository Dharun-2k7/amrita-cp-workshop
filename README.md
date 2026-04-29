# IOI Vismaya Workshop Platform

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supported-blue.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

A scalable, production-ready, and visually engaging full-stack web application built for class 9-12th students taking part in the IOI Vismaya Workshop conducted by the Amrita Vishwa Vidyapeetham ICPC club. This platform is designed to host competitive programming workshops, manage users, and run live coding contests with real-time leaderboards.

## ✨ Features

*   **Modern User Interface:** A dynamic, "Cyber/Neon" aesthetic featuring responsive card layouts, borderless timeline designs, and 3D tilt effects for an engaging user experience.
*   **Secure Authentication System:**
    *   User Registration with Email OTP Verification.
    *   Secure Login & Password Reset capabilities.
    *   Role-Based Access Control (Users vs. Administrators).
*   **Competitive Problem Engine:**
    *   Live problem dashboard where users can submit answers.
    *   Scheduled problem releases.
    *   Automated correctness checking and point distribution.
    *   Archives section for past problems.
*   **Real-time Leaderboard:** Dynamically ranks users based on points accumulated and fastest solve times.
*   **Admin Dashboard:**
    *   Manage active and scheduled problems.
    *   Create, edit, and toggle problem visibility.
    *   Manage administrative privileges (Grant/Revoke admins), with safeguards for the primary owner.

## 🚀 Tech Stack

*   **Backend:** Python, Flask
*   **Database:** PostgreSQL (Primary production database), SQLAlchemy (ORM)
*   **Authentication:** Flask-Login, Flask-Bcrypt
*   **Frontend:** HTML5, Vanilla CSS (Modern UI/UX design), JavaScript (Micro-animations, Tilt effects)
*   **Deployment:** Optimized for Serverless deployment on Vercel.

## 🛠️ Local Development Setup

### Prerequisites

*   Python 3.9 or higher
*   pip (Python package manager)
*   Git
*   PostgreSQL installed locally (or access to a cloud PostgreSQL instance)

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/amrita-cp-workshop.git
    cd amrita-cp-workshop
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add the following:
    ```env
    SECRET_KEY=your_super_secret_key_here
    POSTGRES_URL=postgresql://username:password@localhost:5432/vismaya_db
    
    # Email Configuration for OTP Verification
    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME=your_email@gmail.com
    MAIL_PASSWORD=your_app_password
    MOCK_EMAIL=False # Set to True to skip sending real emails during dev
    
    # Admin Setup
    ADMIN_EMAIL=your_admin_email@example.com
    ```

5.  **Initialize the Database:**
    ```bash
    python init_db.py
    ```

6.  **Run the Application:**
    ```bash
    python run.py
    ```
    The platform will be available at `http://127.0.0.1:5000`.

## 📖 Documentation

For a comprehensive guide on architecture, deployment, API routes, models, and end-to-end usage, please refer to the [DOCUMENTATION.md](./DOCUMENTATION.md) file included in this repository.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
