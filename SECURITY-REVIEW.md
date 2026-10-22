# Runtime TLS material hygiene — 2026-10-22

Remove historical private TLS material from the current source tree and keep newly issued local credentials outside Git and Docker build contexts. Git history is retained. This change does not revoke historical material, prove absence of prior access, or establish the state of any deployed service. No production environment was contacted or changed.

The review clone preserves original evidence only under ignored `.secret/credential-evidence-20261022/` (directories 700, files 600). Do not use these archived files for development or deployment. Public certificates are distinct from private keys.

## Local development

Provide a **new**, development-only certificate/private-key PEM at `.secret/stunnel/cert.pem`, with directory permissions 700 and file permissions 600. Do not copy the archived material back. The stunnel config and development HTTP listeners now bind loopback. The launcher exits before starting services if the local PEM is absent. This is a development launcher, not a production deployment procedure.

Four standard-library regression tests run with a clean environment and network denied. They check the current Git index for private-key headers/containers, Git/Docker exclusions, local listener/configuration and refusal to start when local TLS material is missing. No legacy dependencies or app startup hooks were executed.

## Before any build or deployment

The legacy Dockerfile expects an SSH credential in its build context and clones a separate remote source. The new Docker exclusions deliberately block sending such credentials to the builder. The existing Docker build is not verified or ready to publish; replace that source-fetch mechanism with an authenticated build system that never persists private material in image layers, and attest the intended source commit. Do not remove exclusions to make a build pass. The legacy Python/framework dependencies require separate supported-version migration and compatibility verification.

The service owner must inventory historical key use and repository/image/artifact access, preserve provider and access logs privately, determine whether keys were reused, issue replacements where required, switch consumers and retire old material according to impact. Expired historical certificates do not prove the underlying key was never reused. No revocation or history rewrite has been performed. Hosting/deployment mappings, running versions, backups and operations remain unverified.

For staging, identify the actual hosting source, deployment/image ID and runtime, use newly issued environment-specific credentials, and exercise dummy users/data before requesting production authorization. Rollback retains baseline commit and prior deployment metadata; use a forward fix or restrict entry points rather than restoring published keys or credential-bearing image builds. No schema/data changes are included.
