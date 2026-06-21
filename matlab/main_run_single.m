clear; clc;
cfg = config_default();

% Choose scenario
noise_name = "med";
sigma = cfg.noise_levels.(noise_name);
fault_type = "bias";  % "bias" or "freeze"
seed = 1;

utils.set_seed(seed);

% Generate profile
[t, V_clean, phase] = sim.generate_profile(cfg);
V_noisy = sim.add_noise(V_clean, sigma);

% Choose fault onset within climb or descent (example: climb)
phase_focus = "climb";
if phase_focus == "climb"
    t_start = 0; t_end = cfg.t1;
else
    t_start = cfg.t2; t_end = cfg.T_total;
end
tf = t_start + (cfg.fault_onset_frac_lo + (cfg.fault_onset_frac_hi-cfg.fault_onset_frac_lo)*rand) * (t_end - t_start);

% Inject fault
if fault_type == "bias"
    [V_faulty, fault_mask] = faults.inject_bias(t, V_noisy, tf, cfg.bias_mag_kt);
else
    [V_faulty, fault_mask] = faults.inject_freeze(t, V_noisy, tf);
end

% Detect
F_T = detect.detect_threshold(t, V_faulty, cfg);
F_R = detect.detect_rate(t, V_faulty, phase, cfg);

% Metrics
mT = eval.compute_metrics(t, fault_mask, F_T);
mR = eval.compute_metrics(t, fault_mask, F_R);

disp(mT); disp(mR);

% Save outputs
run_id = utils.make_run_id(fault_type, noise_name, seed, phase_focus);
meta = struct("fault_type",fault_type,"noise",noise_name,"seed",seed,"phase_focus",phase_focus,"t_fault",tf);
utils.save_run_csv(cfg, run_id, t, phase, V_clean, V_noisy, V_faulty, fault_mask, F_T, F_R, meta);
eval.make_example_plots(t, V_clean, V_noisy, V_faulty, fault_mask, F_T, F_R, cfg, run_id);