function run_id = make_run_id(fault_type, noise_name, seed, phase_focus)
%MAKE_RUN_ID Unique but readable ID.
run_id = sprintf("fault_%s_noise_%s_seed_%d_phase_%s", fault_type, noise_name, seed, phase_focus);
end