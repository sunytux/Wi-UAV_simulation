function [ conf ] = setRxPose(conf, confFile, resultDir, x, y, z, u, v, w)
%UNTITLED6 Summary of this function goes here
%   Detailed explanation goes here
    RESULT_DIR = [resultDir, '/result'];
    CONF_FILE = confFile;
    
    conf.snapshot.Rx.x = x;
    conf.snapshot.Rx.y = y;
    conf.snapshot.Rx.z = z;
	conf.snapshot.Rx.u = u;
    conf.snapshot.Rx.v = v;
    conf.snapshot.Rx.w = w;
    
    conf.save(CONF_FILE);
    
end

