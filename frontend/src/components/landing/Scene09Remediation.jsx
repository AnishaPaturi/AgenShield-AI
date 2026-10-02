import { motion } from 'framer-motion'

export default function Scene09Remediation() {
  const steps = ['FINDING', 'PROPOSAL', 'SANDBOX', 'VERIFIED PATCH']

  return (
    <section
      className="cinematic-scene scene-09-remediation"
      id="remediation"
      aria-label="Autonomous Remediation"
    >
      <div className="scene-container text-center">
        {/* Split Header */}
        <div className="scene-header-split">
          <motion.div
            className="header-left"
            initial={{ opacity: 0, x: -70 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          >
            <h2 className="scene-heading-clean">
              SANDBOX-VALIDATED
              <br />
              <span className="highlight-gradient">PATCH SYNTHESIS.</span>
            </h2>
          </motion.div>

          <motion.div
            className="header-right"
            initial={{ opacity: 0, x: 70 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: false, amount: 0.3 }}
            transition={{ duration: 0.9, delay: 0.12, ease: [0.16, 1, 0.3, 1] }}
          >
            <p className="scene-header-subtext">
              Zero production regression risk: Every proposed patch is executed and verified in an isolated container sandbox.
            </p>
          </motion.div>
        </div>

        {/* Minimal Process + Subtle Floating Code Diff (Not a full IDE window) */}
        <motion.div
          className="pure-remediation-stage"
          initial={{ opacity: 0, scale: 0.96 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: false, amount: 0.3 }}
          transition={{ duration: 1.0, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        >
          {/* Subtle Progression Bar */}
          <div className="remediation-pure-flow">
            {steps.map((st, i) => (
              <span key={st} className="remediation-flow-item">
                <span className={`remediation-step-name ${i === 3 ? 'verified' : ''}`}>
                  {st}
                </span>
                {i < steps.length - 1 && <span className="remediation-flow-arrow">→</span>}
              </span>
            ))}
          </div>

          {/* Subtle Floating Code Evidence Piece */}
          <div className="floating-diff-snippet">
            <div className="diff-snippet-header">
              <span className="diff-file-tag">terraform/s3_vault.tf</span>
              <span className="diff-verified-tag">• LOCALSTACK CONTAINER VERIFIED</span>
            </div>

            <pre className="diff-code-clean">
              <code>
                <span className="code-del">-   acl    = &quot;public-read&quot;</span>
                {'\n'}
                <span className="code-add">+   acl    = &quot;private&quot;</span>
                {'\n'}
                <span className="code-add">+   server_side_encryption_configuration &#123;</span>
                {'\n'}
                <span className="code-add">
                  +     rule &#123; apply_server_side_encryption_by_default &#123; sse_algorithm = &quot;AES256&quot; &#125; &#125;
                </span>
                {'\n'}
                <span className="code-add">+   &#125;</span>
              </code>
            </pre>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
