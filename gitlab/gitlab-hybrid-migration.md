# Process of moving from Gitlab Omnibus to Hybrid Architecture

## References
Current Architecture: Omnibus 1k Architecture - https://docs.gitlab.com/administration/reference_architectures/1k_users/
Target Architecture: Hybrid 2k Architecture - https://docs.gitlab.com/administration/reference_architectures/2k_users/#cloud-native-hybrid-reference-architecture-with-helm-charts-alternative
Helm Chart Advanced Configuration: https://docs.gitlab.com/charts/advanced/
Gitlab Environment Toolkit (GET): https://gitlab.com/gitlab-org/gitlab-environment-toolkit 

## Questions:
1. Support of GET for on-prem homelabs - i.e. proxmox or vmware support
2. If not using GET - should the basic Helm chart be used or the Gitlab Operator

## Methodoly
The 2k Hybrid Architecture supports the following workload: API: 40 RPS, Web: 4 RPS, Git (Pull): 4 RPS, Git (Push): 1 RPS. This is an increase from the existing single server Omnibus deployed in my homelab: https://docs.gitlab.com/administration/reference_architectures/1k_users/.
Notably the Hybrid 2k architecture only needs single PostgreSQL, Redis, and Gitaly component. Theoretically we should be able to deploy the stateless components (Webservice, Sidekiq, etc) in a new kubernetes deployment and keep only the Postgres, Redis, and Gitaly services on the current
running Omnibus instance. This provides a low risk path of migrating to a Hybrid deployment. We should simple swap DNS to point to the Webservices deploying via Kubernetes that are configured to the existing Omnibus instance which has only the Postgres, Redis, and Gitaly services running. 
If performance issues are seen, I should be able to roll back to the pure omnibus by swapping DNS to point back to the omnibus server and starting the webservice, sidekiq, etc services via the gitlab.rb and reconfiguring.

## Why Hybrid
Hybrid installations leverage the benefits of both cloud native and traditional compute deployments. With this, stateless components can benefit from cloud native workload management benefits while stateful components are deployed in compute VMs with Linux package installations to benefit from increased permanence.

In a production deployment:

The stateful components, like PostgreSQL or Gitaly (a Git repository storage dataplane), must run outside the cluster on PaaS or compute instances. This configuration is required to scale and reliably service the variety of workloads found in production GitLab environments.
You should use Cloud PaaS for PostgreSQL, Redis, and object storage for all non-Git repository storage.

## Hybrid Instructions

### IMPORTANT:
Ensure hybrid chart and omnibus are using the same Gitlab version

1. (Optional) Prep Omnibus Host
Install kubectl, helm, and minio cli on the existing omnibus host. This allows for managing both the gitlab instance and the kubernetes deployment from the same VM. Optional, but makes life easy.
```
# omnibus host
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
/get_helm.sh

curl https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc && chmod +x /usr/local/bin/mc
```

2. Helm Install
```
mkdir -p /opt/gitlab-helm/ && cd /opt/gitlab-helm

# NOTE - I will be using a kubeconfig localated at /opt/gitlab-helm/kubeconfig.
export KUBECONFIG=/opt/gitlab-helm/kubeconfig

# quick check to verify kubeconfig is working
kubectl config current-context
kubectl cluster-info
kubectl get nodes

helm repo add gitlab https://charts.gitlab.io/
helm repo update

cat <<EOF > values.yaml
# Configuration File
global:
  hosts:
    domain: example.com
EOF

helm upgrade --install gitlab gitlab/gitlab \
  --namespace gitlab \
  --create-namespace \
  --version 8.10.1 \
  --values values.yaml \
  --timeout 600s
```

X. Migrate Omnibus to object storage
https://docs.gitlab.com/administration/object_storage/#migrate-to-object-storage
registry: https://docs.gitlab.com/administration/packages/container_registry/#migrate-to-object-storage-without-downtime
```
# gitlab.rb
gitlab_rails['object_store']['enabled'] = true
gitlab_rails['object_store']['proxy_download'] = true
gitlab_rails['object_store']['remote_directory'] = 'gitlab' # Bucket name
gitlab_rails['object_store']['connection'] = {
  'provider' => 'AWS', # or your provider
  'aws_access_key_id' => 'access',
  'aws_secret_access_key' => 'secret',
  'region' => 'us-west-1', # e.g., us-west-1
  'endpoint' => 'endpoint', # Optional, for custom S3-compatible services
  'path_style' => true # Set to true if using a custom S3-compatible service
}

# For GitLab uploads
gitlab_rails['object_store']['uploads']['enabled'] = true
gitlab_rails['object_store']['artifacts']['enabled'] = true
gitlab_rails['object_store']['lfs']['enabled'] = true
gitlab_rails['object_store']['packages']['enabled'] = true
gitlab_rails['object_store']['pages']['enabled'] = true
```

then reconfgiure
```
gitlab-ctl reconfigure
```

then run rake task to migrate all:
```
gitlab-rake "gitlab:uploads:migrate:all"
gitlab-rake "gitlab:artifacts:migrate"
```

and you can track progress:
```
gitlab-rails dbconsole --database main
gitlabhq_production=# SELECT count(*) AS total, sum(case when store = '1' then 1 else 0 end) AS filesystem, sum(case when store = '2' then 1 else 0 end) AS objectstg FROM uploads;
gitlabhq_production=# SELECT count(*) AS total, sum(case when file_store = '1' then 1 else 0 end) AS filesystem, sum(case when file_store = '2' then 1 else 0 end) AS objectstg FROM ci_job_artifacts;
```

X. change gitlab VM to use 1 core and 8 cpu instead of 2 core and 4 cpu
X. migrate registry from local omnibus to object storage
X. Update for prometheus TODO
X. Runner configurations
- Do runners swap automatically with DNS change?
X. Disaster recovery (backup/restore)
X. Autoscaling
x. Future Proofing (scaling)

