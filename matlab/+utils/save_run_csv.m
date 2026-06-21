function save_run_csv(cfg, run_id, t, phase, V_clean, V_noisy, V_faulty, fault_mask, F_T, F_R, meta)
%SAVE_RUN_CSV Save per-run timeseries + metadata in header row style.

if ~exist(cfg.out_csv_dir, "dir"), mkdir(cfg.out_csv_dir); end

T = table(t, phase, V_clean, V_noisy, V_faulty, fault_mask, F_T, F_R);

% Add metadata fields as separate tiny table and write two files (simple)
csv_path = fullfile(cfg.out_csv_dir, run_id + ".csv");
writetable(T, csv_path);

meta_path = fullfile(cfg.out_csv_dir, run_id + "_meta.txt");
fid = fopen(meta_path, "w");
fprintf(fid, "run_id=%s\n", run_id);
fields = fieldnames(meta);
for i=1:numel(fields)
    k = fields{i};
    fprintf(fid, "%s=%s\n", k, string(meta.(k)));
end
fclose(fid);
end