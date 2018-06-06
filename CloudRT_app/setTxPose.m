function [ conf ] = setTxPose(conf, resultDir, x, y, z, u, v, w)
%UNTITLED6 Summary of this function goes here
%   Detailed explanation goes here
    RESULT_DIR = [resultDir, '/result'];
    CONF_FILE = [resultDir, '/configure.json'];
    
    conf.snapshot.Tx.x = x;
    conf.snapshot.Tx.y = y;
    conf.snapshot.Tx.z = z;
	conf.snapshot.Tx.u = u;
    conf.snapshot.Tx.v = v;
    conf.snapshot.Tx.w = w;
    
    conf.save(CONF_FILE);
    
end

