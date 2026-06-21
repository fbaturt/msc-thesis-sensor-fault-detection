function out_path = make_fig_3_2_profile(cfg, noise_name, seed)
%MAKE_FIG_3_2_PROFILE Generate Chapter 3 Figure 3.2 (Clean vs Noisy airspeed profile).
%
%   out_path = make_fig_3_2_profile(cfg, noise_name, seed)
%
% Inputs
%   cfg        : configuration struct from config_default()
%   noise_name : "low" | "med" | "high"
%   seed       : random seed for reproducibility
%
% Output
%   out_path   : full path to saved PNG

    arguments
        cfg struct
        noise_name (1,1) string = "med"
        seed (1,1) double = 1
    end

    % --- Reproducibility
    utils.set_seed(seed);

    % --- Generate clean profile
    % Expect: [t, V_clean, phase] or [t, V_clean]
    try
        [t, V_clean, ~] = sim.generate_profile(cfg);
    catch
        [t, V_clean] = sim.generate_profile(cfg);
    end

    % --- Add noise
    sigma = cfg.noise_levels.(noise_name);
    V_noisy = sim.add_noise(V_clean, sigma);

    % --- Prepare output directory (use same figure folder)
    if ~isfield(cfg, "out_fig_dir") || strlength(string(cfg.out_fig_dir)) == 0
        cfg.out_fig_dir = fullfile(pwd, "output", "figures");
    end
    if ~exist(cfg.out_fig_dir, "dir")
        mkdir(cfg.out_fig_dir);
    end

    run_id = "fig3_2_profile_" + noise_name + "_seed_" + string(seed);
    out_path = fullfile(cfg.out_fig_dir, char(run_id + ".png"));

    % --- Create figure (match style across thesis figures)
    fig = figure("Visible","on");
    set(fig, "Color", "w");
    set(gcf, "Position", [100 100 900 500]); % consistent canvas
    ax = gca;
    set(ax, "FontSize", 12);

    % Plot
    plot(t, V_clean, "LineWidth", 1.2); hold on;
    plot(t, V_noisy, "LineWidth", 1.0);

    grid on; box on;
    xlabel("Time (s)");
    ylabel("Airspeed (kt)");

    % Title is optional; for thesis, caption usually replaces title
    title("Simulated Airspeed Profile (Clean vs Noisy)");

    legend("Clean", "Noisy", "Location", "best");

    % --- Export high quality image
    drawnow;
    exportgraphics(gcf, out_path, "Resolution", 600);

    % Keep open for debugging; close for batch production if desired
    % close(fig);
end