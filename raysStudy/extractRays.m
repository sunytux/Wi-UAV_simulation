function extractRays(snapShot, csvFile)
%extractRays Summary of this function goes here
%   snapShot is a snapshot mat file saved with CloudRT its name should be
%   following the convention: 'u01-t000000-ant01_snapshot_1.mat'
    warning('off','all')

	[filepath, name, ext] = fileparts(snapShot);

    user = str2num(name(2:3));
    id = str2num(name(6:11));
    ant = str2num(name(16:17));
    
    m = matfile(snapShot);

    rays = m.Rays(1, 1); % This is mandatory to load the rays struct


    for i=1:length(rays.properties)
        prop = cell2mat(rays.properties(i));
        rayType = prop(1);
        refOrder = prop(2);
        ref = cell2mat(rays.reflection(i));
        E_re = prop(5);
        E_im = prop(6);
        aoa = prop(8);
        eoa = prop(9);
        aod = prop(10);
        eod = prop(11);
        
        if refOrder == 1
            ref(2,:) = m.Rx;
        elseif refOrder == 0
            ref = [m.Rx;m.Rx];
        end

        %%% Print line 

        line = [id, user, ant, m.Tx(1,:), m.Rx(1,:), rayType, refOrder, ref(1,:), ref(2,:), E_re, E_im, aoa, eoa,aod, eod];
        dlmwrite(csvFile, line, 'delimiter',',','-append');
        
    end
end

