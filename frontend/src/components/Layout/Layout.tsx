import React from 'react'
import { Box, useTheme, useMediaQuery } from '@mui/material'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '../../store'
import { setSidebarOpen } from '../../store/slices/uiSlice'
import Sidebar from './Sidebar'
import Header from './Header'
import NotificationSnackbar from './NotificationSnackbar'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const dispatch = useDispatch()
  const { sidebarOpen } = useSelector((state: RootState) => state.ui)

  React.useEffect(() => {
    if (isMobile) {
      dispatch(setSidebarOpen(false))
    }
  }, [isMobile, dispatch])

  return (
    <>
      <Header />
      <Box sx={{ display: 'flex', flex: 1 }}>
        <Sidebar />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            width: { sm: `calc(100% - ${sidebarOpen ? 240 : 0}px)` },
            ml: { sm: sidebarOpen ? 0 : 0 },
            transition: theme.transitions.create(['width', 'margin'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
            minHeight: 'calc(100vh - 64px)',
            backgroundColor: 'background.default',
          }}
        >
          {children}
        </Box>
      </Box>
      <NotificationSnackbar />
    </>
  )
}

export default Layout
