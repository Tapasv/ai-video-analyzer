import React, { useState } from 'react'
import { createTheme, ThemeProvider, CssBaseline } from '@mui/material'
import UploadSection from './components/UploadSection'
import ResultsDashboard from './components/ResultsDashboard'

// Create a custom dark theme using MUI's theming system
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1',      // Indigo — main buttons and accents
    },
    secondary: {
      main: '#22d3ee',      // Cyan — secondary highlights
    },
    background: {
      default: '#0a0f1e',   // Very dark navy — page background
      paper: '#141929',     // Slightly lighter — card backgrounds
    },
  },
  typography: {
    fontFamily: 'Inter, sans-serif',
  },
  shape: {
    borderRadius: 12,       // Rounded corners everywhere
  },
})

export default function App() {
  // "results" stores the analysis response from the backend
  // It starts as null — meaning no analysis has been done yet
  const [results, setResults] = useState(null)

  return (
    <ThemeProvider theme={theme}>
      {/* CssBaseline applies MUI's CSS reset so the app looks consistent */}
      <CssBaseline />

      {/* If there are no results yet, show the upload screen */}
      {/* Once the backend responds, switch to the results dashboard */}
      {!results
        ? <UploadSection onResults={setResults} />
        : <ResultsDashboard results={results} onReset={() => setResults(null)} />
      }
    </ThemeProvider>
  )
}