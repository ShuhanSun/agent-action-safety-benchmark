# Threat Model

## Protected boundary

ActionGuardBench focuses on the **pre-execution boundary** between an agent's proposed action and a tool that can create an external side effect.

## Assets

- user data and credentials
- user accounts and permissions
- files and persistent state
- external communications made in the user's name
- financial or contractual commitments
- system integrity

## Adversaries and failure sources

1. **Untrusted-content attacker**: places malicious instructions in webpages, email, documents, or tool output.
2. **Malicious user request**: asks the agent to perform a prohibited or clearly unsafe action.
3. **Confused deputy**: induces an agent with broad permissions to act outside the user's authority or intent.
4. **Benign ambiguity**: incomplete user intent makes a consequential action unsafe to execute automatically.
5. **Agent planning error**: the agent proposes a side effect that is unnecessary for the requested task.

## Initial risk taxonomy

- prompt injection
- data exfiltration
- credential exposure
- destructive state changes
- over-privileged actions
- unauthorized external communication
- financial commitment
- permission escalation
- unsafe system modification

## Out of scope for v0.1

- real malware execution
- live credential access
- real financial transfers
- real email or messaging
- physical robotics
- evaluation of general harmful language

All side-effecting tools are represented as structured mock actions only.
