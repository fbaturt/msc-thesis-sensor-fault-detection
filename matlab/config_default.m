function cfg = config_default()
%CONFIG_DEFAULT Central configuration for simulations and detection.

% --- Time base ---
cfg.fs = 10;                 % Hz
cfg.dt = 1/cfg.fs;           % s
cfg.T_total = 600;           % total duration (s)

% Phase split (seconds) - piecewise profile
cfg.t1 = 200;                % end of climb
cfg.t2 = 450;                % end of cruise (start of descent)

% --- Airspeed profile (IAS/CAS direct) ---
cfg.V0 = 140;                % kt
cfg.Vc = 250;                % kt
cfg.Vf = 160;                % kt

% Optional small cruise variability
cfg.cruise_sine_amp = 1.0;   % kt
cfg.cruise_sine_freq = 0.02; % Hz

% --- Noise levels (kt, std dev) ---
cfg.noise_levels = struct( ...
    "low", 0.5, ...
    "med", 1.0, ...
    "high", 2.0);

% --- Fault settings ---
cfg.bias_mag_kt = 10;        % +10 kt bias
cfg.freeze_min_rate = 0.2;   % kt/s threshold for "nearly zero"
cfg.freeze_hold_s = 5.0;     % seconds needed to declare freeze

% Fault onset window as fraction of phase duration
cfg.fault_onset_frac_lo = 0.30;
cfg.fault_onset_frac_hi = 0.60;

% --- Detection thresholds ---
cfg.Vmin = 60;               % kt
cfg.Vmax = 400;              % kt
cfg.jump_max_kt_per_s = 40;  % kt/s
cfg.rate_max_kt_per_s = 40;  % kt/s

% --- Monte Carlo settings ---
cfg.N_runs_per_scenario = 50;

% --- Output ---
cfg.out_dir = fullfile(pwd, "output");
cfg.out_csv_dir = fullfile(cfg.out_dir, "runs_csv");
cfg.out_fig_dir = fullfile(cfg.out_dir, "figures");
end