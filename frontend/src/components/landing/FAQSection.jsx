import React, { useState } from 'react'
import { ChevronDown, HelpCircle } from 'lucide-react'

const FAQ_ITEMS = [
  {
    id: 'iac-support',
    question: 'What Infrastructure-as-Code formats does AgentShield AI evaluate?',
    answer: 'AgentShield natively parses and analyzes Terraform (.tf, .tfvars, .tf.json), AWS CloudFormation (YAML and JSON), Kubernetes manifests (Deployments, Roles, RoleBindings, NetworkPolicies, PodSecurityStandards), Azure Resource Manager (ARM) templates, and Azure Bicep.'
  },
  {
    id: 'agent-consensus',
    question: 'How does the multi-agent consensus mechanism prevent hallucinated findings?',
    answer: 'Every candidate vulnerability discovered by the SecurityAnalystAgent undergoes independent cross-evaluation by the FindingPrioritizer and ValidatorAgent against AST structural graphs, CWE registries, and CIS Benchmark specifications. Findings that fail deterministic validation or exhibit low consensus are flagged or rejected prior to reporting.'
  },
  {
    id: 'remediation-safety',
    question: 'Does AgentShield automatically modify production cloud resources without approval?',
    answer: 'No. AgentShield strictly enforces a human-in-the-loop security paradigm. Remediation patches synthesized by the RemediationAgent are validated in isolated test sandboxes to ensure syntactic and semantic safety, and then routed to the Human Audit Queue for SecOps inspection, diff review, and authorized approval before any merge or deployment.'
  },
  {
    id: 'compliance-standards',
    question: 'What compliance frameworks are mapped during scan analysis?',
    answer: 'Scans automatically map findings to CIS Cloud Benchmarks (AWS, Azure, GCP v1.4/v1.5), SOC 2 Type II Trust Services Criteria, NIST SP 800-53 Rev 5, HIPAA Security Rule, and PCI-DSS v4.0 with downloadable audit-ready SARIF and JSON artifacts.'
  },
  {
    id: 'zero-retention',
    question: 'Is my proprietary IaC code used to train public AI foundation models?',
    answer: 'Under no circumstances. Analysis occurs within isolated private execution environments with strict zero-retention SLAs. Customer IaC templates and security topology graphs are never shared, exposed to third parties, or ingested into public LLM training datasets.'
  },
  {
    id: 'attack-path-engine',
    question: 'How does the Attack Path Engine calculate blast radiuses across clouds?',
    answer: 'The engine constructs a directed acyclic graph (DAG) connecting misconfigured IAM roles, cross-account trust boundaries, security groups, and storage endpoints. It simulates adversarial lateral movement from internet ingress points to crown-jewel data stores to calculate the compound blast radius score.'
  }
]

export default function FAQSection() {
  const [openId, setOpenId] = useState('iac-support')

  const toggle = (id) => {
    setOpenId(prev => prev === id ? null : id)
  }

  return (
    <section className="landing-section" id="faq" style={{ padding: '96px 24px', maxWidth: '1100px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '56px' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 14px',
          borderRadius: '999px',
          background: 'var(--primary-dim, rgba(167, 139, 250, 0.12))',
          border: '1px solid var(--primary-border, rgba(167, 139, 250, 0.28))',
          color: 'var(--primary, #A78BFA)',
          fontSize: '12px',
          fontFamily: 'var(--mono)',
          marginBottom: '16px',
          letterSpacing: '0.05em'
        }}>
          <HelpCircle size={14} /> ARCHITECTURAL INQUIRIES & FAQ
        </div>
        <h2 style={{ fontSize: '36px', fontWeight: 800, letterSpacing: '-0.02em', margin: '0 0 16px' }}>
          Frequently Answered Security Questions
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '16px', maxWidth: '640px', margin: '0 auto' }}>
          Technical details on multi-agent validation, zero-trust cloud boundaries, and Infrastructure-as-Code governance.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', maxWidth: '820px', margin: '0 auto' }}>
        {FAQ_ITEMS.map((item) => {
          const isOpen = openId === item.id
          return (
            <div
              key={item.id}
              style={{
                borderRadius: '12px',
                background: 'var(--surface-glass, rgba(14, 19, 34, 0.72))',
                border: isOpen
                  ? '1px solid var(--primary-border, rgba(167, 139, 250, 0.35))'
                  : '1px solid var(--border-subtle, rgba(255, 255, 255, 0.06))',
                overflow: 'hidden',
                transition: 'border-color 0.2s ease, background 0.2s ease'
              }}
            >
              <button
                type="button"
                onClick={() => toggle(item.id)}
                aria-expanded={isOpen}
                aria-controls={`faq-answer-${item.id}`}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '20px 24px',
                  background: 'none',
                  border: 'none',
                  color: 'var(--text, #F8FAFC)',
                  fontSize: '16px',
                  fontWeight: 600,
                  textAlign: 'left',
                  cursor: 'pointer',
                  gap: '16px'
                }}
              >
                <span>{item.question}</span>
                <ChevronDown
                  size={18}
                  style={{
                    transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
                    flexShrink: 0,
                    color: isOpen ? 'var(--primary)' : 'var(--text-muted)'
                  }}
                  aria-hidden="true"
                />
              </button>

              {isOpen && (
                <div
                  id={`faq-answer-${item.id}`}
                  style={{
                    padding: '0 24px 22px',
                    color: 'var(--text-muted, #94A3B8)',
                    fontSize: '14.5px',
                    lineHeight: 1.65,
                    borderTop: '1px solid var(--border-subtle, rgba(255, 255, 255, 0.04))',
                    paddingTop: '16px'
                  }}
                >
                  {item.answer}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}
