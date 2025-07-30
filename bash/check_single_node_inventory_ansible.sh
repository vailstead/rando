if [ "$(ansible all --inventory your_inventory_file --list-hosts | tail -n +2 | wc -l)" -eq 1 ]; then
  ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i your_inventory_file playbooks/playbook1.yml
else
  echo "Playbook skipped: inventory has more than one host."
fi
