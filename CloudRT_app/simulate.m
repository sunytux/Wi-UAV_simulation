function [ conf, result ] = simulate( conf, resultDir)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
    RESULT_DIR = [resultDir, '/result'];
    CONF_FILE = [resultDir, '/configure.json'];
    
    %% Simulation
    conf.callRT(CONF_FILE);

    %% Load and Analyze result
    result = MatResult;
    result.LoadByDir(RESULT_DIR);

end

