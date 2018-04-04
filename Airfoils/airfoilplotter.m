clc
close all
clear all

fid= fopen('airfoils/USNPS4.dat','r'); % Filename can be changed as required
Coor = fscanf(fid,'%g %g',[2 Inf]) ; 
fclose(fid) ; 
Coorpr = Coor';

hold on
plot(Coorpr(:,1),Coorpr(:,2),'b');    %plot upper surface coords
%plot(X_vect,C,'r');                  %plot class function
axis([0,1,-0.5,0.5]);
