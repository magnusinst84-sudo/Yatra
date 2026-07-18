# Yatra - Historical & Heritage Explorer

Yatra is a premium, cinematic web application that allows users to explore rich historical timelines and heritage destinations across India and the ancient world. With an immersive "Cinema Grid" aesthetic, custom animations, and a curated dark/antique color palette, it offers users an immersive journey through time.

## 🌟 Key Features

- **Interactive Historical Timeline Slider:** Immersive auto-advancing slideshow of key destinations (such as Ayodhya, Jaipur, Pune, Varanasi, and Vijayanagar) with custom slide-up/fade animations.
- **Cinematic Overlays & Radial Gradients:** Custom styling with custom HSL tailored colors (`antiqueGold`, `darkBg`, and `lightGray`) and ambient visual glow effects.
- **Timeline Filtering & Search:** A glassmorphism search and filter form panel for historical places and eras.
- **Walkthrough Logs & History:** A timeline of past walkthrough coordinates and historical logs, along with native web-sharing options.
- **Firebase Auth (Google OAuth):** Pre-configured integration for user authentication using Google Sign-In.
- **Immersive Visual Elements:** Interactive floating elements (antique compass, globe, etc.) that leverage keyframe animations.

## 🛠️ Technology Stack

- **Framework:** [React 18](https://react.dev/)
- **Build System:** [Vite](https://vite.dev/)
- **Language:** JavaScript & TypeScript
- **Styling:** [Tailwind CSS v3](https://tailwindcss.com/) & PostCSS
- **Authentication:** [Firebase Auth SDK](https://firebase.google.com/)

## 📁 File Structure

Below is an overview of the key directories and files within the `frontend` folder:

*   **`src/`**
    *   `App.jsx`: Main routing logic controlling the page transitions (Home ↔ History).
    *   `main.jsx`: Application entry point.
    *   `index.css`: Global styles, custom keyframes, and custom Tailwind configurations.
    *   **`components/`**
        *   `Navbar.jsx`: Immersive top navigation bar with user sign-in status.
    *   **`pages/`**
        *   `Home.jsx`: Main dashboard showcasing destinations, search tools, and sliders.
        *   `History.jsx`: History timeline listing interactive logs and shared places.
    *   **`services/`**
        *   `firebase.js`: Firebase integration, helper utilities for Google Sign-In and logout.
        *   `api.js`: Service file placeholder for backend API endpoints.
*   `tailwind.config.js`: Custom theme configuration incorporating fonts, custom animation timing, and golden theme accents.
*   `index.html`: Base HTML template configuration.

## 🚀 Getting Started

To run the application locally:

### 1. Prerequisites
Ensure you have [Node.js](https://nodejs.org/) installed (version 18+ recommended).

### 2. Install Dependencies
Run the following command in the `frontend` directory:
```bash
npm install
```

### 3. Environment Variables Setup
Create a `.env` file in the `frontend` directory and define your Firebase config parameters.
```env
VITE_FIREBASE_CONFIG='{"apiKey": "YOUR_API_KEY", "authDomain": "YOUR_AUTH_DOMAIN", "projectId": "YOUR_PROJECT_ID", "storageBucket": "YOUR_STORAGE_BUCKET", "messagingSenderId": "YOUR_MESSAGING_SENDER_ID", "appId": "YOUR_APP_ID"}'
```

### 4. Running the Development Server
Start the Vite development server:
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser to view the application.

### 5. Production Build
To build and optimize the application for production deployment:
```bash
npm run build
```
Preview the built site locally using:
```bash
npm run preview
```

## 📜 License
This project is private and proprietary.
