import React from 'react'
import { Box, Typography, CircularProgress, Paper } from '@mui/material'

// A reusable component that shows a circular score gauge with a label
// Props:
//   label  — the title above the gauge (e.g. "Overall Score")
//   score  — a number from 0 to 100
//   color  — the color of the circle ring
export default function ScoreCard({ label, score, color = '#6366f1' }) {
  return (
    <Paper elevation={3} sx={{ p: 3, textAlign: 'center', borderRadius: 3, background: '#141929' }}>
      <Typography variant="subtitle2" color="text.secondary" mb={2} fontWeight={600} textTransform="uppercase" letterSpacing={1}>
        {label}
      </Typography>

      {/* Box with "relative" position so we can layer the score number on top of the circle */}
      <Box sx={{ position: 'relative', display: 'inline-flex' }}>

        {/* Grey background circle — always full 100% so it looks like a track */}
        <CircularProgress
          variant="determinate"
          value={100}
          size={100}
          thickness={4}
          sx={{ color: '#2a2f4e', position: 'absolute', top: 0, left: 0 }}
        />

        {/* Colored foreground circle — fills based on score */}
        <CircularProgress
          variant="determinate"
          value={score}
          size={100}
          thickness={4}
          sx={{ color: color }}
        />

        {/* Score number centered inside the circle */}
        <Box sx={{
          top: 0, left: 0, bottom: 0, right: 0,
          position: 'absolute',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Typography variant="h5" fontWeight={700} color="white">
            {score}
          </Typography>
        </Box>
      </Box>
    </Paper>
  )
}