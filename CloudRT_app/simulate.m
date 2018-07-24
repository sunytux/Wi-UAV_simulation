function [ conf, Re, Im ] = simulate( conf, resultDir, idx)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
    RESULT_DIR = [resultDir, '/result'];
    CONF_FILE = [resultDir, '/configure.json'];

    conf.setOutPutFile(fullfile(RESULT_DIR, ['result-', int2str(idx), '.mat']));
    conf.save(CONF_FILE);


    %% Simulation
    conf.callRT(CONF_FILE);

    load(fullfile(RESULT_DIR, ['result-', int2str(idx), '_snapshot_1.mat']));
    Re = CTF_Re(1);
    Im = CTF_Im(1);
end

