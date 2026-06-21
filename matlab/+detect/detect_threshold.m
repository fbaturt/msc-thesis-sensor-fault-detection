function F = detect_threshold(t, V, cfg)
%DETECT_THRESHOLD Absolute limits + jump limit.

F = zeros(size(V));

% Absolute bounds
abs_bad = (V < cfg.Vmin) | (V > cfg.Vmax);

% Jump limit (convert kt/s to per-sample)
jump_limit = cfg.jump_max_kt_per_s * cfg.dt;
dV = [0; abs(diff(V))];
jump_bad = dV > jump_limit;

F(abs_bad | jump_bad) = 1;
end