function [V_faulty, fault_mask] = inject_freeze(t, V_in, t_fault)
%INJECT_FREEZE Freezes signal at value at t_fault.

fault_mask = t >= t_fault;
V_faulty = V_in;

idx0 = find(t >= t_fault, 1, "first");
if isempty(idx0)
    return;
end
V0 = V_in(idx0);
V_faulty(fault_mask) = V0;
end