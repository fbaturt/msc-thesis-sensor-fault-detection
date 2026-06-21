function m = compute_metrics(t, fault_mask, F)
%COMPUTE_METRICS Detection delay, missed detection, false alarm count.
% fault_mask: true where fault is active
% F: detector flag (0/1)

m = struct();
m.missed = 0;
m.delay_s = NaN;
m.false_alarms = 0;

% False alarms: detections when no fault
F_nf = F(~fault_mask) > 0;
m.false_alarms = sum(diff([0; F_nf]) == 1);

% Detection time: first detection after fault starts
idx_fault_start = find(fault_mask, 1, "first");
if isempty(idx_fault_start)
    % no fault scenario (not used in your current scope, but safe)
    return;
end

idx_detect = find(( (1:numel(F))' >= idx_fault_start ) & (F > 0), 1, "first");
if isempty(idx_detect)
    m.missed = 1;
    return;
end

m.delay_s = t(idx_detect) - t(idx_fault_start);
end