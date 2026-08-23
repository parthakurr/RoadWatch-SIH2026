import React, { useState, useEffect, useRef, useMemo } from 'react';
import L from 'leaflet';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
} from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

// ─── Municipal Ward Zone Definitions (New Delhi) ─────────────────────────────
const WARD_ZONES = [
  { name: 'All Wards', bounds: null },
  { name: 'Ward 1 — Connaught Place',   bounds: { latMin: 28.614, latMax: 28.624, lngMin: 77.205, lngMax: 77.218 } },
  { name: 'Ward 2 — Karol Bagh',        bounds: { latMin: 28.604, latMax: 28.614, lngMin: 77.198, lngMax: 77.210 } },
  { name: 'Ward 3 — Lodhi Road',         bounds: { latMin: 28.604, latMax: 28.614, lngMin: 77.210, lngMax: 77.220 } },
  { name: 'Ward 4 — Chandni Chowk',     bounds: { latMin: 28.618, latMax: 28.628, lngMin: 77.198, lngMax: 77.213 } },
  { name: 'Ward 5 — Paharganj',          bounds: { latMin: 28.610, latMax: 28.622, lngMin: 77.200, lngMax: 77.215 } },
  { name: 'Ward 6 — India Gate',         bounds: { latMin: 28.608, latMax: 28.620, lngMin: 77.212, lngMax: 77.226 } },
];

// ─── Login Screen Component ──────────────────────────────────────────────────
function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    setTimeout(() => {
      if (username === 'admin' && (password === 'roadeye2026' || password === 'roadwatch2026')) {
        sessionStorage.setItem('rw_auth', 'true');
        onLogin();
      } else {
        setError('Invalid credentials. Use admin / roadeye2026');
        setIsLoading(false);
      }
    }, 500);
  };

  return (
    <div className="min-h-screen animated-gradient flex items-center justify-center p-4 bg-slate-950 text-slate-100">
      <div className="w-full max-w-md fade-in">
        {/* Logo & Branding */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-amber-500 to-red-600 flex items-center justify-center font-bold text-white shadow-2xl shadow-amber-500/30 text-3xl mx-auto mb-4 tracking-wider">
            RE
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">RoadEye</h1>
          <p className="text-slate-400 text-sm mt-1">Municipal AI Road Governance Platform</p>
          <span className="inline-block mt-2 text-xs bg-amber-500/20 text-amber-400 px-3 py-1 rounded-full border border-amber-500/30 font-semibold">
            SIH 2026 — Command Center
          </span>
        </div>

        {/* Login Card */}
        <div className="bg-slate-900/90 backdrop-blur-xl rounded-2xl border border-slate-800 p-8 shadow-2xl">
          <h2 className="text-lg font-bold text-white mb-1">Municipal Officer Login</h2>
          <p className="text-xs text-slate-400 mb-6">Authorized personnel only. Enter your credentials.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs text-slate-400 font-semibold mb-1.5 uppercase tracking-wider">Officer ID</label>
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder="Enter officer username"
                className="w-full bg-slate-950 border border-slate-700 text-white text-sm px-4 py-3 rounded-xl outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500/50 transition"
                autoFocus
                required
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 font-semibold mb-1.5 uppercase tracking-wider">Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Enter password"
                className="w-full bg-slate-950 border border-slate-700 text-white text-sm px-4 py-3 rounded-xl outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500/50 transition"
                required
              />
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-xs px-4 py-2.5 rounded-xl font-medium">
                🔒 {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-sm py-3 rounded-xl shadow-lg shadow-amber-500/20 transition-all btn-glow disabled:opacity-60 cursor-pointer"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                  Authenticating...
                </span>
              ) : 'Sign In to Command Center'}
            </button>
          </form>

          <div className="mt-5 pt-4 border-t border-slate-800 text-center">
            <p className="text-xs text-slate-500">🔐 Demo Login: <code className="text-amber-400">admin</code> / <code className="text-amber-400">roadeye2026</code></p>
          </div>
        </div>

        <p className="text-center text-xs text-slate-600 mt-6">
          Powered by RoadEye Edge AI — Smart India Hackathon 2026
        </p>
      </div>
    </div>
  );
}

// ─── Main App Component ──────────────────────────────────────────────────────
export default function App() {
  // Auth State
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => sessionStorage.getItem('rw_auth') === 'true'
  );

  // Data State
  const [potholes, setPotholes] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [selectedPothole, setSelectedPothole] = useState(null);
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [filterWard, setFilterWard] = useState('All Wards');
  const [activeTab, setActiveTab] = useState('map'); // 'map' | 'list' | 'analytics'
  const [loading, setLoading] = useState(true);
  const [assignContractorInput, setAssignContractorInput] = useState('');

  const mapRef = useRef(null);
  const leafletInstance = useRef(null);
  const markersGroup = useRef(null);

  // API Backend fetch
  const API_BASE = 'http://localhost:8000/api/v1';

  const fetchData = async () => {
    try {
      let url = `${API_BASE}/potholes?limit=150`;
      if (filterSeverity !== 'ALL') url += `&severity=${filterSeverity}`;
      if (filterStatus !== 'ALL') url += `&status=${filterStatus}`;

      const [resPotholes, resAnalytics] = await Promise.all([
        fetch(url).then(r => r.json()),
        fetch(`${API_BASE}/analytics/summary`).then(r => r.json())
      ]);

      setPotholes(resPotholes);
      setAnalytics(resAnalytics);
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch RoadWatch data:", err);
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isAuthenticated) return;
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, [filterSeverity, filterStatus, isAuthenticated]);

  // ─── Ward-Filtered Potholes (client-side GPS bounding box) ───────────────
  const filteredPotholes = useMemo(() => {
    const ward = WARD_ZONES.find(w => w.name === filterWard);
    if (!ward || !ward.bounds) return potholes;
    return potholes.filter(p =>
      p.latitude >= ward.bounds.latMin &&
      p.latitude <= ward.bounds.latMax &&
      p.longitude >= ward.bounds.lngMin &&
      p.longitude <= ward.bounds.lngMax
    );
  }, [potholes, filterWard]);

  // ─── Leaflet Map ─────────────────────────────────────────────────────────
  useEffect(() => {
    if (activeTab !== 'map' || !mapRef.current || !isAuthenticated) return;

    if (!leafletInstance.current) {
      const map = L.map(mapRef.current).setView([28.6139, 77.2090], 13);

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(map);

      leafletInstance.current = map;
      markersGroup.current = L.layerGroup().addTo(map);
    }

    // Invalidate map size to ensure tiles render immediately
    setTimeout(() => {
      if (leafletInstance.current) {
        leafletInstance.current.invalidateSize();
      }
    }, 200);

    // Render Markers
    if (markersGroup.current) {
      markersGroup.current.clearLayers();

      filteredPotholes.forEach(p => {
        let color = '#EAB308'; // Low = Yellow
        if (p.severity === 'HIGH') color = '#EF4444';
        else if (p.severity === 'MEDIUM') color = '#F97316';
        if (p.status === 'VERIFIED_FIXED') color = '#22C55E';

        const customIcon = L.divIcon({
          className: 'custom-pin',
          html: `
            <div style="
              background-color: ${color};
              width: 22px;
              height: 22px;
              border-radius: 50%;
              border: 3px solid white;
              box-shadow: 0 0 12px ${color};
              display: flex;
              align-items: center;
              justify-content: center;
              color: white;
              font-size: 10px;
              font-weight: bold;
            ">
              ${p.scan_count > 1 ? p.scan_count : ''}
            </div>
          `,
          iconSize: [22, 22],
          iconAnchor: [11, 11]
        });

        const marker = L.marker([p.latitude, p.longitude], { icon: customIcon });
        marker.on('click', () => setSelectedPothole(p));
        markersGroup.current.addLayer(marker);
      });
    }

    // Fly to ward bounds when ward filter changes
    if (filterWard !== 'All Wards' && leafletInstance.current) {
      const ward = WARD_ZONES.find(w => w.name === filterWard);
      if (ward?.bounds) {
        leafletInstance.current.fitBounds([
          [ward.bounds.latMin, ward.bounds.lngMin],
          [ward.bounds.latMax, ward.bounds.lngMax]
        ], { padding: [30, 30], maxZoom: 15 });
      }
    }
  }, [filteredPotholes, activeTab, isAuthenticated, filterWard]);

  // ─── Status Update Handlers ──────────────────────────────────────────────
  const handleUpdateStatus = async (id, newStatus, contractor = null) => {
    try {
      const res = await fetch(`${API_BASE}/potholes/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          assigned_contractor: contractor || selectedPothole?.assigned_contractor
        })
      });
      const updated = await res.json();
      setSelectedPothole(updated);
      fetchData();
    } catch (err) {
      alert("Failed to update pothole status");
    }
  };

  const handleVerifyRepair = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/potholes/${id}/verify-repair`, { method: 'POST' });
      const updated = await res.json();
      setSelectedPothole(updated);
      fetchData();
    } catch (err) {
      alert("Verification failed");
    }
  };

  // ─── Export Handlers ─────────────────────────────────────────────────────
  const exportCSV = () => {
    let url = `${API_BASE}/export/csv`;
    const params = [];
    if (filterSeverity !== 'ALL') params.push(`severity=${filterSeverity}`);
    if (filterStatus !== 'ALL') params.push(`status=${filterStatus}`);
    if (params.length) url += '?' + params.join('&');

    const a = document.createElement('a');
    a.href = url;
    a.download = 'RoadEye_Audit_Report.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const exportPDF = () => {
    const doc = new jsPDF();

    doc.setFontSize(20);
    doc.setTextColor(40);
    doc.text('RoadEye Municipal Audit Report', 14, 22);

    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 30);
    doc.text(`Total Potholes: ${analytics?.total_potholes || 0}  |  Repair Rate: ${analytics?.repair_rate_percentage || 0}%  |  Critical: ${analytics?.critical_high_count || 0}`, 14, 36);
    if (filterWard !== 'All Wards') doc.text(`Ward Filter: ${filterWard}`, 14, 42);

    const startY = filterWard !== 'All Wards' ? 48 : 42;

    autoTable(doc, {
      startY,
      head: [['ID', 'Defect Class', 'Severity', 'Latitude', 'Longitude', 'Status', 'Scans', 'Contractor']],
      body: filteredPotholes.map(p => [
        p.id,
        p.class_name,
        p.severity,
        p.latitude.toFixed(5),
        p.longitude.toFixed(5),
        p.status,
        p.scan_count,
        p.assigned_contractor || '—'
      ]),
      theme: 'grid',
      headStyles: { fillColor: [245, 158, 11], textColor: [15, 23, 42], fontStyle: 'bold' },
      styles: { fontSize: 8, cellPadding: 2 },
      alternateRowStyles: { fillColor: [248, 250, 252] },
    });

    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(150);
      doc.text('RoadEye SIH 2026 — Automated Road Damage Detection & Governance', 14, doc.internal.pageSize.height - 10);
      doc.text(`Page ${i} of ${pageCount}`, doc.internal.pageSize.width - 35, doc.internal.pageSize.height - 10);
    }

    doc.save('RoadEye_Audit_Report.pdf');
  };

  // ─── Logout Handler ──────────────────────────────────────────────────────
  const handleLogout = () => {
    sessionStorage.removeItem('rw_auth');
    setIsAuthenticated(false);
  };

  // ─── Chart Data ──────────────────────────────────────────────────────────
  const severityChartData = {
    labels: ['High Severity', 'Medium Severity', 'Low Severity'],
    datasets: [{
      data: [
        analytics?.critical_high_count || 0,
        analytics?.medium_count || 0,
        analytics?.low_count || 0
      ],
      backgroundColor: ['#EF4444', '#F97316', '#EAB308'],
      borderColor: ['#991B1B', '#9A3412', '#854D0E'],
      borderWidth: 2,
      hoverOffset: 8,
    }]
  };

  const statusCounts = useMemo(() => ({
    PENDING: potholes.filter(p => p.status === 'PENDING').length,
    ASSIGNED: potholes.filter(p => p.status === 'ASSIGNED').length,
    IN_REPAIR: potholes.filter(p => p.status === 'IN_REPAIR').length,
    VERIFIED_FIXED: potholes.filter(p => p.status === 'VERIFIED_FIXED').length,
    RE_SCAN_NEEDED: potholes.filter(p => p.status === 'RE_SCAN_NEEDED').length,
  }), [potholes]);

  const repairPipelineData = {
    labels: ['Pending', 'Assigned', 'In Repair', 'Verified Fixed', 'Re-Scan'],
    datasets: [{
      label: 'Pothole Count',
      data: [
        statusCounts.PENDING,
        statusCounts.ASSIGNED,
        statusCounts.IN_REPAIR,
        statusCounts.VERIFIED_FIXED,
        statusCounts.RE_SCAN_NEEDED
      ],
      backgroundColor: ['#F59E0B', '#3B82F6', '#F97316', '#22C55E', '#EF4444'],
      borderColor: ['#D97706', '#2563EB', '#EA580C', '#16A34A', '#DC2626'],
      borderWidth: 1,
      borderRadius: 6,
    }]
  };

  const darkChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#CBD5E1', font: { size: 11, weight: '600' }, padding: 16 }
      },
    },
  };

  const barChartOptions = {
    ...darkChartOptions,
    plugins: {
      ...darkChartOptions.plugins,
      legend: { display: false },
    },
    scales: {
      x: {
        ticks: { color: '#94A3B8', font: { size: 10 } },
        grid: { color: '#1E293B' },
        border: { color: '#334155' },
      },
      y: {
        ticks: { color: '#94A3B8', font: { size: 10 }, stepSize: 1 },
        grid: { color: '#1E293B' },
        border: { color: '#334155' },
        beginAtZero: true,
      },
    },
  };

  // ─── Auth Gate ───────────────────────────────────────────────────────────
  if (!isAuthenticated) {
    return <LoginScreen onLogin={() => setIsAuthenticated(true)} />;
  }

  // ─── Main Dashboard ──────────────────────────────────────────────────────
  return (
    <div className="h-screen w-screen bg-slate-950 text-slate-100 flex flex-col font-sans overflow-hidden">
      {/* ─── Top Navigation Bar ─── */}
      <header className="bg-slate-900 border-b border-slate-800 px-4 md:px-6 py-3 flex flex-col md:flex-row items-center justify-between shadow-xl gap-3 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-red-600 flex items-center justify-center font-bold text-white shadow-lg shadow-amber-500/20 text-xl shrink-0 tracking-wider">
            RE
          </div>
          <div>
            <h1 className="text-lg md:text-xl font-bold tracking-wide text-white flex items-center gap-2">
              RoadEye <span className="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded-full border border-amber-500/30">SIH 2026</span>
            </h1>
            <p className="text-xs text-slate-400 hidden sm:block">Municipal Automated Edge AI Pothole Governance System</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-1.5 bg-slate-950 p-1.5 rounded-xl border border-slate-800 overflow-x-auto w-full md:w-auto">
          {[
            { key: 'map', label: '🗺️ GIS Command Map' },
            { key: 'list', label: '📋 Work Orders' },
            { key: 'analytics', label: '📊 Analytics' },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-3 md:px-4 py-1.5 rounded-lg text-xs md:text-sm font-medium transition whitespace-nowrap cursor-pointer ${
                activeTab === tab.key
                  ? 'bg-amber-500 text-slate-950 font-bold shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Live Status + Logout */}
        <div className="flex items-center gap-2 md:gap-3">
          <span className="flex items-center gap-2 text-xs bg-emerald-500/10 text-emerald-400 px-3 py-1.5 rounded-full border border-emerald-500/20">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span className="hidden sm:inline">Edge Fleet Connected</span>
            <span className="sm:hidden">Live</span>
          </span>
          <button
            onClick={handleLogout}
            className="text-xs text-slate-400 hover:text-red-400 px-2.5 py-1.5 rounded-lg border border-slate-800 hover:border-red-500/30 transition cursor-pointer"
            title="Sign Out"
          >
            🚪 Logout
          </button>
        </div>
      </header>

      {/* ─── KPI Counters Bar ─── */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-2 md:gap-4 px-4 md:px-6 py-2.5 bg-slate-900/50 border-b border-slate-800/80 shrink-0">
        <div className="bg-slate-900 p-2.5 md:p-3 rounded-xl border border-slate-800">
          <div className="text-xs text-slate-400 font-medium">Total Detected</div>
          <div className="text-xl md:text-2xl font-black text-white mt-0.5">{analytics?.total_potholes || 0}</div>
        </div>
        <div className="bg-slate-900 p-2.5 md:p-3 rounded-xl border border-slate-800">
          <div className="text-xs text-red-400 font-medium flex items-center gap-1">🔴 High Severity</div>
          <div className="text-xl md:text-2xl font-black text-red-400 mt-0.5">{analytics?.critical_high_count || 0}</div>
        </div>
        <div className="bg-slate-900 p-2.5 md:p-3 rounded-xl border border-slate-800">
          <div className="text-xs text-amber-400 font-medium">🟠 In Repair</div>
          <div className="text-xl md:text-2xl font-black text-amber-400 mt-0.5">{analytics?.in_repair_count || 0}</div>
        </div>
        <div className="bg-slate-900 p-2.5 md:p-3 rounded-xl border border-slate-800">
          <div className="text-xs text-emerald-400 font-medium">🟢 Verified Fixed</div>
          <div className="text-xl md:text-2xl font-black text-emerald-400 mt-0.5">{analytics?.repaired_count || 0}</div>
        </div>
        <div className="bg-slate-900 p-2.5 md:p-3 rounded-xl border border-slate-800 col-span-2 md:col-span-1">
          <div className="text-xs text-indigo-400 font-medium">⚡ Repair Velocity</div>
          <div className="text-xl md:text-2xl font-black text-indigo-400 mt-0.5">{analytics?.repair_rate_percentage || 0}%</div>
        </div>
      </div>

      {/* ─── Main Content Area (Expands to Fill Screen) ─── */}
      <div className="flex-1 flex overflow-hidden relative">

        {/* ════════════ MAP VIEW ════════════ */}
        {activeTab === 'map' && (
          <div className="flex-1 flex flex-col md:flex-row relative h-full w-full">
            {/* Filter Floating Overlay */}
            <div className="absolute top-3 left-3 z-[1000] bg-slate-900/95 backdrop-blur-md p-2.5 md:p-3 rounded-xl border border-slate-700/80 shadow-2xl flex flex-wrap items-center gap-2 md:gap-3 max-w-[calc(100%-24px)]">
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-slate-400 font-semibold uppercase hidden sm:inline">Severity:</span>
                <select
                  value={filterSeverity}
                  onChange={e => setFilterSeverity(e.target.value)}
                  className="bg-slate-800 text-white text-xs px-2.5 py-1.5 rounded-lg border border-slate-700 outline-none cursor-pointer"
                >
                  <option value="ALL">All Severities</option>
                  <option value="HIGH">High Only</option>
                  <option value="MEDIUM">Medium Only</option>
                  <option value="LOW">Low Only</option>
                </select>
              </div>

              <div className="flex items-center gap-1.5">
                <span className="text-xs text-slate-400 font-semibold uppercase hidden sm:inline">Status:</span>
                <select
                  value={filterStatus}
                  onChange={e => setFilterStatus(e.target.value)}
                  className="bg-slate-800 text-white text-xs px-2.5 py-1.5 rounded-lg border border-slate-700 outline-none cursor-pointer"
                >
                  <option value="ALL">All Statuses</option>
                  <option value="PENDING">Pending Action</option>
                  <option value="ASSIGNED">Assigned</option>
                  <option value="IN_REPAIR">In Repair</option>
                  <option value="VERIFIED_FIXED">Verified Fixed</option>
                </select>
              </div>

              {/* Ward Filter */}
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-amber-400 font-semibold uppercase hidden sm:inline">🏙️ Ward:</span>
                <select
                  value={filterWard}
                  onChange={e => setFilterWard(e.target.value)}
                  className="bg-slate-800 text-amber-300 text-xs px-2.5 py-1.5 rounded-lg border border-amber-500/50 outline-none cursor-pointer font-medium"
                >
                  {WARD_ZONES.map(w => (
                    <option key={w.name} value={w.name}>{w.name}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Map Container Element */}
            <div ref={mapRef} className="flex-1 w-full h-full min-h-[400px] z-0"></div>

            {/* ─── Selected Pothole Detail Panel ─── */}
            {selectedPothole && (
              <div className="w-full md:w-96 bg-slate-900 border-t md:border-t-0 md:border-l border-slate-800 p-4 md:p-5 overflow-y-auto flex flex-col justify-between z-10 shadow-2xl slide-up md:animate-none max-h-[50vh] md:max-h-none shrink-0">
                <div>
                  <div className="flex items-start justify-between">
                    <div>
                      <span className={`text-xs px-2.5 py-1 rounded-full font-bold uppercase tracking-wider ${
                        selectedPothole.severity === 'HIGH' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                        selectedPothole.severity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                      }`}>
                        {selectedPothole.severity} SEVERITY
                      </span>
                      <h2 className="text-lg font-bold text-white mt-2">{selectedPothole.class_name} #{selectedPothole.id}</h2>
                    </div>
                    <button
                      onClick={() => setSelectedPothole(null)}
                      className="text-slate-400 hover:text-white text-lg font-bold p-1 cursor-pointer"
                    >
                      ✕
                    </button>
                  </div>

                  {/* Snapshot Image Preview */}
                  <div className="mt-3 rounded-xl overflow-hidden bg-slate-950 border border-slate-800 h-40 md:h-44 flex items-center justify-center">
                    {selectedPothole.image_base64 ? (
                      <img src={`data:image/jpeg;base64,${selectedPothole.image_base64}`} alt="Pothole Snapshot" className="w-full h-full object-cover" />
                    ) : (
                      <div className="text-center p-4">
                        <div className="text-3xl mb-1">📸</div>
                        <div className="text-xs text-slate-500">Live AI Edge Camera Snapshot</div>
                        <div className="text-xs text-amber-400/80 font-mono mt-1">Confidence: {(selectedPothole.confidence * 100).toFixed(0)}%</div>
                      </div>
                    )}
                  </div>

                  {/* Details Grid */}
                  <div className="mt-3 space-y-2 text-xs">
                    {[
                      ['Status', selectedPothole.status, 'text-amber-400 font-bold'],
                      ['GPS', `${selectedPothole.latitude}, ${selectedPothole.longitude}`, 'font-mono text-slate-200'],
                      ['Vehicle', selectedPothole.vehicle_id, 'font-mono text-indigo-400'],
                      ['Scans', `${selectedPothole.scan_count} times`, 'font-bold text-white bg-slate-800 px-2 py-0.5 rounded'],
                      ['Contractor', selectedPothole.assigned_contractor || 'Unassigned', 'text-slate-300'],
                    ].map(([label, value, cls]) => (
                      <div key={label} className="flex justify-between py-1 border-b border-slate-800">
                        <span className="text-slate-400">{label}</span>
                        <span className={cls}>{value}</span>
                      </div>
                    ))}
                  </div>

                  {/* Assign Contractor */}
                  <div className="mt-3 bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                    <label className="text-xs text-slate-400 block mb-1 font-medium">Assign Contractor:</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="e.g. PWD Zone 4 Infra"
                        value={assignContractorInput}
                        onChange={e => setAssignContractorInput(e.target.value)}
                        className="bg-slate-900 border border-slate-700 text-xs px-2.5 py-1.5 rounded-lg flex-1 text-white outline-none focus:border-amber-500 transition"
                      />
                      <button
                        onClick={() => {
                          if (assignContractorInput) {
                            handleUpdateStatus(selectedPothole.id, 'ASSIGNED', assignContractorInput);
                            setAssignContractorInput('');
                          }
                        }}
                        className="bg-amber-500 text-slate-950 font-bold text-xs px-3 py-1.5 rounded-lg hover:bg-amber-400 transition btn-glow cursor-pointer"
                      >
                        Assign
                      </button>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-3 space-y-2">
                  <button
                    onClick={() => handleUpdateStatus(selectedPothole.id, 'IN_REPAIR')}
                    className="w-full bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs py-2 rounded-xl border border-slate-700 transition cursor-pointer"
                  >
                    🚜 Mark Repair In Progress
                  </button>
                  <button
                    onClick={() => handleVerifyRepair(selectedPothole.id)}
                    className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs py-2.5 rounded-xl shadow-lg shadow-emerald-600/20 transition flex items-center justify-center gap-2 cursor-pointer"
                  >
                    ✅ Verify Repair (Auto-Scan Fixed)
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ════════════ WORK ORDERS LIST VIEW ════════════ */}
        {activeTab === 'list' && (
          <div className="flex-1 p-4 md:p-6 overflow-y-auto fade-in">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
              <h2 className="text-lg md:text-xl font-bold text-white">Municipal Work Orders & Inspection Log</h2>

              <div className="flex flex-wrap items-center gap-2">
                <select
                  value={filterWard}
                  onChange={e => setFilterWard(e.target.value)}
                  className="bg-slate-800 text-amber-300 text-xs px-2.5 py-1.5 rounded-lg border border-amber-500/50 outline-none cursor-pointer"
                >
                  {WARD_ZONES.map(w => (
                    <option key={w.name} value={w.name}>{w.name}</option>
                  ))}
                </select>

                <button
                  onClick={exportCSV}
                  className="bg-slate-800 hover:bg-slate-700 text-emerald-400 text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-700 transition flex items-center gap-1.5 cursor-pointer"
                >
                  📥 Export CSV
                </button>
                <button
                  onClick={exportPDF}
                  className="bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold px-3 py-1.5 rounded-lg shadow transition btn-glow flex items-center gap-1.5 cursor-pointer"
                >
                  📄 Export PDF Report
                </button>
              </div>
            </div>

            {filterWard !== 'All Wards' && (
              <div className="mb-3 text-xs bg-amber-500/10 text-amber-400 px-3 py-2 rounded-lg border border-amber-500/20 inline-flex items-center gap-2">
                🏙️ Filtered: <strong>{filterWard}</strong> — showing {filteredPotholes.length} of {potholes.length} records
                <button onClick={() => setFilterWard('All Wards')} className="ml-2 text-slate-400 hover:text-white cursor-pointer">✕ Clear</button>
              </div>
            )}

            <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs min-w-[700px]">
                  <thead className="bg-slate-950 text-slate-400 uppercase font-semibold border-b border-slate-800">
                    <tr>
                      <th className="p-3 md:p-3.5">ID</th>
                      <th className="p-3 md:p-3.5">Defect Class</th>
                      <th className="p-3 md:p-3.5">Severity</th>
                      <th className="p-3 md:p-3.5">Coordinates</th>
                      <th className="p-3 md:p-3.5">Scans</th>
                      <th className="p-3 md:p-3.5">Status</th>
                      <th className="p-3 md:p-3.5">Contractor</th>
                      <th className="p-3 md:p-3.5 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {filteredPotholes.map(p => (
                      <tr key={p.id} className="hover:bg-slate-800/50 transition">
                        <td className="p-3 md:p-3.5 font-bold text-white">#{p.id}</td>
                        <td className="p-3 md:p-3.5">{p.class_name}</td>
                        <td className="p-3 md:p-3.5">
                          <span className={`px-2 py-0.5 rounded font-bold ${
                            p.severity === 'HIGH' ? 'text-red-400 bg-red-500/10' :
                            p.severity === 'MEDIUM' ? 'text-amber-400 bg-amber-500/10' :
                            'text-yellow-400 bg-yellow-500/10'
                          }`}>{p.severity}</span>
                        </td>
                        <td className="p-3 md:p-3.5 font-mono text-xs">{p.latitude}, {p.longitude}</td>
                        <td className="p-3 md:p-3.5 font-bold text-white">{p.scan_count}x</td>
                        <td className="p-3 md:p-3.5">
                          <span className={`font-semibold ${
                            p.status === 'VERIFIED_FIXED' ? 'text-emerald-400' :
                            p.status === 'IN_REPAIR' ? 'text-orange-400' :
                            p.status === 'ASSIGNED' ? 'text-blue-400' :
                            'text-amber-400'
                          }`}>{p.status}</span>
                        </td>
                        <td className="p-3 md:p-3.5">{p.assigned_contractor || '—'}</td>
                        <td className="p-3 md:p-3.5 text-right">
                          <button
                            onClick={() => { setSelectedPothole(p); setActiveTab('map'); }}
                            className="bg-slate-800 hover:bg-slate-700 text-amber-400 px-3 py-1 rounded border border-slate-700 text-xs transition cursor-pointer"
                          >
                            📍 Inspect
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ════════════ ANALYTICS VIEW ════════════ */}
        {activeTab === 'analytics' && (
          <div className="flex-1 p-4 md:p-6 overflow-y-auto space-y-6 fade-in">
            <h2 className="text-lg md:text-xl font-bold text-white">Municipal Infrastructure Governance & Repair Metrics</h2>

            {/* Charts Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
              {/* Severity Doughnut Chart */}
              <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800">
                <h3 className="text-sm font-bold text-slate-300 mb-4">🔴 Severity Breakdown</h3>
                <div className="h-64 flex items-center justify-center">
                  <Doughnut data={severityChartData} options={{
                    ...darkChartOptions,
                    cutout: '55%',
                    plugins: {
                      ...darkChartOptions.plugins,
                      legend: {
                        position: 'bottom',
                        labels: { color: '#CBD5E1', font: { size: 11 }, padding: 16, usePointStyle: true, pointStyleWidth: 10 }
                      },
                    }
                  }} />
                </div>
              </div>

              {/* Repair Pipeline Bar Chart */}
              <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800">
                <h3 className="text-sm font-bold text-slate-300 mb-4">📊 Repair Pipeline Status</h3>
                <div className="h-64">
                  <Bar data={repairPipelineData} options={barChartOptions} />
                </div>
              </div>
            </div>

            {/* Repair Velocity KPI + Differentiators */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
              {/* Repair Velocity Gauge */}
              <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800">
                <h3 className="text-sm font-bold text-slate-300 mb-4">⚡ Fleet Repair Velocity</h3>
                <div className="flex items-center justify-center py-4">
                  <div className="relative w-40 h-40">
                    <svg className="w-40 h-40 -rotate-90" viewBox="0 0 120 120">
                      <circle cx="60" cy="60" r="52" fill="none" stroke="#1E293B" strokeWidth="10" />
                      <circle
                        cx="60" cy="60" r="52" fill="none" stroke="#F59E0B" strokeWidth="10"
                        strokeDasharray={`${(analytics?.repair_rate_percentage || 0) / 100 * 327} 327`}
                        strokeLinecap="round"
                        className="transition-all duration-1000"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-3xl font-black text-amber-400">{analytics?.repair_rate_percentage || 0}%</span>
                      <span className="text-xs text-slate-400">Repaired</span>
                    </div>
                  </div>
                </div>
                <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-slate-950 p-2.5 rounded-lg text-center border border-slate-800">
                    <div className="text-emerald-400 font-bold text-lg">{analytics?.repaired_count || 0}</div>
                    <div className="text-slate-400">Fixed</div>
                  </div>
                  <div className="bg-slate-950 p-2.5 rounded-lg text-center border border-slate-800">
                    <div className="text-amber-400 font-bold text-lg">{analytics?.in_repair_count || 0}</div>
                    <div className="text-slate-400">In Progress</div>
                  </div>
                </div>
              </div>

              {/* SIH Differentiators */}
              <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800">
                <h3 className="text-sm font-bold text-slate-300 mb-3">🏆 SIH Differentiators & Edge AI Stats</h3>
                <ul className="space-y-3 text-xs text-slate-400">
                  <li className="flex items-start gap-2.5 bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-emerald-400 text-lg">✓</span>
                    <div>
                      <strong className="text-slate-200 block">Spatial Deduplication (10m Haversine)</strong>
                      Prevents duplicate alerts when multiple garbage trucks pass the same pothole.
                    </div>
                  </li>
                  <li className="flex items-start gap-2.5 bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-emerald-400 text-lg">✓</span>
                    <div>
                      <strong className="text-slate-200 block">On-Device Offline Edge Buffer</strong>
                      Works without continuous 4G connectivity using SQLite buffer on Raspberry Pi.
                    </div>
                  </li>
                  <li className="flex items-start gap-2.5 bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-emerald-400 text-lg">✓</span>
                    <div>
                      <strong className="text-slate-200 block">Automated Repair Verification</strong>
                      Automatically checks if pothole is fixed when vehicle re-scans the area.
                    </div>
                  </li>
                  <li className="flex items-start gap-2.5 bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-emerald-400 text-lg">✓</span>
                    <div>
                      <strong className="text-slate-200 block">Active Fleet Vehicles</strong>
                      {analytics?.active_vehicles_count || 0} municipal vehicles actively scanning roads.
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ─── Footer ─── */}
      <footer className="bg-slate-900 border-t border-slate-800 px-6 py-2.5 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-500 shrink-0">
        <span>Powered by <strong className="text-amber-400/80">RoadEye AI</strong> — Smart India Hackathon 2026</span>
        <span>Edge AI • Haversine Dedup • FastAPI • React Leaflet GIS</span>
      </footer>
    </div>
  );
}
