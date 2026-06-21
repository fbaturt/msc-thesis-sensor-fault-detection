function V_noisy = add_noise(V_clean, sigma)
%ADD_NOISE Additive Gaussian noise.
V_noisy = V_clean + sigma * randn(size(V_clean));
end