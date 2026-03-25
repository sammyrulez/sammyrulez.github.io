---
title: "top Putting Secrets in Your Repo. Seriously."
date: 2026-03-27 22:48
tag:
- devops
- terraform
- secops
- dataengineering
category: blog
author: samreghenzi
description:  "How we integrated OCI Vault with Terraform to manage secrets properly — and why the side effects are even better than the main benefit."
---

# Stop Putting Secrets in Your Repo. Seriously.

We've all been there. You're setting up a new microservice, you need a database connection string, a Keycloak client secret, an OCIR auth token — and before you know it, you're copy-pasting credentials into a `.tfvars` file and telling yourself *"I'll fix this later"*.

Later never comes. Until it does, and it's painful.

This post walks through how we wired up **OCI Vault** with **Terraform** to manage secrets properly — and why the side effects are even better than the main benefit.

---

## The Problem with `TF_VAR_` and Plain tfvars

The classic approach for passing secrets to Terraform is either:

- `export TF_VAR_my_secret="..."` before every apply
- A `secrets.tfvars` file conveniently added to `.gitignore` (and inevitably forgotten on a new machine)

Both approaches work until they don't:

- A new team member clones the repo and has no idea what secrets to set
- CI/CD needs the secret injected as a pipeline variable — now you're duplicating it
- Someone accidentally commits the file. It happens.
- You rotate a credential and have to remember every place it's used

The real issue is that secrets live **outside your infrastructure definition**. They're implicit, undocumented, and fragile.

---

## Enter OCI Vault

OCI Vault is Oracle Cloud's managed secret store. Think of it as a safe deposit box that Terraform can open at plan/apply time. You store the secret once, reference it by OCID, and Terraform fetches the value directly — no environment variables, no hidden files.

### Creating a secret

```bash
oci vault secret create-base64 \
  --compartment-id $COMPARTMENT_ID \
  --vault-id $VAULT_OCID \
  --key-id $KEY_OCID \
  --secret-name "my-service-db-password" \
  --secret-content-content "$(echo -n 'supersecret' | base64)"
```

That's it. The secret now has an OCID you can reference anywhere.

---

## Wiring It Into Terraform

The integration is clean. Declare a `data` source, decode the content, use it where you need it:

```hcl
data "oci_secrets_secretbundle" "db_password" {
  secret_id = var.db_password_secret_ocid
}

module "microservice" {
  ...
  app_secrets = {
    Oracle__ConnectionString = base64decode(
      data.oci_secrets_secretbundle.db_password.secret_bundle_content[0].content
    )
  }
}
```

Your `common.tfvars` now contains only an OCID — a pointer, not a value:

```hcl
db_password_secret_ocid = "ocid1.vaultsecret.oc1.eu-miami-1.amaaaaaaxxx"
```

An OCID is not a secret. You can commit it. You can share it. You can put it in a ticket. The actual value stays in the Vault, protected by IAM policies and audit logs.

---

## The Real Win: A Repo You Can Actually Share

Here's the part that doesn't get enough attention.

When your secrets live in a Vault and your repo contains only OCIDs and config, your entire infrastructure definition becomes **fully committable**. No `.gitignore` exceptions. No "ask a colleague for the secrets file". No onboarding friction.

A developer cloning the repo for the first time gets everything they need to understand the infrastructure — and with the right IAM permissions, they can run `terraform plan` immediately.

This changes the dynamic of your infrastructure code from *"mostly version controlled"* to *"fully version controlled"*. And that matters more than it sounds:

- **Pull requests for infrastructure changes are complete** — reviewers see the full picture, not just the non-sensitive half
- **Git history is trustworthy** — a `git log` on `main.tf` tells the real story of what changed and when
- **Rollbacks are safe** — checking out a previous commit gives you a working state, not a broken one missing secret references

---

## Portability Across Environments and Teams

With this setup, spinning up a new environment is a two-step operation:

1. Create the secrets in the Vault for the new environment
2. Add the OCIDs to the new `envs/staging.tfvars`

No secret synchronization. No "which version of the connection string does staging use?". The Vault is the source of truth, and Terraform reads from it at apply time.

The same applies when onboarding a new microservice. Copy the `infra_template/` directory, fill in the placeholders, point to the right Vault OCIDs — done. The template is self-documenting because there's nothing hidden.

---

## Secret Rotation Without Drama

Rotating a secret used to mean: update the value in five places, hope you didn't miss one, redeploy everything, debug the one service that broke because you forgot to update its CI variable.

With Vault:

```bash
oci vault secret update-base64 \
  --secret-id $SECRET_OCID \
  --secret-content-content "$(echo -n 'new-value' | base64)"
```

Then `terraform apply`. Terraform fetches the new value, updates the Kubernetes secret, and the pod picks it up. One place, one command, full audit trail.

---

## A Note on the Audit Trail

Every access to a Vault secret is logged in OCI Audit. You know who read what and when. This is not just a compliance checkbox — it's genuinely useful when you're debugging a production incident and need to know whether a secret was accessed or rotated in the last 24 hours.

---

## Summary

| Before | After |
|---|---|
| Secrets in `.tfvars`, gitignored | Only OCIDs in tfvars, fully committed |
| `export TF_VAR_secret=...` before every apply | No environment variables needed |
| Manual secret rotation in multiple places | One update in Vault, one `terraform apply` |
| Onboarding requires sharing secret files | Clone repo, get IAM access, run plan |
| Partial git history | Complete, trustworthy git history |

The Vault setup takes an afternoon. The benefits compound forever. It's one of those infrastructure investments that quietly pays off every single day — even when nothing goes wrong.

Especially when nothing goes wrong.
