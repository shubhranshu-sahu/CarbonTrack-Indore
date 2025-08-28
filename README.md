# 🌱 MSME CarbonTrack

> **Track. Analyze. Reduce.**  
> Empowering MSMEs with digital tools to build a greener future.

---

## 🌍 What is CarbonTrack?

**MSME CarbonTrack** is a Flask-based web platform designed to help **Micro, Small, and Medium Enterprises (MSMEs)** in India **track, monitor, and reduce their carbon footprint**.

Many MSMEs operate in semi-urban or rural areas where digital awareness and environmental tracking tools are limited. CarbonTrack bridges this gap by offering an intuitive, AI-enhanced system to log carbon emissions, visualize usage patterns, and get smart suggestions — all aligned with government guidelines and thresholds.

---

## 🚨 Why CarbonTrack?

🔻 **The Problem**
- Lack of awareness and tools for tracking carbon emissions at the MSME level.
- Difficulty in staying within prescribed CO₂ emission limits.
- No affordable or user-friendly solution for monitoring emissions in real time.

✅ **Our Solution**
- A digital, mobile-friendly platform that empowers MSMEs to **log, view, and analyze** their carbon emissions.
- Integrated **AI suggestions** for actionable improvement.
- Auto-generated reports for internal use or compliance reporting.

---

## 🚀 Key Features

### ✅ 1. **Secure User Authentication & Business Profiling**
- Sign up with business details (MSME category, type, etc.).
- Data stored securely with password hashing (`passlib`).
- Configurable business profile to personalize insights.

---

### 📊 2. **Interactive Dashboard**
- Real-time emission summary: **monthly, yearly, all-time**.
- Emission vs. government limit with **color-coded progress bars**.
- Toggle between **monthly** and **yearly** views dynamically.

---

### 📋 3. **Carbon Emission Activity Logging**
- Add daily carbon-emitting activities:
  - Inputs: `Category`, `Sub-type`, `Value`, `Unit`, `Date`.
- Automatic calculation of CO₂ emission per activity.
- View logs in a table with:
  - Serial No., Category, Sub-type, Value, Emission, Date.
- Actions:
  - 📝 Edit via modal
  - 🗑️ Delete activity

---

### 📈 4. **Emission Summary with Graphs**
- **Pie Chart**: Category-wise CO₂ distribution.
- **Bar Chart**: Monthly/yearly comparison with dropdown selectors.
- **Line Chart**: Emission trends across time.
- **All graphs update dynamically without reloading** using JavaScript `fetch()`.

---

### 🤖 5. **AI-Powered Suggestions (Carbon Coach 🌱)**
- Clickable AI button styled as a card.
- Fetches **4 personalized tips** using AI (based on last 30 days’ emission data).
- Highlights the user's high-emission areas and gives practical MSME-friendly suggestions.

---

### 📄 6. **PDF Report Generation**
- Download beautiful, styled **PDF reports** with:
  - Emission totals and category-wise breakdown
  - Trend graphs and pie/bar charts
  - Custom date range selector

---

### 👤 7. **User Profile Page**
- Update business name, category, and type.
- Extendable fields for future analytics or sector-specific adjustments.

---

### 🧭 8. **Sidebar Navigation**
- Clean, collapsible **Bootstrap sidebar**.
- Icons for all sections with active highlighting.
- Responsive for mobile and tablet users.

---

## 🔧 Technologies Used

| Layer         | Technologies                                |
|---------------|---------------------------------------------|
| **Frontend**  | HTML5, CSS3, Bootstrap 5, JavaScript        |
| **Backend**   | Flask, Python, SQLAlchemy ORM               |
| **Database**  | MySQL (can use Railway, PlanetScale, etc.)  |
| **Charts**    | Chart.js                                    |
| **PDF Reports**| xhtml2pdf / WeasyPrint                     |
| **AI Integration** | OpenAI API / (HuggingFace optional fallback) |
| **Security**  | `passlib` for password hashing              |

---

## 📦 Folder Structure

