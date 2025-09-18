import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Container,
} from '@mui/material'
import {
  Home as HomeIcon,
  ArrowBack as ArrowBackIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'

const NotFound: React.FC = () => {
  const navigate = useNavigate()

  const handleGoHome = () => {
    navigate('/')
  }

  const handleGoBack = () => {
    navigate(-1)
  }

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          textAlign: 'center',
        }}
      >
        <Typography variant="h1" sx={{ fontSize: '6rem', fontWeight: 'bold', color: 'primary.main', mb: 2 }}>
          404
        </Typography>

        <Typography variant="h4" gutterBottom>
          Page Not Found
        </Typography>

        <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 400 }}>
          The page you're looking for doesn't exist or has been moved.
          Let's get you back on track.
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
          <Button
            variant="contained"
            startIcon={<HomeIcon />}
            onClick={handleGoHome}
            size="large"
          >
            Go to Dashboard
          </Button>

          <Button
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            onClick={handleGoBack}
            size="large"
          >
            Go Back
          </Button>
        </Box>
      </Box>
    </Container>
  )
}

export default NotFound
