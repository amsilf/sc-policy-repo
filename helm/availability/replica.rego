package play

import rego.v1

number_of_replicas := 2

deny contains msg if {
	r := input.spec.replicas
	r < number_of_replicas

	msg := sprintf("The number of replicas should be larger than %v. The current number is %v", [number_of_replicas, r])
}