import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import type { ActiveTab } from './components/Sidebar';
import { OverviewPage } from './pages/OverviewPage';
import { ConjunctionsPage } from './pages/ConjunctionsPage';
import { RiskAnalysisPage } from './pages/RiskAnalysisPage';
import { ManeuverAdvisorPage } from './pages/ManeuverAdvisorPage';
import { OrbitalVisualizationPage } from './pages/OrbitalVisualizationPage';
import { SecurityPage } from './pages/SecurityPage';
import { ScenariosPage } from './pages/ScenariosPage';
import { AuditLogsPage } from './pages/AuditLogsPage';

import { fetchSatellites, fetchConjunctions } from './services/api';
import type { SatelliteSummary, ConjunctionEvent, SignedCommandPayload } from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');
  const [liveDataMode, setLiveDataMode] = useState<boolean>(false);
  const [satellites, setSatellites] = useState<SatelliteSummary[]>([]);
  const [conjunctions, setConjunctions] = useState<ConjunctionEvent[]>([]);
  const [selectedConjunction, setSelectedConjunction] = useState<ConjunctionEvent | null>(null);
  const [signedCommand, setSignedCommand] = useState<SignedCommandPayload | null>(null);

  useEffect(() => {
    fetchSatellites(liveDataMode).then(setSatellites).catch(console.error);
    fetchConjunctions().then((conjs) => {
      setConjunctions(conjs);
      if (conjs.length > 0 && !selectedConjunction) {
        setSelectedConjunction(conjs[0]);
      }
    }).catch(console.error);
  }, [liveDataMode]);

  return (
    <div className="flex flex-col min-h-screen bg-[#0b0f19] text-gray-100 antialiased selection:bg-blue-600 selection:text-white">
      {/* Top Header Navbar */}
      <Navbar
        liveDataMode={liveDataMode}
        setLiveDataMode={setLiveDataMode}
        activeThreatCount={conjunctions.filter(c => c.risk_level !== 'SAFE').length}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Navigation Sidebar */}
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Main Content Area */}
        <main className="flex-1 p-8 overflow-y-auto max-w-7xl mx-auto w-full">
          {activeTab === 'overview' && (
            <OverviewPage
              satellites={satellites}
              conjunctions={conjunctions}
              onNavigate={setActiveTab}
            />
          )}

          {activeTab === 'conjunctions' && (
            <ConjunctionsPage
              conjunctions={conjunctions}
              onSelectConjunction={setSelectedConjunction}
              onNavigate={setActiveTab}
            />
          )}

          {activeTab === 'risk' && (
            <RiskAnalysisPage
              conjunction={selectedConjunction}
              onNavigate={setActiveTab}
            />
          )}

          {activeTab === 'maneuvers' && (
            <ManeuverAdvisorPage
              onNavigate={setActiveTab}
              setSignedCommand={setSignedCommand}
            />
          )}

          {activeTab === 'orbit3d' && (
            <OrbitalVisualizationPage conjunction={selectedConjunction} />
          )}

          {activeTab === 'security' && (
            <SecurityPage signedCommand={signedCommand} />
          )}

          {activeTab === 'scenarios' && (
            <ScenariosPage
              onNavigate={setActiveTab}
              setConjunctions={setConjunctions}
              setSignedCommand={setSignedCommand}
            />
          )}

          {activeTab === 'logs' && <AuditLogsPage />}
        </main>
      </div>
    </div>
  );
}

export default App;
