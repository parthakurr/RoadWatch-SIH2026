import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';

export default function App() {
  const [potholes, setPotholes] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [selectedPothole, setSelectedPothole] = useState(null);
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');
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
    fetchData();
    const interval = setInterval(fetchData, 4000); // 4-second auto-poll
    return () => clearInterval(interval);
  }, [filterSeverity, filterStatus]);

  // Leaflet Map Initialization
  useEffect(() => {
    if (activeTab !== 'map' || !mapRef.current) return;

    if (!leafletInstance.current) {
      // Initialize map centered at New Delhi municipal area
      const map = L.map(mapRef.current).setView([28.6139, 77.2090], 13);
      
      // Dark tile layer for modern command center feel
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(map);

      leafletInstance.current = map;
      markersGroup.current = L.layerGroup().addTo(map);
    }

    // Render Markers
    if (markersGroup.current) {
      markersGroup.current.clearLayers();

      potholes.forEach(p => {
        let color = '#EAB308'; // Low = Yellow
        if (p.severity === 'HIGH') color = '#EF4444'; // High = Red
        else if (p.severity === 'MEDIUM') color = '#F97316'; // Med = Orange
        if (p.status === 'VERIFIED_FIXED') color = '#22C55E'; // Fixed = Green

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
  }, [potholes, activeTab]);

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

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <header className="bg-slate-900 border-b border-slate-800 px-6 py-4 flex flex-wrap items-center justify-between shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-red-600 flex items-center justify-center font-bold text-white shadow-lg shadow-amber-500/20 text-xl">
            RW
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-wide text-white flex items-center gap-2">
              RoadWatch <span className="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded-full border border-amber-500/30">SIH 2026</span>
            </h1>
            <p className="text-xs text-slate-400">Municipal Automated Edge AI Pothole Governance System</p>
          </div>
        </div>

        {/* Mode & Navigation Tabs */}
        <div className="flex items-center gap-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
          <button 
            onClick={() => setActiveTab('map')} 
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition ${activeTab === 'map' ? 'bg-amber-500 text-slate-950 font-bold shadow' : 'text-slate-400 hover:text-white'}`}>
            🗺️ GIS Command Map
          </button>
          <button 
            onClick={() => setActiveTab('list')} 
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition ${activeTab === 'list' ? 'bg-amber-500 text-slate-950 font-bold shadow' : 'text-slate-400 hover:text-white'}`}>
            📋 Work Orders
          </button>
          <button 
            onClick={() => setActiveTab('analytics')} 
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition ${activeTab === 'analytics' ? 'bg-amber-500 text-slate-950 font-bold shadow' : 'text-slate-400 hover:text-white'}`}>
            📊 Municipal Analytics
          </button>
        </div>

        {/* Live Status Badge */}
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-2 text-xs bg-emerald-500/10 text-emerald-400 px-3 py-1.5 rounded-full border border-emerald-500/20">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            Edge Fleet Connected (Live Syncing)
          </span>
        </div>
      </header>

      {/* KPI Counters Bar */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 px-6 py-4 bg-slate-900/50 border-b border-slate-800/80">
        <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
          <div className="text-xs text-slate-400 font-medium">Total Detected Potholes</div>
          <div className="text-2xl font-black text-white mt-1">{analytics?.total_potholes || 0}</div>
        </div>
        <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
          <div className="text-xs text-red-400 font-medium flex items-center gap-1">🔴 High Severity (Critical)</div>
          <div className="text-2xl font-black text-red-400 mt-1">{analytics?.critical_high_count || 0}</div>
        </div>
        <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
          <div className="text-xs text-amber-400 font-medium">🟠 Repairs In Progress</div>
          <div className="text-2xl font-black text-amber-400 mt-1">{analytics?.in_repair_count || 0}</div>
        </div>
        <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
          <div className="text-xs text-emerald-400 font-medium">🟢 Auto-Verified Fixed</div>
          <div className="text-2xl font-black text-emerald-400 mt-1">{analytics?.repaired_count || 0}</div>
        </div>
        <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800">
          <div className="text-xs text-indigo-400 font-medium">⚡ Fleet Repair Velocity</div>
          <div className="text-2xl font-black text-indigo-400 mt-1">{analytics?.repair_rate_percentage || 0}%</div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* MAP VIEW */}
        {activeTab === 'map' && (
          <div className="flex-1 flex relative">
            {/* Filter Floating Overlay */}
            <div className="absolute top-4 left-4 z-[1000] bg-slate-900/90 backdrop-blur-md p-3 rounded-xl border border-slate-700/80 shadow-2xl flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 font-semibold uppercase">Severity:</span>
                <select 
                  value={filterSeverity} 
                  onChange={e => setFilterSeverity(e.target.value)}
                  className="bg-slate-800 text-white text-xs px-2.5 py-1.5 rounded-lg border border-slate-700 outline-none">
                  <option value="ALL">All Severities</option>
                  <option value="HIGH">High Only</option>
                  <option value="MEDIUM">Medium Only</option>
                  <option value="LOW">Low Only</option>
                </select>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 font-semibold uppercase">Status:</span>
                <select 
                  value={filterStatus} 
                  onChange={e => setFilterStatus(e.target.value)}
                  className="bg-slate-800 text-white text-xs px-2.5 py-1.5 rounded-lg border border-slate-700 outline-none">
                  <option value="ALL">All Statuses</option>
                  <option value="PENDING">Pending Action</option>
                  <option value="ASSIGNED">Assigned to Contractor</option>
                  <option value="IN_REPAIR">In Repair</option>
                  <option value="VERIFIED_FIXED">Verified Fixed</option>
                </select>
              </div>
            </div>

            {/* Map Container Element */}
            <div ref={mapRef} className="flex-1 w-full h-full z-0"></div>

            {/* Selected Pothole Detail Sidebar Drawer */}
            {selectedPothole && (
              <div className="w-96 bg-slate-900 border-l border-slate-800 p-5 overflow-y-auto flex flex-col justify-between z-10 shadow-2xl">
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
                      className="text-slate-400 hover:text-white text-lg font-bold p-1">
                      ✕
                    </button>
                  </div>

                  {/* Snapshot Image Preview */}
                  <div className="mt-4 rounded-xl overflow-hidden bg-slate-950 border border-slate-800 h-48 flex items-center justify-center">
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
                  <div className="mt-4 space-y-2.5 text-xs">
                    <div className="flex justify-between py-1.5 border-b border-slate-800">
                      <span className="text-slate-400">Status</span>
                      <span className="font-bold text-amber-400">{selectedPothole.status}</span>
                    </div>
                    <div className="flex justify-between py-1.5 border-b border-slate-800">
                      <span className="text-slate-400">GPS Coordinates</span>
                      <span className="font-mono text-slate-200">{selectedPothole.latitude}, {selectedPothole.longitude}</span>
                    </div>
                    <div className="flex justify-between py-1.5 border-b border-slate-800">
                      <span className="text-slate-400">Vehicle Scanner Tag</span>
                      <span className="font-mono text-indigo-400">{selectedPothole.vehicle_id}</span>
                    </div>
                    <div className="flex justify-between py-1.5 border-b border-slate-800">
                      <span className="text-slate-400">Re-scan Count (Deduplicated)</span>
                      <span className="font-bold text-white bg-slate-800 px-2 py-0.5 rounded">{selectedPothole.scan_count} times</span>
                    </div>
                    <div className="flex justify-between py-1.5 border-b border-slate-800">
                      <span className="text-slate-400">Contractor Assigned</span>
                      <span className="text-slate-300 font-medium">{selectedPothole.assigned_contractor || 'Unassigned'}</span>
                    </div>
                  </div>

                  {/* Assign Contractor Action */}
                  <div className="mt-5 bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <label className="text-xs text-slate-400 block mb-1 font-medium">Assign Repair Contractor:</label>
                    <div className="flex gap-2">
                      <input 
                        type="text" 
                        placeholder="e.g. PWD Zone 4 Infra" 
                        value={assignContractorInput}
                        onChange={e => setAssignContractorInput(e.target.value)}
                        className="bg-slate-900 border border-slate-700 text-xs px-2.5 py-1.5 rounded-lg flex-1 text-white outline-none"
                      />
                      <button 
                        onClick={() => {
                          if (assignContractorInput) {
                            handleUpdateStatus(selectedPothole.id, 'ASSIGNED', assignContractorInput);
                            setAssignContractorInput('');
                          }
                        }}
                        className="bg-amber-500 text-slate-950 font-bold text-xs px-3 py-1.5 rounded-lg hover:bg-amber-400 transition">
                        Assign
                      </button>
                    </div>
                  </div>
                </div>

                {/* Workflow Actions Footer */}
                <div className="mt-6 space-y-2">
                  <button 
                    onClick={() => handleUpdateStatus(selectedPothole.id, 'IN_REPAIR')}
                    className="w-full bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs py-2 rounded-xl border border-slate-700 transition">
                    🚜 Mark Repair In Progress
                  </button>
                  <button 
                    onClick={() => handleVerifyRepair(selectedPothole.id)}
                    className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs py-2.5 rounded-xl shadow-lg shadow-emerald-600/20 transition flex items-center justify-center gap-2">
                    ✅ Trigger Auto-Scan Verification (Fixed)
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* WORK ORDERS LIST VIEW */}
        {activeTab === 'list' && (
          <div className="flex-1 p-6 overflow-y-auto">
            <h2 className="text-xl font-bold text-white mb-4">Municipal Work Orders & Inspection Log</h2>
            <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-xl">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 uppercase font-semibold border-b border-slate-800">
                  <tr>
                    <th className="p-3.5">ID</th>
                    <th className="p-3.5">Defect Class</th>
                    <th className="p-3.5">Severity</th>
                    <th className="p-3.5">Coordinates</th>
                    <th className="p-3.5">Scan Count</th>
                    <th className="p-3.5">Status</th>
                    <th className="p-3.5">Assigned Contractor</th>
                    <th className="p-3.5 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-300">
                  {potholes.map(p => (
                    <tr key={p.id} className="hover:bg-slate-800/50 transition">
                      <td className="p-3.5 font-bold text-white">#{p.id}</td>
                      <td className="p-3.5">{p.class_name}</td>
                      <td className="p-3.5">
                        <span className={`px-2 py-0.5 rounded font-bold ${
                          p.severity === 'HIGH' ? 'text-red-400 bg-red-500/10' :
                          p.severity === 'MEDIUM' ? 'text-amber-400 bg-amber-500/10' :
                          'text-yellow-400 bg-yellow-500/10'
                        }`}>{p.severity}</span>
                      </td>
                      <td className="p-3.5 font-mono">{p.latitude}, {p.longitude}</td>
                      <td className="p-3.5 font-bold text-white">{p.scan_count}x</td>
                      <td className="p-3.5 font-semibold text-amber-400">{p.status}</td>
                      <td className="p-3.5">{p.assigned_contractor || '-'}</td>
                      <td className="p-3.5 text-right">
                        <button 
                          onClick={() => { setSelectedPothole(p); setActiveTab('map'); }}
                          className="bg-slate-800 hover:bg-slate-700 text-amber-400 px-3 py-1 rounded border border-slate-700">
                          Inspect on Map
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ANALYTICS VIEW */}
        {activeTab === 'analytics' && (
          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            <h2 className="text-xl font-bold text-white">Municipal Infrastructure Governance & Repair Metrics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800">
                <h3 className="text-sm font-bold text-slate-300 mb-3">Severity Breakdown</h3>
                <div className="space-y-3 text-xs">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span>Critical High Severity</span>
                      <span className="font-bold text-red-400">{analytics?.critical_high_count}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div className="bg-red-500 h-full" style={{ width: `${(analytics?.critical_high_count / (analytics?.total_potholes || 1)) * 100}%` }}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between mb-1">
                      <span>Medium Severity</span>
                      <span className="font-bold text-amber-400">{analytics?.medium_count}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div className="bg-amber-500 h-full" style={{ width: `${(analytics?.medium_count / (analytics?.total_potholes || 1)) * 100}%` }}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between mb-1">
                      <span>Low Severity</span>
                      <span className="font-bold text-yellow-400">{analytics?.low_count}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div className="bg-yellow-500 h-full" style={{ width: `${(analytics?.low_count / (analytics?.total_potholes || 1)) * 100}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800">
                <h3 className="text-sm font-bold text-slate-300 mb-3">SIH Differentiators & Edge AI Stats</h3>
                <ul className="space-y-2.5 text-xs text-slate-400">
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-400">✓</span> <strong>Spatial Deduplication:</strong> Prevents duplicate alerts when multiple garbage trucks pass the same pothole.
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-400">✓</span> <strong>On-Device Offline Edge Buffer:</strong> Works without continuous 4G connectivity using SQLite buffer.
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-400">✓</span> <strong>Automated Repair Verification:</strong> Automatically checks if pothole is fixed when vehicle re-scans area.
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
