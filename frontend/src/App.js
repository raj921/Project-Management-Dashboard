import React, { useState } from 'react';
import {
  Box, Button, Card, CardContent, CardHeader, CircularProgress, Container, CssBaseline,
  FormControl, FormHelperText, Grid, Input, InputLabel, List,
  ListItem, ListItemIcon, ListItemText, ThemeProvider, Typography, createTheme
} from '@mui/material';
import { CloudUpload, Description, Error, Warning, CheckCircle, Assignment, Event } from '@mui/icons-material';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 500,
    },
    h2: {
      fontWeight: 500,
      margin: '1.5rem 0 1rem',
    },
    h3: {
      fontWeight: 500,
      margin: '1.25rem 0 0.75rem',
    },
  },
});

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setResult(null);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'https://project-management-dashboard-w90o.onrender.com';
      console.log('API URL:', apiUrl);
      console.log('Sending request to:', `${apiUrl}/dashboard`);
      const res = await fetch(`${apiUrl}/dashboard`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Failed to fetch dashboard data');
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const hasBlockers = (blockers) => {
    if (!blockers) return false;
    return blockers.some(b => b.task);
  };

  const getStatusIcon = (status) => {
    if (!status) return <Assignment color="action" />;
    const statusLower = status.toLowerCase();
    if (statusLower.includes('complete') || statusLower.includes('done')) {
      return <CheckCircle color="success" />;
    } else if (statusLower.includes('block') || statusLower.includes('risk')) {
      return <Warning color="warning" />;
    } else if (statusLower.includes('error') || statusLower.includes('fail')) {
      return <Error color="error" />;
    }
    return <Assignment color="action" />;
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Project Management Dashboard
          </Typography>
        </Box>

        <Card sx={{ mb: 4, boxShadow: 3 }}>
          <CardHeader 
            title="Upload Project Data" 
            titleTypographyProps={{ variant: 'h5' }}
            avatar={<CloudUpload color="primary" />}
          />
          <CardContent>
            <form onSubmit={handleSubmit}>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={8}>
                  <FormControl fullWidth>
                    <InputLabel htmlFor="file-upload" shrink={!!file}>
                      {file ? file.name : ""}
                    </InputLabel>
                    <Input
                      id="file-upload"
                      type="file"
                      inputProps={{ accept: '.xlsx' }}
                      onChange={handleFileChange}
                      disabled={loading}
                      sx={{ display: 'none' }}
                    />
                    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2, alignItems: 'flex-start', mt: 1 }}>
                      <Box>
                        <label htmlFor="file-upload">
                          <Button
                            variant="outlined"
                            component="span"
                            startIcon={<CloudUpload />}
                            disabled={loading}
                            sx={{ whiteSpace: 'nowrap' }}
                          >
                            Choose File
                          </Button>
                        </label>
                      </Box>
                      {file && (
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            p: 1, 
                            bgcolor: 'action.hover', 
                            borderRadius: 1,
                            wordBreak: 'break-word',
                            width: '100%',
                            maxWidth: 400
                          }}
                        >
                          {file.name}
                          <Typography component="span" variant="caption" display="block" color="text.secondary">
                            ({(file.size / 1024).toFixed(2)} KB)
                          </Typography>
                        </Typography>
                      )}
                    </Box>
                    <FormHelperText>Upload your project data in Excel format</FormHelperText>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4} sx={{ textAlign: { xs: 'center', md: 'right' } }}>
                  <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={!file || loading}
                    startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Description />}
                  >
                    {loading ? 'Analyzing...' : 'Analyze Project'}
                  </Button>
                </Grid>
              </Grid>
            </form>
          </CardContent>
        </Card>

        {error && (
          <Card sx={{ mb: 4, bgcolor: 'error.light' }}>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Error color="error" sx={{ mr: 1 }} />
                <Typography variant="body1">{error}</Typography>
              </Box>
            </CardContent>
          </Card>
        )}

        {result && (
          <Box>
            {/* Project Summary */}
            <Card sx={{ mb: 4, boxShadow: 3 }}>
              <CardHeader 
                title="Project Summary" 
                titleTypographyProps={{ variant: 'h5' }}
                avatar={<Description color="primary" />}
              />
              <CardContent>
                <Typography variant="body1" paragraph>{result.summary}</Typography>
                
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  {result.milestones && result.milestones.length > 0 && (
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>Milestones</Typography>
                      <List dense>
                        {result.milestones.map((milestone, i) => (
                          <ListItem key={i}>
                            <ListItemIcon><Event color="primary" /></ListItemIcon>
                            <ListItemText primary={milestone} />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                  )}
                  
                  {result.updates && result.updates.length > 0 && (
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>Team Updates</Typography>
                      <List dense>
                        {result.updates.map((update, i) => (
                          <ListItem key={i}>
                            <ListItemText primary={update} />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                  )}
                </Grid>
              </CardContent>
            </Card>

            {/* Tasks */}
            {result.tasks && result.tasks.length > 0 && (
              <Card sx={{ mb: 4, boxShadow: 3 }}>
                <CardHeader 
                  title="Tasks" 
                  titleTypographyProps={{ variant: 'h5' }}
                  avatar={<Assignment color="primary" />}
                />
                <CardContent>
                  <List>
                    {result.tasks.map((task, i) => (
                      <ListItem key={i} divider={i < result.tasks.length - 1}>
                        <ListItemIcon>
                          {getStatusIcon(task.Status || task.status)}
                        </ListItemIcon>
                        <ListItemText
                          primary={task.Task || task.task || 'No Description'}
                          secondary={
                            <>
                              <Typography component="span" variant="body2" color="text.primary" display="block">
                                Status: {task.Status || task.status || 'No Status'}
                              </Typography>
                              <Typography component="span" variant="body2" color="text.secondary" display="block">
                                Owner: {task.Owner || task.owner || 'Unassigned'}
                              </Typography>
                              <Typography component="span" variant="body2" color="text.secondary">
                                Due: {task.DueDate || task.dueDate || task.due || 'No due date'}
                              </Typography>
                            </>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            )}

            {/* Blockers & Risks */}
            <Card sx={{ mb: 4, boxShadow: 3, borderLeft: hasBlockers(result.blockers) ? '4px solid #ff9800' : 'none' }}>
              <CardHeader 
                title="Blockers & Risks" 
                titleTypographyProps={{ 
                  variant: 'h5',
                  color: hasBlockers(result.blockers) ? 'error' : 'textPrimary'
                }}
                avatar={<Warning color={hasBlockers(result.blockers) ? 'warning' : 'disabled'} />}
              />
              <CardContent>
                {!hasBlockers(result.blockers) ? (
                  <Typography>No blockers or risks detected.</Typography>
                ) : (
                  <List>
                    {result.blockers.filter(b => b.task).map((blocker, i) => (
                      <ListItem key={i} alignItems="flex-start" divider={i < result.blockers.length - 1}>
                        <ListItemIcon><Warning color="warning" /></ListItemIcon>
                        <ListItemText
                          primary={blocker.task}
                          secondary={
                            <>
                              <Typography component="span" variant="body2" color="text.primary" display="block">
                                Reason: {blocker.reason}
                              </Typography>
                              <Typography component="span" variant="body2" color="text.secondary">
                                Owner: {blocker.owner || 'Unassigned'} | Due: {blocker.due || 'No due date'}
                              </Typography>
                            </>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                )}

                {/* AI Analysis */}
                {result.blockers && result.blockers.filter(b => b.llm_analysis).length > 0 && (
                  <Box sx={{ mt: 3, p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                      <Description color="primary" sx={{ mr: 1 }} /> AI Analysis
                    </Typography>
                    <Typography variant="body2">
                      {result.blockers.find(b => b.llm_analysis)?.llm_analysis}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>

            {/* Action Plan */}
            {result.actions && result.actions.length > 0 && (
              <Card sx={{ mb: 4, boxShadow: 3, borderLeft: '4px solid #4caf50' }}>
                <CardHeader 
                  title="Action Plan / Next Steps" 
                  titleTypographyProps={{ variant: 'h5' }}
                  avatar={<CheckCircle color="success" />}
                />
                <CardContent>
                  <List>
                    {result.actions.map((action, i) => (
                      <ListItem key={i}>
                        <ListItemIcon><CheckCircle color="action" /></ListItemIcon>
                        <ListItemText primary={action} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            )}
          </Box>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;
