TODO

- fix longhor on rpi4
- test upgrading baseline longhorn to new version
- test rpi4 overlay to increase default replicas to 2
- test upgrade rpi4 longhorn version only

- above tests with ingress-nginx

- test with a single monolithic fleet.yaml that wraps multiple helm charts

test troubleshooting
- can I do a helm uninstall of an application that for some reason is failing and will fleet redploy automatically


# Overlays
You can define the overlays in the same directory as the application but with different values file:
base/longhorn/fleet.yaml - helm chart definition and target clusters. For any overlay you need to make sure it is defined as a separate target and a separate values file:


## Overriding values 
```
defaultNamespace: longhorn-system

helm:
  chart: longhorn
  repo: https://charts.longhorn.io
  # TODO test upgrade path from 1.8.0 to latest
  version: 1.8.1
  releaseName: longhorn
  valuesFiles:
    - values.yaml

targets:
  - name: default-all
    clusterGroup: all-clusters
  
  - name: rpi4-override
    clusterName: rpi4
    helm:
      valuesFiles:
        - values.yaml # baseline first
        - rpi4.yaml  # override second
```

## Overriding helm chart versions
Same as overriding values but target the targets[].helm.version
```

```

