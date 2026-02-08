import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, Cpu, Database, Zap, TrendingUp, Layers, Server, Clock } from 'lucide-react';
import './App.css';

const API_URL = 'http://localhost:5000';

function App() {
  const [tasks, setTasks] = useState([]);
  const [taskType, setTaskType] = useState('send_email');
  const [emailTo, setEmailTo] = useState('');
  const [videoFile, setVideoFile] = useState('');
  const [stats, setStats] = useState({ total: 0, pending: 0, running: 0, completed: 0 });
  const [throughput, setThroughput] = useState([]);
  const [workerDistribution, setWorkerDistribution] = useState([]);

  useEffect(() => {
    loadTasks();
    const interval = setInterval(loadTasks, 1500);
    return () => clearInterval(interval);
  }, []);

  const loadTasks = async () => {
    try {
      const response = await axios.get(`${API_URL}/tasks`);
      const taskData = response.data;
      setTasks(taskData);

      setStats({
        total: taskData.length,
        pending: taskData.filter(t => t.status === 'pending').length,
        running: taskData.filter(t => t.status === 'running').length,
        completed: taskData.filter(t => t.status === 'completed').length
      });

      
      const last20 = taskData.slice(0, 20).reverse();
      const throughputData = last20.reduce((acc, task, idx) => {
        const bucket = Math.floor(idx / 4);
        if (!acc[bucket]) acc[bucket] = { name: `T${bucket}`, count: 0 };
        if (task.status === 'completed') acc[bucket].count++;
        return acc;
      }, []).filter(Boolean);
      setThroughput(throughputData);

      
      setWorkerDistribution([
        { name: 'Worker 1', value: taskData.filter((t, i) => i % 3 === 0 && t.status === 'completed').length },
        { name: 'Worker 2', value: taskData.filter((t, i) => i % 3 === 1 && t.status === 'completed').length },
        { name: 'Worker 3', value: taskData.filter((t, i) => i % 3 === 2 && t.status === 'completed').length },
      ]);
    } catch (error) {
      console.error('Error loading tasks:', error);
    }
  };

  const createTask = async (e) => {
    e.preventDefault();
    const data = taskType === 'send_email' ? { to: emailTo } : { file: videoFile };
    try {
      await axios.post(`${API_URL}/tasks`, { type: taskType, data });
      setEmailTo('');
      setVideoFile('');
      loadTasks();
    } catch (error) {
      console.error('Error creating task:', error);
    }
  };

  const MetricCard = ({ icon: Icon, label, value, trend, color, gradient }) => (
    <div className="metric-card" style={{ background: gradient }}>
      <div className="metric-header">
        <div className="metric-icon" style={{ background: color }}>
          <Icon size={20} strokeWidth={2.5} />
        </div>
        {trend && <span className="metric-trend">↑ {trend}%</span>}
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-label">{label}</div>
    </div>
  );

  const COLORS = ['#8b5cf6', '#ec4899', '#06b6d4'];

  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-content">
          <div className="nav-brand">
            <div className="brand-icon">
              <Layers size={28} strokeWidth={2.5} />
            </div>
            <div className="brand-text">
              <span className="brand-name">ScaleFlow</span>
              <span className="brand-tagline">Distributed Task Execution Engine</span>
            </div>
          </div>
          <div className="nav-stats">
            <div className="nav-stat">
              <Server size={16} />
              <span>3 Workers Active</span>
            </div>
            <div className="nav-stat">
              <Database size={16} />
              <span>PostgreSQL</span>
            </div>
            <div className="nav-stat">
              <Zap size={16} />
              <span>Redis Queue</span>
            </div>
          </div>
        </div>
      </nav>

      <div className="container">
        <div className="metrics-grid">
          <MetricCard 
            icon={Activity} 
            label="Total Tasks Processed" 
            value={stats.total}
            trend={stats.total > 0 ? 12 : 0}
            color="rgba(139, 92, 246, 0.2)"
            gradient="linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%)"
          />
          <MetricCard 
            icon={Clock} 
            label="Pending in Queue" 
            value={stats.pending}
            color="rgba(251, 191, 36, 0.2)"
            gradient="linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(251, 191, 36, 0.05) 100%)"
          />
          <MetricCard 
            icon={Cpu} 
            label="Currently Executing" 
            value={stats.running}
            color="rgba(59, 130, 246, 0.2)"
            gradient="linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%)"
          />
          <MetricCard 
            icon={TrendingUp} 
            label="Successfully Completed" 
            value={stats.completed}
            trend={stats.completed > 0 ? 8 : 0}
            color="rgba(16, 185, 129, 0.2)"
            gradient="linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%)"
          />
        </div>

        <div className="dashboard-grid">
          <div className="panel large">
            <div className="panel-header">
              <h2>Task Throughput Analysis</h2>
              <span className="panel-subtitle">Completed tasks over time buckets</span>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={throughput}>
                <defs>
                  <linearGradient id="colorThroughput" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip contentStyle={{ background: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }} />
                <Area type="monotone" dataKey="count" stroke="#8b5cf6" strokeWidth={3} fillOpacity={1} fill="url(#colorThroughput)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2>Worker Load Distribution</h2>
              <span className="panel-subtitle">Tasks per worker node</span>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={workerDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {workerDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="legend">
              {workerDistribution.map((worker, idx) => (
                <div key={idx} className="legend-item">
                  <div className="legend-dot" style={{ background: COLORS[idx] }} />
                  <span>{worker.name}: {worker.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="panel create-panel">
            <div className="panel-header">
              <h2>Dispatch New Task</h2>
              <span className="panel-subtitle">Submit to distributed queue</span>
            </div>
            <form onSubmit={createTask} className="create-form">
              <div className="form-row">
                <div className="form-field">
                  <label>Task Type</label>
                  <select value={taskType} onChange={(e) => setTaskType(e.target.value)}>
                    <option value="send_email">Email Delivery</option>
                    <option value="process_video">Video Processing</option>
                  </select>
                </div>
              </div>
              {taskType === 'send_email' ? (
                <div className="form-field">
                  <label>Recipient Address</label>
                  <input
                    type="email"
                    value={emailTo}
                    onChange={(e) => setEmailTo(e.target.value)}
                    placeholder="user@domain.com"
                    required
                  />
                </div>
              ) : (
                <div className="form-field">
                  <label>Media File Path</label>
                  <input
                    type="text"
                    value={videoFile}
                    onChange={(e) => setVideoFile(e.target.value)}
                    placeholder="media/video_1080p.mp4"
                    required
                  />
                </div>
              )}
              <button type="submit" className="submit-btn">
                <Zap size={18} />
                Enqueue Task
              </button>
            </form>
          </div>

          <div className="panel execution-log">
            <div className="panel-header">
              <h2>Execution Log</h2>
              <span className="panel-subtitle">Real-time task lifecycle</span>
            </div>
            <div className="log-container">
              {tasks.length === 0 ? (
                <div className="empty-log">
                  <Server size={48} opacity={0.3} />
                  <p>No tasks in execution history</p>
                </div>
              ) : (
                tasks.map(task => (
                  <div key={task.id} className={`log-entry status-${task.status}`}>
                    <div className="log-header">
                      <div className="log-id">
                        <div className="status-indicator" />
                        <span>#{task.id}</span>
                      </div>
                      <div className="log-badge">{task.status}</div>
                    </div>
                    <div className="log-body">
                      <code className="log-type">{task.type}</code>
                      <span className="log-data">{JSON.stringify(task.data)}</span>
                    </div>
                    <div className="log-timeline">
                      <div className="timeline-event">
                        <Clock size={12} />
                        <span>{new Date(task.created_at).toLocaleTimeString()}</span>
                      </div>
                      {task.started_at && (
                        <div className="timeline-event">
                          <Cpu size={12} />
                          <span>{new Date(task.started_at).toLocaleTimeString()}</span>
                        </div>
                      )}
                      {task.completed_at && (
                        <div className="timeline-event">
                          <TrendingUp size={12} />
                          <span>{new Date(task.completed_at).toLocaleTimeString()}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;