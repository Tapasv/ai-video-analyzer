import React, { useState, useRef } from 'react'
import axios from 'axios'
import {
  Box, Typography, Button, LinearProgress,
  Paper, Alert, Stack
} from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import VideoFileIcon from '@mui/icons-material/VideoFile'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export default function UploadSection({ onResults }) {
  // selectedFile stores the video file the user picks
  const [selectedFile, setSelectedFile] = useState(null)

  // loading is true while we're waiting for the backend to respond
  const [loading, setLoading] = useState(false)

  // progress tracks the upload % (0–100)
  const [progress, setProgress] = useState(0)

  // error stores any error message to show the user
  const [error, setError] = useState(null)

  // dragOver changes the UI when user drags a file over the drop zone
  const [dragOver, setDragOver] = useState(false)

  // fileInputRef lets us trigger the hidden file input when user clicks the box
  const fileInputRef = useRef(null)

  // Called when user selects a file through the file picker
  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
    }
  }

  // Called when user drops a file onto the drop zone
  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
    }
  }

  // Called when user clicks the Analyze button
  const handleUpload = async () => {
    if (!selectedFile) return

    // FormData is how we send files to a backend via HTTP
    const formData = new FormData()
    formData.append('video', selectedFile)  // "video" must match what Flask expects

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        // onUploadProgress lets us update the progress bar during upload
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          setProgress(percent)
        }
      })

      // Pass the results up to App.jsx so it can switch to the dashboard
      onResults(response.data)

    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      p: 3,
      background: 'radial-gradient(ellipse at top, #1a1f4e 0%, #0a0f1e 70%)'
    }}>
      {/* Page heading */}
      <Typography variant="h3" fontWeight={700} textAlign="center" mb={1}
        sx={{ background: 'linear-gradient(90deg, #6366f1, #22d3ee)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
        AI Interview Analyzer
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" mb={5} textAlign="center">
        Upload your interview video and get instant AI-powered feedback
      </Typography>

      {/* Drag & drop upload box */}
      <Paper
        elevation={4}
        onClick={() => fileInputRef.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        sx={{
          width: '100%',
          maxWidth: 520,
          p: 6,
          textAlign: 'center',
          cursor: 'pointer',
          border: `2px dashed ${dragOver ? '#6366f1' : '#2a2f4e'}`,
          background: dragOver ? 'rgba(99,102,241,0.08)' : 'background.paper',
          transition: 'all 0.2s ease',
          '&:hover': { borderColor: '#6366f1', background: 'rgba(99,102,241,0.05)' }
        }}
      >
        {/* Hidden file input — we trigger it via the ref */}
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          accept="video/*"
          onChange={handleFileChange}
        />

        {selectedFile ? (
          <Stack alignItems="center" spacing={1}>
            <VideoFileIcon sx={{ fontSize: 52, color: '#6366f1' }} />
            <Typography fontWeight={600}>{selectedFile.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {(selectedFile.size / (1024 * 1024)).toFixed(1)} MB
            </Typography>
          </Stack>
        ) : (
          <Stack alignItems="center" spacing={1}>
            <CloudUploadIcon sx={{ fontSize: 52, color: 'text.secondary' }} />
            <Typography fontWeight={600}>Drop your video here</Typography>
            <Typography variant="body2" color="text.secondary">
              or click to browse — MP4, MOV, AVI, WebM
            </Typography>
          </Stack>
        )}
      </Paper>

      {/* Show error message if something went wrong */}
      {error && (
        <Alert severity="error" sx={{ mt: 2, maxWidth: 520, width: '100%' }}>
          {error}
        </Alert>
      )}

      {/* Progress bar during upload/analysis */}
      {loading && (
        <Box sx={{ width: '100%', maxWidth: 520, mt: 3 }}>
          <Typography variant="body2" color="text.secondary" mb={1} textAlign="center">
            {progress < 100 ? `Uploading... ${progress}%` : 'Analyzing your interview — this may take a minute...'}
          </Typography>
          <LinearProgress
            variant={progress < 100 ? 'determinate' : 'indeterminate'}
            value={progress}
            sx={{ borderRadius: 2, height: 8 }}
          />
        </Box>
      )}

      {/* Analyze button */}
      {!loading && (
        <Button
          variant="contained"
          size="large"
          disabled={!selectedFile}
          onClick={handleUpload}
          sx={{ mt: 3, px: 6, py: 1.5, fontWeight: 700, fontSize: '1rem', borderRadius: 3 }}
        >
          Analyze Interview
        </Button>
      )}
    </Box>
  )
}