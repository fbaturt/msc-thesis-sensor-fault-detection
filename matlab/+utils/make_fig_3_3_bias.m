function out_path = make_fig_3_3_bias(cfg, noise_name, seed, phase_focus, bias_mag_kt)
%MAKE_FIG_3_3_BIAS Generate Chapter 3 Figure 3.3 (Bias fault example).

    arguments
        cfg struct
        noise_name (1,1) string = "med"
        seed (1,1) double = 1
        phase_focus (1,1) string {mustBeMember(phase_focus, ["climb","descent"])} = "climb"
        bias_mag_kt (1,1) double = 10
    end

    utils.set_seed(seed);

    [t, V_clean, phase] = sim.generate_profile(cfg);

    sigma = cfg.noise_levels.(noise_name);
    V_noisy = sim.add_noise(V_clean, sigma);

    tf = pick_fault_time_in_phase(t, phase, phase_focus, 0.30, 0.60);

    [V_faulty, ~] = faults.inject_bias(t, V_noisy, tf, bias_mag_kt);

    if ~exist(cfg.out_fig_dir, "dir")
        mkdir(cfg.out_fig_dir);
    end

    run_id = "fig3_3_bias_" + noise_name + "_seed_" + string(seed) + "_phase_" + phase_focus;
    out_path = fullfile(cfg.out_fig_dir, char(run_id + ".png"));

    fig = figure("Visible","on");
    set(fig, "Color", "w");
    set(fig, "Position", [100 100 900 500]);
    set(gca, "FontSize", 12);

    plot(t, V_clean, "LineWidth", 1.2); hold on;
    plot(t, V_noisy, "LineWidth", 1.0);
    plot(t, V_faulty, "LineWidth", 1.0);

    % Fault onset marker (MATLAB-version compatible)
    xl = xline(tf, "--");
    xl.Label = "Fault onset";
    xl.LabelOrientation = "aligned";

    grid on;
    box on;
    xlabel("Time (s)");
    ylabel("Airspeed (kt)");
    title("Constant Bias Fault Example");
    legend("Clean", "Noisy", "Faulty", "Location", "best");

    exportgraphics(fig, out_path, "Resolution", 600);
end

function tf = pick_fault_time_in_phase(t, phase, target_phase, p_lo, p_hi)
    idx = find(phase == target_phase);
    if isempty(idx)
        error("Requested phase '%s' not found in 'phase' array.", target_phase);
    end
    t_phase = t(idx);
    t_lo = t_phase(1) + p_lo * (t_phase(end) - t_phase(1));
    t_hi = t_phase(1) + p_hi * (t_phase(end) - t_phase(1));
    tf = t_lo + (t_hi - t_lo) * rand();
end