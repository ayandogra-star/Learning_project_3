# Frontend Setup

Modern React frontend for the PDF Processing application, built with Vite and styled with Tailwind CSS.

## Prerequisites

- Node.js 16+ and npm

## Installation & Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file (or use the provided `.env` template):
   ```env
   VITE_API_URL=http://localhost:8000
   ```

## Running the Frontend

From the frontend directory:

```bash
npm run dev
```

The development server will start at http://localhost:5173 and automatically open in your browser.

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

## Preview Production Build

```bash
npm run preview
```

## Features

- 🎨 **Modern UI** - Built with Tailwind CSS for a clean, responsive design
- ⚡ **Fast Development** - Vite provides instant HMR (Hot Module Replacement)
- 📱 **Responsive** - Works seamlessly on desktop, tablet, and mobile
- 📊 **Charts** - Real-time data visualization with Recharts
- 🎯 **Component-Based** - Modular React components for easy maintenance
- ♿ **Accessible** - Built with accessibility best practices

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── LandingPage.jsx       # Home page with upload button
│   │   ├── UploadForm.jsx        # File upload with progress
│   │   └── Dashboard.jsx         # Analytics dashboard
│   ├── services/
│   │   └── api.js                # API client
│   ├── App.jsx                   # Main app component
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles
├── package.json
├── vite.config.js
├── tailwind.config.js
└── index.html
```

## Technologies Used

- **React 18** - UI library with modern hooks
- **Vite** - Next generation frontend tooling
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Recharts** - Data visualization library
- **Axios** - HTTP client

## Environment Variables

- `VITE_API_URL` - Backend API base URL (default: http://localhost:8000)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
