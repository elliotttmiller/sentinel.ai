import React, { useEffect, useState } from "react";
import { Card, CardContent, Typography, Grid } from "@mui/material";

function DashboardWidgets() {
  const [widgets, setWidgets] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/dashboard")
      .then((res) => {
        if (!res.ok) {
          setLoading(false);
          setWidgets(null);
          return null;
        }
        return res.json();
      })
      .then((data) => {
        if (data) setWidgets(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
        setWidgets(null);
      });
  }, []);

  if (loading) return <div style={{textAlign:'center',marginTop:'2rem'}}><span style={{fontSize:'1.2rem'}}>Loading dashboard...</span></div>;
  if (!widgets) return <div style={{color:'red',textAlign:'center',marginTop:'2rem'}}>Dashboard API not available or returned no data.</div>;

  return (
    <div style={{ maxWidth: 800, margin: '2rem auto', padding: '1rem' }}>
      <Typography variant="h4" align="center" gutterBottom>System Overview</Typography>
      <Grid container spacing={3} justifyContent="center">
        <Grid>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" color="primary">Status</Typography>
              <Typography variant="body1">{widgets.system_status === "ok" ? "✅ Operational" : "⚠️ Issue"}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" color="primary">Active Users</Typography>
              <Typography variant="body1">👤 {widgets.active_users}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" color="primary">Missions</Typography>
              <Typography variant="body1">🚀 {widgets.missions}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      <Typography variant="caption" display="block" align="center" style={{marginTop:'2rem',color:'#888'}}>
        Last updated: {new Date(widgets.timestamp).toLocaleString()}
      </Typography>
    </div>
  );
}

export default DashboardWidgets;
