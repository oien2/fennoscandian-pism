load('PISMprecipinput.mat')
load('PISMtempinput.mat')

precipitation = permute(climprecip, [2, 1, 3]);
temp = permute(climtemp, [2, 1, 3]);

nccreate('modernclimate.nc', 'precipitation', 'Dimensions', {'lon', 101, 'lat', 60, 'time', 12}, 'Format', '64bit');
nccreate('modernclimate.nc', 'air_temp', 'Dimensions', {'lon', 101, 'lat', 60, 'time', 12}, 'Format', '64bit');

nccreate('modernclimate.nc', 'lat','Dimensions', {'lat', 60});

nccreate('modernclimate.nc', 'lon','Dimensions', {'lon', 101});


ncwrite('modernclimate.nc', 'precipitation', precipitation);
ncwrite('modernclimate.nc', 'air_temp', temp);
ncwrite('modernclimate.nc', 'lat', lat(:,1));
ncwrite('modernclimate.nc', 'lon', lon(1,:));
