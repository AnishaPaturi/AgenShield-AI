import { useEffect, useRef, useState } from 'react'

const AGENTS = [
  { n: '01', name: 'Manager / Router', desc: 'Coordinates workflow state, retries, and routing between every agent below.' },
  { n: '02', name: 'Hybrid AST Parser', desc: 'Converts Terraform, CloudFormation, Kubernetes, and Helm into a resolved AST — variables and conditionals included.' },
  { n: '03', name: 'Secrets Scanner', desc: 'Runs Gitleaks and TruffleHog to catch committed keys, tokens, and certificates before they ship.' },
  { n: '04', name: 'RAG Query', desc: 'Grounds every finding in current AWS/Azure/GCP docs, CIS Benchmarks, and CVE data — not a hallucinated guess.' },
  { n: '05', name: 'Security Analyst', desc: 'Claude and GPT-4o independently assess each resource; disagreement escalates to a human review queue.' },
  { n: '06', name: 'Remediation', desc: 'Writes an executable patch, not a doc link — a real diff targeting the exact resource block.' },
  { n: '07', name: 'Sandbox Validator', desc: 'Runs terraform validate, kube-linter, and a LocalStack dry-run before any patch is trusted.' },
  { n: '08', name: 'Report Generator', desc: 'Exports JSON, Markdown, HTML, SARIF, and PDF — mapped to SOC 2, HIPAA, PCI-DSS, and NIST controls.' },
]

export default function Pipeline() {
  const [visible, setVisible] = useState(new Set())
  const refs = useRef([])

  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            setVisible((prev) => new Set(prev).add(Number(e.target.dataset.i)))
          }
        })
      },
      { threshold: 0.2 }
    )
    refs.current.forEach((el) => el && obs.observe(el))
    return () => obs.disconnect()
  }, [])

  return (
    <section className="pipeline">
      <div className="section-heading">
        <span className="eyebrow">the pipeline</span>
        <h2>One upload. Eight agents. A validated patch at the end.</h2>
        <p>Each agent hands its output to the next — this is the exact order a template moves through, start to finish.</p>
      </div>
      <div className="pipeline-list">
        {AGENTS.map((a, i) => (
          <div
            key={a.n}
            ref={(el) => (refs.current[i] = el)}
            data-i={i}
            className={`pipeline-item ${visible.has(i) ? 'in' : ''}`}
            style={{ transitionDelay: `${(i % 4) * 70}ms` }}
          >
            <div className="pipeline-n">{a.n}</div>
            <div>
              <div className="pipeline-name">{a.name}</div>
              <div className="pipeline-desc">{a.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
