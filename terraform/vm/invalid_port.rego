package terraform.vm

import rego.v1

invalid_ports := ["3389"]

deny contains msg if {
    r := input.resource_changes

    sec_groups := [change | change := r[_]; change.type == "azurerm_network_security_group"]

    sec_rules := [rule | rule := sec_groups[_].change.after.security_rule]

    some rule_set in sec_rules
    some rule in rule_set
    rule.access == "Allow"
    rule.destination_port_range in invalid_ports
    
    msg := sprintf("The below ports aren't allowed in production: %v", invalid_ports)
}