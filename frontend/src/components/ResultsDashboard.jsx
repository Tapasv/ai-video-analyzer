import React from 'react'
import {
  Box, Typography, Button, Grid, Paper,
  Stack, Chip, Divider, Container
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer, Tooltip
} from 'recharts'
import ScoreCard from './ScoreCard'
import FeedbackPanel from './FeedbackPanel'

// Grade colors — each letter grade gets its own color
const gradeColors = {
  A: '#22c55e',   // Green
  B: '#6366f1',   // Indigo
  C: '#f59e0b',   // Amber
  D: '#f97316',   // Orange
  F: '#ef4444'    // Red
}

// This is the main results page shown after analysis is complete
// Props:
//   results — the full JSON response from the backend
//   onReset — function to go back to the upload screen
export default function ResultsDashboard({ results, onReset }) {
  const { transcript, sentiment, emotion, clarity, score } = results

  // Build the data array for the Radar (spider) chart
  // Each entry needs a "subject" (label) and "score" (value)
  const radarData = [
    { subject: 'Sentiment', score: score.breakdown.sentiment_score },
    { subject: 'Emotion',   score: score.breakdown.emotion_score },
    { subject: 'Clarity',   score: score.breakdown.clarity_score },
  ]

  const gradeColor = gradeColors[score.grade] || '#6366f1'

  return (
    <Box sx={{
      minHeight: '100vh',
      background: 'radial-gradient(ellipse at top, #1a1f4e 0%, #0a0f1e 70%)',
      py: 5
    }}>
      <Container maxWidth="lg">

        {/* ── HEADER ─────────────────────────────────────────── */}
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography variant="h4" fontWeight={700}
            sx={{ background: 'linear-gradient(90deg, #6366f1, #22d3ee)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Interview Analysis
          </Typography>
          <Button
            startIcon={<RefreshIcon />}
            variant="outlined"
            onClick={onReset}
            sx={{ borderRadius: 3 }}
          >
            Analyze Another
          </Button>
        </Stack>

        {/* ── OVERALL SCORE BANNER ───────────────────────────── */}
        <Paper elevation={6} sx={{
          p: 4, mb: 4, borderRadius: 4,
          background: `linear-gradient(135deg, #141929, ${gradeColor}22)`,
          border: `1px solid ${gradeColor}44`
        }}>
          <Stack direction={{ xs: 'column', md: 'row' }} alignItems="center" spacing={3}>
            <EmojiEventsIcon sx={{ fontSize: 56, color: gradeColor }} />
            <Box flex={1}>
              <Stack direction="row" alignItems="center" spacing={2} mb={1}>
                <Typography variant="h2" fontWeight={800} sx={{ color: gradeColor }}>
                  {score.final_score}
                </Typography>
                <Typography variant="h4" color="text.secondary">/100</Typography>
                <Chip
                  label={`Grade: ${score.grade} — ${score.grade_label}`}
                  sx={{ background: gradeColor, color: '#fff', fontWeight: 700, fontSize: '1rem', px: 1 }}
                />
              </Stack>
              <Typography variant="h6" color="text.secondary">
                {score.overall_feedback}
              </Typography>
            </Box>
          </Stack>
        </Paper>

        {/* ── SCORE CARDS + RADAR CHART ──────────────────────── */}
        <Grid container spacing={3} mb={4}>

          {/* Individual score cards */}
          <Grid item xs={12} md={4}>
            <Stack spacing={2}>
              <ScoreCard label="Sentiment Score" score={score.breakdown.sentiment_score} color="#22d3ee" />
              <ScoreCard label="Emotion Score"   score={score.breakdown.emotion_score}   color="#f59e0b" />
              <ScoreCard label="Clarity Score"   score={score.breakdown.clarity_score}   color="#6366f1" />
            </Stack>
          </Grid>

          {/* Radar chart showing all 3 scores visually */}
          <Grid item xs={12} md={8}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 3, background: '#141929', height: '100%' }}>
              <Typography variant="h6" fontWeight={600} mb={2}>Score Breakdown</Typography>
              <ResponsiveContainer width="100%" height={280}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#2a2f4e" />
                  {/* Labels around the outside of the chart */}
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 13 }} />
                  {/* Radial scale from 0 to 100 */}
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
                  {/* The actual filled area */}
                  <Radar name="Score" dataKey="score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.35} />
                  <Tooltip
                    contentStyle={{ background: '#1e2438', border: 'none', borderRadius: 8 }}
                    formatter={(value) => [`${value}/100`, 'Score']}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>

        {/* ── DETAILED FEEDBACK + TRANSCRIPT ─────────────────── */}
        <Grid container spacing={3}>

          {/* Left: detailed feedback for each category */}
          <Grid item xs={12} md={7}>
            <Typography variant="h6" fontWeight={600} mb={2}>Detailed Feedback</Typography>
            <FeedbackPanel sentiment={sentiment} emotion={emotion} clarity={clarity} />
          </Grid>

          {/* Right: transcript of what was said */}
          <Grid item xs={12} md={5}>
            <Typography variant="h6" fontWeight={600} mb={2}>Transcript</Typography>
            <Paper elevation={3} sx={{
              p: 3, borderRadius: 3, background: '#141929',
              maxHeight: 500, overflowY: 'auto'
            }}>
              <Typography variant="body2" color="text.secondary" lineHeight={1.9}>
                {transcript || 'No speech detected.'}
              </Typography>
            </Paper>

            {/* Quick stats below the transcript */}
            <Paper elevation={3} sx={{ p: 3, borderRadius: 3, background: '#141929', mt: 2 }}>
              <Typography variant="subtitle2" fontWeight={600} mb={2}>Quick Stats</Typography>
              <Divider sx={{ mb: 2 }} />
              <Stack spacing={1}>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Total Words</Typography>
                  <Typography variant="body2" fontWeight={600}>{clarity.word_count}</Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Speaking Pace</Typography>
                  <Typography variant="body2" fontWeight={600}>{clarity.words_per_minute} WPM</Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Filler Words</Typography>
                  <Typography variant="body2" fontWeight={600}>{clarity.total_fillers}</Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Long Pauses</Typography>
                  <Typography variant="body2" fontWeight={600}>{clarity.long_pauses}</Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Dominant Emotion</Typography>
                  <Typography variant="body2" fontWeight={600} sx={{ textTransform: 'capitalize' }}>
                    {emotion.dominant_emotion}
                  </Typography>
                </Stack>
              </Stack>
            </Paper>
          </Grid>
        </Grid>

      </Container>
    </Box>
  )
}