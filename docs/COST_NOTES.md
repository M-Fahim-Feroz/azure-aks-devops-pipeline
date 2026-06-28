# Cost Notes — Azure AKS DevOps Pipeline

> [!CAUTION]
> This project provisions **real Azure resources** that incur ongoing charges. Always destroy resources after testing.

## Estimated Monthly Cost (Southeast Asia Region)

| Resource | SKU / Config | Estimated Cost |
|---|---|---|
| AKS Node Pool | 1× Standard_DS2_v2 (2 vCPU, 7 GB RAM) | ~$70–90/month |
| Azure Container Registry | Basic tier | ~$5/month |
| Azure Load Balancer | Standard | ~$20/month |
| Azure Storage Account | LRS (file share for PostgreSQL) | <$1/month |
| Virtual Network / Subnet | Standard | Free |
| Terraform State Storage | LRS blob (tiny state file) | <$1/month |
| **Total (approximate)** | | **~$96–116/month** |

> Costs vary by region, usage, and Azure pricing updates. Always check the [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/).

## Cost Reduction Tips

- **Stop the node pool** when not in use (AKS does not support pause, but you can scale to 0 manually).
- **Use Azure for Students** subscription — $100 free credit, no credit card required.
- **Destroy after demo** — the full stack can be rebuilt in ~10 minutes with a `workflow_dispatch` trigger.

## Destroy Everything

```bash
# Fastest — deletes all application resources
az group delete --name azure-aks-devops-rg --yes --no-wait

# Optional — deletes Terraform state storage (do this LAST)
az group delete --name terraform-state-rg --yes --no-wait
```

## What is NOT Covered by Azure for Students

- Standard Load Balancers may consume free credit faster.
- AKS node VMs are the largest cost driver — consider `Standard_B2s` to reduce cost.
