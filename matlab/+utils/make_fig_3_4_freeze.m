function out_path = make_fig_3_4_freeze(cfg, noise_name, seed, phase_focus)
%MAKE_FIG_3_4_FREEZE Generate Chapter 3 Figure 3.4 (Frozen signal fault example).
%
%   out_path = make_fig_3_4_freeze(cfg, noise_name, seed, phase_focus)

    arguments
        cfg struct
        noise_name (1,1) string = "med"
        seed (1,1) double = 1
        phase_focus (1,1) string {mustBeMember(phase_focus, ["climb","descent"])} = "climb"
    end

    utils.set_seed(seed);

    % --- Generate profile
    [t, V_clean, phase] = sim.generate_profile(cfg);

    % --- Add noise
    sigma = cfg.noise_levels.(noise_name);
    V_noisy = sim.add_noise(V_clean, sigma);

    % --- Choose fault onset within requested phase (30%–60% of that phase)
    tf = pick_fault_time_in_phase(t, phase, phase_focus, 0.30, 0.60);

    % --- Inject freeze fault
    [V_faulty, ~] = faults.inject_freeze(t, V_noisy, tf);

    % --- Output directory
    if ~exist(cfg.out_fig_dir, "dir")
        mkdir(cfg.out_fig_dir);
    end

    run_id = "fig3_4_freeze_" + noise_name + "_seed_" + string(seed) + "_phase_" + phase_focus;
    out_path = fullfile(cfg.out_fig_dir, char(run_id + ".png"));

    % --- Plot (clean/noisy/faulty + fault onset only)
    fig = figure("Visible","on");
    set(fig, "Color", "w");
    set(fig, "Position", [100 100 900 500]);
    set(gca, "FontSize", 12);

    plot(t, V_clean, "LineWidth", 1.2); hold on;
    plot(t, V_noisy, "LineWidth", 1.0);
    plot(t, V_faulty, "LineWidth", 1.0);

    xl = xline(tf, "--");
    xl.Label = "Fault onset";
    xl.LabelOrientation = "aligned";

    grid on; box on;
    xlabel("Time (s)");
    ylabel("Airspeed (kt)");
    title("Frozen Signal Fault Example"); % optional; prefer caption
    legend("Clean", "Noisy", "Faulty", "Location", "best");

    exportgraphics(fig, out_path, "Resolution", 600);
    % close(fig);
end

% ======================= Local helper =======================
function tf = pick_fault_time_in_phase(t, phase, target_phase, p_lo, p_hi)
    idx = find(phase == target_phase);
    if isempty(idx)
        error("pick_fault_time_in_phase:NoPhase", ...
              "Requested phase '%s' not found in 'phase' array.", target_phase);
    end
    t_phase = t(idx);
    t_lo = t_phase(1) + p_lo * (t_phase(end) - t_phase(1));
    t_hi = t_phase(1) + p_hi * (t_phase(end) - t_phase(1));
    tf = t_lo + (t_hi - t_lo) * rand();
end