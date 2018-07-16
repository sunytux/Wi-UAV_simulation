function [ conf ] = initConf(resultDir)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here
%     clear;close all;clc;
    %% Basic Settings
    RESULT_DIR = [resultDir, '/result'];
    if (~exist(RESULT_DIR', 'dir')); mkdir(RESULT_DIR); end%if

    DRONE_IDX = 3; % Tx: index in the Txlist.mat
    USER_IDX = 3; % Rx: index in the Rxlist.mat

    CONF_FILE = [resultDir, '/configure.json'];


    %% Channel Settings
    conf = ConfigureClass;

    % Required frequency 800MHz, 900MHz, 1800MHz, 2100MHz, 2600MHz, 3600MHz
    f = conf.getFrequencyTemplate;
    f.start= 2.57e+9;
    f.end=2.63e+9;
    f.step=10e6;
    Fre = (f.start+f.end)/(2e+6);
    conf.setFrequency(f);

    %%% mechanism
    conf.setLOS(1);
    conf.setReflection(1);
    conf.setReflectionOrder(2);
    conf.setScattering(1);
    conf.setScatteringMode('Lambert'); % DirectiveMode or Lambert
    conf.setTransmission(0);
    conf.setDiffraction(0);
    conf.setOutPutFile(fullfile(RESULT_DIR, 'result.mat'));
    conf.setOutPutRays(1);


    %% Map & Material Configuration
    %%% Scenario (Map)
    conf.scenario.load(fullfile(ConfigureClass.databasePath, 'scenario', 'subrealcity.json'));

    %%% Material
    conf.material.setFrequency(f);
    conf.material.matchByLibrary(conf.scenario.getMaterialNames);

    %%% Antenna
    conf.antenna.Tx.load(fullfile(ConfigureClass.databasePath, 'antenna', 'Microstripantenna.json'));
    conf.antenna.Rx.load(fullfile(ConfigureClass.databasePath, 'antenna', 'omni_vert_pol.json'));


    %% Terminals Configuration
    % load([resultDir, '/RXlist.mat']);
    % load([resultDir, '/TXlist.mat']);

    %%% Tx (Drone)
    TxTrack = SnapshotClass.getTrackTemplate;
    TxTrack.x = 0;
    TxTrack.y = 0;
    TxTrack.z = 0;
    TxTrack.u = 0;
    TxTrack.v = 0;
    TxTrack.w = 0;

    %%% Rx (User)
    RxTrack = SnapshotClass.getTrackTemplate;
    RxTrack.x = 0;
    RxTrack.y = 0;
    RxTrack.z = 0;
    RxTrack.u = 0;
    RxTrack.v = 0;
    RxTrack.w = 0;

    conf.snapshot.setTxRx(TxTrack,RxTrack);


    %% Save Configuration
    conf.save(CONF_FILE);

end

