if [ "$(ansible all --inventory your_inventory_file --list-hosts | tail -n +2 | wc -l)" -eq 1 ]; then
  ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i your_inventory_file playbooks/playbook1.yml
else
  echo "Playbook skipped: inventory has more than one host."
fi


# kubectl get clusters.management.cattle.io -o json | jq -r '.items[] | select(.metadata.annotations["management.cattle.io/cluster-display-name"] == "rke2-prod") | .metadata.name'
