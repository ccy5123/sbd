"""Path-traced snapshots of the odour clouds for the contest figure (ParaView 6.1, OSPRay path tracer).

Scene: sofa duet, releaser reclined 4.5 deg (cfd/runs/sofa_rec4.5_v4_multi), bare; the same camera for both panels.
Clouds: the iso-surfaces the case writes (postProcessing/isoSurfaces/<t>/s<k>_oav{0.1,1,20}.vtk, full resolution),
about 30 s after each release: A90 (s1, released 0.2 s; file t = 30.66 s) and S90 (s3, released 60.2 s; t = 90 s).
Inputs (copied from the server case): <data>/constant/geometry/*.stl and the six iso files.
Usage: pvbatch render_clouds.py <data_dir> <out_dir> [width height spp] [project]
  'project' skips the path tracing and writes <out_dir>/points_px.json: the nose probes and the release point in pixel
  coordinates of the same camera (origin top left), for placing labels on the renders.
"""
import sys
from pathlib import Path

import paraview.simple as ps

data, out = Path(sys.argv[1]), Path(sys.argv[2])
W, H, SPP = (int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (900, 820, 8)
out.mkdir(parents=True, exist_ok=True)

hexrgb = lambda h: [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
# bodies keep the viewer's identity colours (releaser warm, neighbour cool), muted so the clouds stand out;
# clouds use one sequential green ramp, darker = stronger (OAV 0.1 faint trace, 1 trained-panel threshold, 20 noticed)
BODY = {"farter": ("#E9B48F", 1.0), "neighbour": ("#A9C6E3", 1.0), "sofa": ("#9C9A96", 1.0), "emitter": ("#D55E00", 1.0)}
# OAV 0.1 (faint trace) fills most of the room by 30 s and hides the bodies, so only OAV 1 and 20 are drawn
CLOUD = {"oav1": ("#74C476", 0.42), "oav20": ("#006D2C", 0.88)}
SNAPS = {"A90": ("30.66", "s1"), "S90": ("90", "s3")}

view = ps.CreateRenderView()
view.ViewSize = [W, H]
view.OrientationAxesVisibility = 0
view.UseColorPaletteForBackground = 0
view.BackgroundColorMode = "Single Color"
view.Background = [1, 1, 1]
view.Backgroundmode = "Backplate"  # white backdrop that does not light the scene ("Environment" renders grey, "Both" washes the floor out)
view.EnableRayTracing = 1
view.BackEnd = "OSPRay pathtracer"
view.SamplesPerPixel = SPP
view.Denoise = 1
view.Shadows = 1
view.AmbientSamples = 1
view.KeyLightElevation, view.KeyLightAzimuth, view.KeyLightIntensity = 55, 25, 0.9


def show(src, colour, opacity):
    d = ps.Show(src, view)
    d.ColorArrayName = [None, ""]
    d.AmbientColor = d.DiffuseColor = hexrgb(colour)
    d.Opacity = opacity
    d.Specular = 0.15
    return d


for name, (col, op) in BODY.items():
    show(ps.STLReader(FileNames=[str(data / f"constant/geometry/{name}.stl")]), col, op)
# floor and back wall of the room (x -1.0..2.2, y -1.6..1.6), so the bodies cast shadows
show(ps.Plane(Origin=[-1.0, -1.6, 0.0], Point1=[2.2, -1.6, 0.0], Point2=[-1.0, 1.6, 0.0]), "#D9D3CA", 1.0)
show(ps.Plane(Origin=[-1.0, -1.6, 0.0], Point1=[-1.0, 1.6, 0.0], Point2=[-1.0, -1.6, 2.6]), "#E6E1D9", 1.0)

clouds = {}
for rel, (t, s) in SNAPS.items():
    clouds[rel] = [show(ps.LegacyVTKReader(FileNames=[str(data / f"postProcessing/isoSurfaces/{t}/{s}_{lev}.vtk")]), c, o)
                   for lev, (c, o) in CLOUD.items()]

ps.Render(view)  # the first render resets the camera, so set it afterwards
view.CameraPosition = [5.15, -3.12, 2.54]
view.CameraFocalPoint = [0.05, 0.0, 1.1]
view.CameraViewUp = [0, 0, 1]
view.CameraViewAngle = 30

if len(sys.argv) > 6 and sys.argv[6] == "project":
    import json
    from vtkmodules.vtkRenderingCore import vtkCoordinate
    view.EnableRayTracing = 0
    ps.Render(view)
    ren = view.GetRenderer()
    POINTS = {"releaser_nose": [0.0403, -0.3, 1.224], "neighbour_nose": [0.1, 0.3, 1.215], "release": [-0.195, -0.3, 0.478]}
    px = {}
    for k, p in POINTS.items():
        c = vtkCoordinate(); c.SetCoordinateSystemToWorld(); c.SetValue(*p)
        x, y = c.GetComputedDoubleDisplayValue(ren)
        sx, sy = W / view.ViewSize[0], H / view.ViewSize[1]
        px[k] = [x * sx, H - y * sy]
    (out / "points_px.json").write_text(json.dumps({"size": [W, H], "points": px}, indent=1))
    print(px)
    sys.exit(0)

for rel in SNAPS:
    for r, ds in clouds.items():
        for d in ds:
            d.Visibility = int(r == rel)
    ps.Render(view)
    ps.SaveScreenshot(str(out / f"cloud_{rel}.png"), view, ImageResolution=[W, H])
    print("wrote", out / f"cloud_{rel}.png")
