function F = detect_rate(t, V, phase, cfg)
%DETECT_RATE Excessive rate + frozen detection (phase-aware).

F = zeros(size(V));

% Rate (kt/s)
dVdt = [0; diff(V)] ./ cfg.dt;

% Excessive rate
rate_bad = abs(dVdt) > cfg.rate_max_kt_per_s;

% Frozen detection: only meaningful in climb/descent (avoid cruise)
active_phase = (phase == "climb") | (phase == "descent");

near_zero = abs(dVdt) < cfg.freeze_min_rate;
near_zero = near_zero & active_phase;

% Require near-zero for a continuous duration
N_hold = max(1, round(cfg.freeze_hold_s / cfg.dt));
frozen_bad = false(size(V));
count = 0;
for k = 1:numel(V)
    if near_zero(k)
        count = count + 1;
    else
        count = 0;
    end
    if count >= N_hold
        frozen_bad(k) = true;
    end
end

F(rate_bad | frozen_bad) = 1;
end