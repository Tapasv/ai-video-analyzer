import React from 'react'
import { Paper, Typography, Stack, Chip, Divider, Box } from '@mui/material'
import RecordVoiceOverIcon from '@mui/icons-material/RecordVoiceOver'
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt'
import FaceIcon from '@mui/icons-material/Face'
import SpeedIcon from '@mui/icons-material/Speed'

// This component shows detailed written feedback for each category:
// Sentiment, Emotion, Clarity (pace, fillers, pauses)
// Props:
//   sentiment — sentiment result object from backend
//   emotion   — emotion result object from backend
//   clarity   — clarity result object from backend

export default function FeedbackPanel({ sentiment, emotion, clarity }) {
  return (
    <Stack spacing={3}>

      {/* ── SENTIMENT FEEDBACK ─────────────────────────────── */}
      <Paper elevation={3} sx={{ p: 3, borderRadius: 3, background: '#141929' }}>
        <Stack direction="row" alignItems="center" spacing={1} mb={2}>
          <SentimentSatisfiedAltIcon sx={{ color: '#22d3ee' }} />
          <Typography variant="h6" fontWeight={600}>Tone & Sentiment</Typography>
        </Stack>

        <Stack direction="row" spacing={1} mb={2} flexWrap="wrap">
          {/* Show whether tone was positive or negative as a colored chip */}
          <Chip
            label={sentiment.label}
            color={sentiment.label === 'POSITIVE' ? 'success' : 'error'}
            size="small"
          />
          <Chip label={`Confidence: ${sentiment.score}%`} size="small" variant="outlined" />
        </Stack>

        <Typography variant="body2" color="text.secondary">
          {sentiment.summary}
        </Typography>
      </Paper>

      {/* ── EMOTION FEEDBACK ───────────────────────────────── */}
      <Paper elevation={3} sx={{ p: 3, borderRadius: 3, background: '#141929' }}>
        <Stack direction="row" alignItems="center" spacing={1} mb={2}>
          <FaceIcon sx={{ color: '#f59e0b' }} />
          <Typography variant="h6" fontWeight={600}>Facial Expression</Typography>
        </Stack>

        {/* Dominant emotion shown as a big chip */}
        <Chip
          label={`Dominant: ${emotion.dominant_emotion.toUpperCase()}`}
          color="warning"
          size="small"
          sx={{ mb: 2 }}
        />

        <Typography variant="body2" color="text.secondary" mb={2}>
          {emotion.summary}
        </Typography>

        <Divider sx={{ mb: 2 }} />

        {/* Emotion breakdown — show each emotion and its percentage */}
        <Typography variant="caption" color="text.secondary" fontWeight={600} textTransform="uppercase">
          Emotion Breakdown
        </Typography>
        <Stack spacing={1} mt={1}>
          {Object.entries(emotion.emotion_breakdown).map(([emo, pct]) => (
            <Box key={emo}>
              <Stack direction="row" justifyContent="space-between" mb={0.5}>
                <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>{emo}</Typography>
                <Typography variant="body2" color="text.secondary">{pct}%</Typography>
              </Stack>
              {/* Visual bar showing the percentage */}
              <Box sx={{ height: 6, borderRadius: 3, background: '#2a2f4e', overflow: 'hidden' }}>
                <Box sx={{
                  height: '100%',
                  width: `${pct}%`,
                  background: 'linear-gradient(90deg, #f59e0b, #ef4444)',
                  borderRadius: 3,
                  transition: 'width 1s ease'
                }} />
              </Box>
            </Box>
          ))}
        </Stack>
      </Paper>

      {/* ── CLARITY FEEDBACK ───────────────────────────────── */}
      <Paper elevation={3} sx={{ p: 3, borderRadius: 3, background: '#141929' }}>
        <Stack direction="row" alignItems="center" spacing={1} mb={2}>
          <RecordVoiceOverIcon sx={{ color: '#6366f1' }} />
          <Typography variant="h6" fontWeight={600}>Speaking Clarity</Typography>
        </Stack>

        {/* Speaking pace */}
        <Stack direction="row" alignItems="center" spacing={1} mb={1}>
          <SpeedIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
          <Typography variant="body2" fontWeight={600}>
            Speaking Pace: {clarity.words_per_minute} WPM
          </Typography>
        </Stack>
        <Typography variant="body2" color="text.secondary" mb={2}>
          {clarity.pace_feedback}
        </Typography>

        <Divider sx={{ mb: 2 }} />

        {/* Filler words */}
        <Typography variant="body2" fontWeight={600} mb={1}>
          Filler Words: {clarity.total_fillers} detected
        </Typography>
        <Typography variant="body2" color="text.secondary" mb={1}>
          {clarity.filler_feedback}
        </Typography>

        {/* Show chips for each filler word found */}
        {Object.keys(clarity.filler_words).length > 0 && (
          <Stack direction="row" flexWrap="wrap" gap={1} mb={2}>
            {Object.entries(clarity.filler_words).map(([word, count]) => (
              <Chip
                key={word}
                label={`"${word}" × ${count}`}
                size="small"
                color="error"
                variant="outlined"
              />
            ))}
          </Stack>
        )}

        <Divider sx={{ mb: 2 }} />

        {/* Pauses */}
        <Typography variant="body2" fontWeight={600} mb={1}>
          Long Pauses: {clarity.long_pauses} detected
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {clarity.pause_feedback}
        </Typography>
      </Paper>

    </Stack>
  )
}