import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Users, MessageCircle, Activity } from 'lucide-react';

export default function Dashboard() {
  const [farmers, setFarmers] = useState([]);
  const [queries, setQueries] = useState([]);

  useEffect(() => {
    // Fetch dashboard data from FastAPI
    axios.get('http://127.0.0.1:8000/farmers/').then(res => setFarmers(res.data)).catch(console.error);
    axios.get('http://127.0.0.1:8000/queries/').then(res => setQueries(res.data)).catch(console.error);
  }, []);

  return (
    <div>
      <h2>Dashboard Overview</h2>
      <p className="subtitle">Real-time metrics and recent farmer interactions</p>
      
      <div className="dash-grid">
        <div className="card glass">
          <h3><Users size={20} className="status-indicator" style={{padding: '4px', background: 'transparent'}}/> Total Farmers</h3>
          <p className="metric">{farmers.length}</p>
        </div>
        <div className="card glass">
          <h3><MessageCircle size={20} className="status-indicator" style={{padding: '4px', background: 'transparent'}}/> Total Queries</h3>
          <p className="metric">{queries.length}</p>
        </div>
        <div className="card glass">
          <h3><Activity size={20} className="status-indicator" style={{padding: '4px', background: 'transparent'}}/> System Status</h3>
          <p className="metric" style={{fontSize: '2rem', color: '#10b981'}}>Online</p>
        </div>
      </div>

      <h2 style={{ marginTop: '48px', marginBottom: '24px', fontSize: '1.8rem' }}>Recent Activity</h2>
      <div className="glass" style={{ borderRadius: '20px', overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Farmer Details</th>
              <th>Interaction Type</th>
              <th>Query snippet</th>
              <th>AI Response snippet</th>
            </tr>
          </thead>
          <tbody>
            {queries.slice(0, 10).map(q => (
              <tr key={q._id}>
                <td style={{fontWeight: 500}}>{q.phone_number}</td>
                <td>
                  <span className={`badge badge-${q.query_type === 'image' ? 'image' : q.query_type === 'voice' ? 'voice' : 'text'}`}>
                    {q.query_type}
                  </span>
                </td>
                <td style={{color: 'var(--text-muted)'}}>{q.query_text ? (q.query_text.length > 40 ? q.query_text.substring(0, 40) + '...' : q.query_text) : 'Media Request'}</td>
                <td style={{color: 'var(--text-muted)'}}>{q.bot_response ? q.bot_response.substring(0, 50) + '...' : '-'}</td>
              </tr>
            ))}
            {queries.length === 0 && (
              <tr>
                <td colSpan="4" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No queries found yet. Head to the Chat Simulator to test the bot!
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
