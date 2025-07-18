clear all

u    = py.importlib.import_module('xara.units.iks');
xs   = py.importlib.import_module('xsection');
veux = py.importlib.import_module('veux');
xs = py.importlib.reload(xs);


d     = 18*u.inch; % depth
b     = 20*u.inch; % width
t     =  6*u.inch; % thickness
cover =  2*u.inch;

%
% Create composite shape
%

% Create patches
flange = xs.library.Rectangle(t, d);
web    = xs.library.Rectangle(b, t).translate({0, -d/2-t/2});

% Combine into one shape
section = xs.CompositeSection({web, flange});

%
% Add reinforcement
%

% Create a shape representing a single rebar. The parameter z=2 will ensure
% this material takes priority over the concrete of the rectangular flange
bar = xs.library.Circle(0.4, z=2, mesh_scale=1, divisions=int32(10));

% Now replicate the rebar
ri  = {-(b/2-cover), -d/2-t/1.5};
rj  = {  b/2-cover , -d/2-t/1.5};
top_bars = bar.linspace(ri, rj, int32(4));

% section.add_patches(top_bars);

% section = section.translate(section.centroid);

%
% Visualization
%
artist = veux.create_artist(section.model);
artist.draw_outlines();
artist.draw_surfaces(); %field=section.torsion_warping()
artist.save("tee.glb");
% veux.serve(artist);
surfaceMeshShow(readSurfaceMesh("tee.glb"), BackgroundColor="white");
