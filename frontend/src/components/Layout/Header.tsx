import React from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  useTheme,
  useMediaQuery,
  Badge,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  Search as SearchIcon,
} from '@mui/icons-material'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '../../store'
import { toggleSidebar } from '../../store/slices/uiSlice'

const Header: React.FC = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const dispatch = useDispatch()
  const { notifications } = useSelector((state: RootState) => state.ui)

  const handleMenuClick = () => {
    dispatch(toggleSidebar())
  }

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: theme.zIndex.drawer + 1,
        backgroundColor: 'background.paper',
        color: 'text.primary',
        boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="toggle sidebar"
          onClick={handleMenuClick}
          edge="start"
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <Typography
          variant="h6"
          component="div"
          sx={{
            flexGrow: 1,
            fontWeight: 600,
            color: 'primary.main',
          }}
        >
          NexusKnowledge
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton color="inherit" aria-label="search">
            <SearchIcon />
          </IconButton>

          <IconButton color="inherit" aria-label="notifications">
            <Badge
              badgeContent={notifications.length}
              color="error"
              max={99}
            >
              <NotificationsIcon />
            </Badge>
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Header
