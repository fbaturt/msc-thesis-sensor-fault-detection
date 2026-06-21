function [t, V_clean, phase] = generate_profile(cfg)
%GENERATE_PROFILE Piecewise IAS profile: climb -> cruise -> descent.

t = (0:cfg.dt:cfg.T_total).';
n = numel(t);

V_clean = zeros(n,1);
phase = strings(n,1);

% Phase indices
i1 = t < cfg.t1;
i2 = (t >= cfg.t1) & (t < cfg.t2);
i3 = t >= cfg.t2;

% Climb: linear increase V0 -> Vc
V_clean(i1) = cfg.V0 + (cfg.Vc - cfg.V0) * (t(i1) / cfg.t1);
phase(i1) = "climb";

% Cruise: constant + small sine
tau = t(i2) - cfg.t1;
V_clean(i2) = cfg.Vc + cfg.cruise_sine_amp * sin(2*pi*cfg.cruise_sine_freq * tau);
phase(i2) = "cruise";

% Descent: linear decrease Vc -> Vf
t_des = t(i3) - cfg.t2;
T_des = cfg.T_total - cfg.t2;
V_clean(i3) = cfg.Vc + (cfg.Vf - cfg.Vc) * (t_des / T_des);
phase(i3) = "descent";
end