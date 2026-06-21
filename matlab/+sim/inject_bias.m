function [V_faulty, fault_mask] = inject_bias(t, V_in, t_fault, bias_mag)
%INJECT_BIAS Adds constant bias after t_fault.

fault_mask = t >= t_fault;
V_faulty = V_in;
V_faulty(fault_mask) = V_in(fault_mask) + bias_mag;
end