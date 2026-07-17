import React, { useState, useEffect } from 'react';
import { Activity, Droplets, Thermometer, AlertTriangle, CheckCircle2, ChevronDown, ChevronUp, Microscope } from 'lucide-react';
import './index.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function useHashRoute() {
  const read = () => window.location.hash.replace(/^#/, '') || '/';
  const [route, setRoute] = useState(read);
  useEffect(() => {
    const onChange = () => setRoute(read());
    window.addEventListener('hashchange', onChange);
    return () => window.removeEventListener('hashchange', onChange);
  }, []);
  return route;
}

function Header({ route }) {
  return (
    <header className="app-header" role="banner">
      <div className="header-title">
        <Microscope size={24} color="#00a4ef" aria-hidden="true" />
        <span>Microsoft Research | AquaSentinel AI</span>
      </div>
      <nav className="header-nav" aria-label="Main Navigation">
        <a href="#/" aria-current={route === '/' ? 'page' : undefined}>Dashboard</a>
        <a href="#/docs" aria-current={route === '/docs' ? 'page' : undefined}>Documentation</a>
      </nav>
    </header>
  );
}

function App() {
  const route = useHashRoute();
  return (
    <div>
      <Header route={route} />
      {route === '/docs' ? <DocsPage /> : <Dashboard />}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Dashboard (live results from the API)
// ---------------------------------------------------------------------------
function Dashboard() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/api/results`)
      .then(res => res.json())
      .then(json => {
        setData(json.results || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch data:", err);
        setError(true);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="loader-container" role="status" aria-live="polite">
        <div className="spinner" aria-hidden="true"></div>
        <p>Analyzing water samples...</p>
      </div>
    );
  }

  if (error || data.length === 0) {
    return (
      <main className="container" id="main-content">
        <h1 className="page-title">Water Biosurveillance Dashboard</h1>
        <div className="callout warn">
          <strong>No results loaded.</strong> This dashboard reads live analysis from the
          AquaSentinel API (<code>{API_BASE}/api/results</code>). Start it locally with
          {' '}<code>uvicorn api:app --reload</code>, or set <code>VITE_API_URL</code> to a
          deployed backend. The <a href="#/docs">Documentation</a> page explains the whole
          system and works without the API.
        </div>
      </main>
    );
  }

  const lowRisk = data.filter(d => d.risk === 'LOW').length;
  const highRisk = data.filter(d => d.risk === 'HIGH').length;

  return (
    <main className="container" id="main-content">
      <h1 className="page-title">Water Biosurveillance Dashboard</h1>
      <p className="page-subtitle">
        Real-time analysis of microscopic water samples. The AI identifies organisms and combines morphological data with environmental sensors (pH and Temperature) to assess contamination risk.
        {' '}New here? Read the <a href="#/docs">Documentation</a> to see how the pipeline works.
      </p>

      <section aria-labelledby="metrics-heading" className="top-metrics">
        <h2 id="metrics-heading" className="sr-only" style={{ display: 'none' }}>Overall Metrics</h2>

        <div className="top-metric-card">
          <div className="top-metric-icon" aria-hidden="true">
            <Activity size={28} />
          </div>
          <div className="top-metric-info">
            <h2>Total Samples</h2>
            <p>{data.length}</p>
          </div>
        </div>

        <div className="top-metric-card">
          <div className="top-metric-icon" style={{ color: 'var(--risk-low)' }} aria-hidden="true">
            <CheckCircle2 size={28} />
          </div>
          <div className="top-metric-info">
            <h2>Safe (Low Risk)</h2>
            <p>{lowRisk}</p>
          </div>
        </div>

        <div className="top-metric-card">
          <div className="top-metric-icon" style={{ color: 'var(--risk-high)' }} aria-hidden="true">
            <AlertTriangle size={28} />
          </div>
          <div className="top-metric-info">
            <h2>Critical (High Risk)</h2>
            <p>{highRisk}</p>
          </div>
        </div>
      </section>

      <section aria-labelledby="results-heading">
        <h2 id="results-heading" className="sr-only" style={{ display: 'none' }}>Sample Results</h2>
        <div className="dashboard-grid">
          {data.map((item) => (
            <ResultCard key={item.sample_id} data={item} />
          ))}
        </div>
      </section>
    </main>
  );
}

function ResultCard({ data }) {
  const [expanded, setExpanded] = useState(false);

  // Create a unique ID for ARIA linking
  const detailsId = `details-${data.sample_id}`;

  return (
    <article className="card">
      <div className="card-image-wrapper">
        <img
          src={data.image_url}
          alt={`Microscope view of ${data.organism}`}
          className="card-image"
        />
      </div>
      <div className="card-content">
        <div className="card-header">
          <div>
            <h3 className="card-title">{data.organism}</h3>
            <span className="card-subtitle">{data.kind} • {Math.round(data.confidence * 100)}% Confidence</span>
          </div>
          <span className={`risk-badge risk-${data.risk}`} aria-label={`Risk level: ${data.risk}`}>
            {data.risk} RISK
          </span>
        </div>

        <div className="metrics-grid">
          <div className="metric">
            <span className="metric-label">
              <Droplets size={16} aria-hidden="true" style={{marginRight:'6px'}}/>
              pH Level
            </span>
            <span className="metric-value">{data.ph !== null ? data.ph.toFixed(2) : '--'}</span>
          </div>
          <div className="metric">
            <span className="metric-label">
              <Thermometer size={16} aria-hidden="true" style={{marginRight:'6px'}}/>
              Temperature
            </span>
            <span className="metric-value">{data.temperature !== null ? `${data.temperature.toFixed(1)}°C` : '--'}</span>
          </div>
        </div>

        <div className="recommendation">
          <strong>Status:</strong> {data.status}
          <br/>
          {data.recommendation}
        </div>

        <button
          className="expand-button"
          onClick={() => setExpanded(!expanded)}
          aria-expanded={expanded}
          aria-controls={detailsId}
        >
          {expanded ? <ChevronUp size={18} aria-hidden="true" /> : <ChevronDown size={18} aria-hidden="true" />}
          {expanded ? 'Hide Analysis Details' : 'View Analysis Details'}
        </button>

        {expanded && (
          <div id={detailsId} className="reasons-list">
            <p><strong>Potential Disease:</strong> {data.disease}</p>
            <ul>
              {data.reasons.map((reason, i) => (
                <li key={i}>{reason}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </article>
  );
}

// ---------------------------------------------------------------------------
// Documentation / Overview page (fully static — no API needed)
// ---------------------------------------------------------------------------
const ORGANISMS = [
  ['Clean water', 'None', 0, 'Clear field, few particles'],
  ['Algae', 'Algae', 1, 'Large green clusters'],
  ['Cyanobacteria', 'Blue-green bacteria', 2, 'Blue-green filaments / chains'],
  ['Giardia lamblia', 'Protozoa', 2, 'Tear-drop / oval cysts'],
  ['Cryptosporidium', 'Protozoa', 2, 'Small round oocysts'],
  ['E. coli', 'Bacteria', 2, 'Many small dark rods'],
  ['Naegleria fowleri', 'Amoeba', 3, 'Few large irregular bodies'],
];

const STEPS = [
  {
    title: 'Capture the inputs',
    body: (
      <>
        <p>
          Every sample is one microscope image plus two sensor readings — <strong>pH</strong> and
          {' '}<strong>temperature</strong>. They can come from a mock pendrive (the demo default),
          manual entry, or live hardware (Arduino over USB, or a NodeMCU over Wi-Fi).
        </p>
      </>
    ),
  },
  {
    title: 'Classify the organism (the image model)',
    body: (
      <>
        <p>
          The classifier reads actual pixels — not a lookup table. It reduces each image to
          {' '}<strong>8 numeric features</strong> (mean colour, green dominance for chlorophyll,
          texture, edge density, and dark-pixel fraction at two scales to tell tiny rods from large
          blobs), then picks the nearest learned prototype per organism. A softmax over the distances
          gives the confidence and per-class probabilities.
        </p>
        <p>It chooses from seven categories:</p>
        <div className="table-scroll">
          <table className="docs-table">
            <thead>
              <tr><th>Organism</th><th>Kind</th><th>Danger (0–3)</th><th>Look</th></tr>
            </thead>
            <tbody>
              {ORGANISMS.map(([name, kind, danger, look]) => (
                <tr key={name}>
                  <td>{name}</td><td>{kind}</td><td>{danger}</td><td>{look}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </>
    ),
  },
  {
    title: 'Fuse image + sensors into a risk verdict',
    body: (
      <>
        <p>
          A deliberately transparent rule combines the three signals so every verdict can be
          explained line by line. The image says <em>which</em> organism; the sensors say
          {' '}<em>how dangerous</em> the conditions are.
        </p>
        <pre className="code-block">{`risk_score = 2 × organism_danger      (danger 0=clean … 3=severe)
           + 1  if pH outside 6.5–8.5
           + 1  if temperature > 30 °C

score ≤ 1  →  LOW        2–3  →  MODERATE        ≥ 4  →  HIGH`}</pre>
      </>
    ),
  },
  {
    title: 'Assemble one result object',
    body: (
      <p>
        The classification, organism metadata, raw pH/temperature, and the risk verdict are merged
        into a single result object. This one object is the contract every front-end renders — which
        is why the terminal, the Streamlit screen, and this website always agree.
      </p>
    ),
  },
  {
    title: 'Show it',
    body: (
      <p>
        The result is rendered as the cards on the <a href="#/">Dashboard</a>: organism, confidence,
        pH, temperature, the risk badge, a recommendation, and an expandable list of the exact
        reasons behind the verdict.
      </p>
    ),
  },
];

function DocsPage() {
  return (
    <main className="container docs" id="main-content">
      <h1 className="page-title">How AquaSentinel Works</h1>
      <p className="page-subtitle">
        AquaSentinel screens a water sample for microbial contamination in seconds. Give it a
        microscope image of a water drop plus the water&rsquo;s pH and temperature, and it identifies
        the microorganism and reports a contamination risk — an early warning, not a lab replacement.
      </p>

      <section aria-labelledby="pipeline-heading">
        <h2 id="pipeline-heading">The pipeline at a glance</h2>
        <div className="flow" role="img" aria-label="Pipeline: image and sensors flow into the classifier and fusion layer, producing a risk verdict shown on the dashboard">
          <div className="flow-node"><strong>Microscope image</strong><span>the drop of water</span></div>
          <div className="flow-arrow" aria-hidden="true">→</div>
          <div className="flow-node"><strong>Classifier</strong><span>which organism + confidence</span></div>
          <div className="flow-arrow" aria-hidden="true">→</div>
          <div className="flow-node"><strong>Fusion</strong><span>+ pH &amp; temperature → risk</span></div>
          <div className="flow-arrow" aria-hidden="true">→</div>
          <div className="flow-node"><strong>Dashboard</strong><span>verdict + recommendation</span></div>
        </div>
      </section>

      <section aria-labelledby="steps-heading">
        <h2 id="steps-heading">Step by step</h2>
        <ol className="steps">
          {STEPS.map((s, i) => (
            <li className="step" key={s.title}>
              <div className="step-num" aria-hidden="true">{i + 1}</div>
              <div className="step-body">
                <h3>{s.title}</h3>
                {s.body}
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section aria-labelledby="honesty-heading">
        <h2 id="honesty-heading">What&rsquo;s real and what&rsquo;s simulated</h2>
        <ul>
          <li><strong>Real:</strong> the classifier reads real pixels and makes a genuine prediction; the pH/temperature fusion logic is real.</li>
          <li><strong>Simulated for the demo:</strong> the microscope images and sensor readings are generated stand-ins, so the demo runs anywhere without hardware.</li>
          <li><strong>Not claimed:</strong> species-level certainty or a replacement for a laboratory. AquaSentinel is a screening and early-warning tool.</li>
        </ul>
        <div className="callout warn">
          <strong>Honest caveat.</strong> The demo classifier is validated on images from the same
          generator it learned from, so the &ldquo;matches labels&rdquo; count reflects
          self-consistency on synthetic data — not real-world accuracy. The system is built so a real
          image dataset or a fine-tuned CNN drops in without changing anything downstream.
        </div>
      </section>
    </main>
  );
}

export default App;
