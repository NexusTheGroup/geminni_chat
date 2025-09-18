import React from 'react'
import {
  Snackbar,
  Alert,
  AlertTitle,
  IconButton,
  Box,
} from '@mui/material'
import { Close as CloseIcon } from '@mui/icons-material'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '../../store'
import { removeNotification } from '../../store/slices/uiSlice'

const NotificationSnackbar: React.FC = () => {
  const dispatch = useDispatch()
  const { notifications } = useSelector((state: RootState) => state.ui)

  const handleClose = (notificationId: string) => {
    dispatch(removeNotification(notificationId))
  }

  const latestNotification = notifications[notifications.length - 1]

  if (!latestNotification) {
    return null
  }

  return (
    <Snackbar
      open={!!latestNotification}
      autoHideDuration={6000}
      onClose={() => handleClose(latestNotification.id)}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      sx={{ mt: 8 }}
    >
      <Alert
        severity={latestNotification.type}
        action={
          <IconButton
            size="small"
            aria-label="close"
            color="inherit"
            onClick={() => handleClose(latestNotification.id)}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        }
        sx={{ minWidth: 300 }}
      >
        <AlertTitle>
          {latestNotification.type === 'success' && 'Success'}
          {latestNotification.type === 'error' && 'Error'}
          {latestNotification.type === 'warning' && 'Warning'}
          {latestNotification.type === 'info' && 'Information'}
        </AlertTitle>
        {latestNotification.message}
      </Alert>
    </Snackbar>
  )
}

export default NotificationSnackbar
