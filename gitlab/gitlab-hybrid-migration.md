# Process of moving from Gitlab Omnibus to Hybrid Architecture

## References
Current Architecture: Omnibus 1k Architecture - https://docs.gitlab.com/administration/reference_architectures/1k_users/
Target Architecture: Hybrid 2k Architecture - https://docs.gitlab.com/administration/reference_architectures/2k_users/#cloud-native-hybrid-reference-architecture-with-helm-charts-alternative
Helm Chart Advanced Configuration: https://docs.gitlab.com/charts/advanced/

## Methodoly
The 2k Hybrid Architecture supports the following workload: API: 40 RPS, Web: 4 RPS, Git (Pull): 4 RPS, Git (Push): 1 RPS. This is an increase from the existing single server Omnibus deployed in my homelab: https://docs.gitlab.com/administration/reference_architectures/1k_users/.
Notably the Hybrid 2k architecture only needs single PostgreSQL, Redis, and Gitaly component. Theoretically we should be able to deploy the stateless components (Webservice, Sidekiq, etc) in a new kubernetes deployment and keep only the Postgres, Redis, and Gitaly services on the current
running Omnibus instance. This provides a low risk path of migrating to a Hybrid deployment. We should simple swap DNS to point to the Webservices deploying via Kubernetes that are configured to the existing Omnibus instance which has only the Postgres, Redis, and Gitaly services running. 
If performance issues are seen, I should be able to roll back to the pure omnibus by swapping DNS to point back to the omnibus server and starting the webservice, sidekiq, etc services via the gitlab.rb and reconfiguring.

## Why Hybrid
Hybrid installations leverage the benefits of both cloud native and traditional compute deployments. With this, stateless components can benefit from cloud native workload management benefits while stateful components are deployed in compute VMs with Linux package installations to benefit from increased permanence.



