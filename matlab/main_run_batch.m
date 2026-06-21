clear; clc;
cfg = config_default();

fault_types = ["bias","freeze"];
noise_names = ["low","med","high"];
phase_focuses = ["climb","descent"];

all_rows = [];

run_counter = 0;

for ft = fault_types
  for nn = noise_names
    for pf = phase_focuses

      sigma = cfg.noise_levels.(nn);

      for r = 1:cfg.N_runs_per_scenario
        run_counter = run_counter + 1;
        seed = run_counter; % deterministic seeds

        utils.set_seed(seed);

        [t, V_clean, phase] = sim.generate_profile(cfg);
        V_noisy = sim.add_noise(V_clean, sigma);

        if pf == "climb"
          t_start = 0; t_end = cfg.t1;
        else
          t_start = cfg.t2; t_end = cfg.T_total;
        end

        tf = t_start + (cfg.fault_onset_frac_lo + (cfg.fault_onset_frac_hi-cfg.fault_onset_frac_lo)*rand) * (t_end - t_start);

        if ft == "bias"
          [V_faulty, fault_mask] = faults.inject_bias(t, V_noisy, tf, cfg.bias_mag_kt);
        else
          [V_faulty, fault_mask] = faults.inject_freeze(t, V_noisy, tf);
        end

        F_T = detect.detect_threshold(t, V_faulty, cfg);
        F_R = detect.detect_rate(t, V_faulty, phase, cfg);

        mT = eval.compute_metrics(t, fault_mask, F_T);
        mR = eval.compute_metrics(t, fault_mask, F_R);

        run_id = utils.make_run_id(ft, nn, seed, pf);
        meta = struct("fault_type",ft,"noise",nn,"seed",seed,"phase_focus",pf,"t_fault",tf);

        utils.save_run_csv(cfg, run_id, t, phase, V_clean, V_noisy, V_faulty, fault_mask, F_T, F_R, meta);

        % summary row
        row = table(string(run_id), string(ft), string(nn), string(pf), tf, ...
          mT.delay_s, mT.missed, mT.false_alarms, ...
          mR.delay_s, mR.missed, mR.false_alarms, ...
          'VariableNames', ["run_id","fault_type","noise","phase_focus","t_fault", ...
                            "T_delay_s","T_missed","T_false_alarms", ...
                            "R_delay_s","R_missed","R_false_alarms"]);
        all_rows = [all_rows; row]; %#ok<AGROW>
      end

    end
  end
end

if ~exist(cfg.out_dir, "dir"), mkdir(cfg.out_dir); end
summary_path = fullfile(cfg.out_dir, "summaries", "summary_runs.csv");
if ~exist(fileparts(summary_path), "dir"), mkdir(fileparts(summary_path)); end
writetable(all_rows, summary_path);

disp("Batch complete. Summary saved to:");
disp(summary_path);