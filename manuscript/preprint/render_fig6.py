"""Path-traced odour clouds for Figure 6 of the manuscript (ParaView 6.1, OSPRay path tracer); the panels are put
together with labels by compose_fig6.py. Same method as manuscript/liner_contest/render_clouds.py.

Panels (v4 multi-release RANS runs; iso-surfaces the cases write every 1 s, full resolution):
  sofa_A90  sofa, releaser leaning forward 10 deg (sofa_rec-10_v4_multi): strongest audible release (s1, released
            0.2 s), 5 s later (file t = 5; it peaks at the neighbour after 3 s)
  sofa_S50  same run and camera: median silent release (s4, released 90.2 s), 15 s later (t = 105)
  elev_S50  elevator, front-row releaser (elev_v4_FL_multi): median silent release (s4, released 90.2 s), 16 s later
            (t = 106), when it peaks at the person behind
Clouds: OAV 1 (trained-panel threshold) and 20 (half of attentive observers notice); OAV 0.1 fills the room and
hides the bodies, so it is not drawn. The sofa run wrote no iso-surfaces before 59 s in the upright case, hence the
leaning-forward run (same set-up, all times kept).
Inputs: <data>/<case>/constant/geometry/*.stl and the iso files above (copied from the server cases).
Usage: pvbatch render_fig6.py <data_dir> <out_dir> [width height spp] [project]
  'project' skips the path tracing and writes <out_dir>/points_px_<scene>.json: noses and release point in pixel
  coordinates of each camera (origin top left), for the labels.
"""
import json
import sys
from pathlib import Path

import paraview.simple as ps

data, out = Path(sys.argv[1]), Path(sys.argv[2])
W, H, SPP = (int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (900, 820, 8)
PROJECT = len(sys.argv) > 6 and sys.argv[6] == "project"
out.mkdir(parents=True, exist_ok=True)
hexrgb = lambda h: [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
CLOUD = {"oav1": ("#74C476", 0.42), "oav20": ("#006D2C", 0.88)}
RELEASER, OTHER, FURNITURE, EMITTER = "#E9B48F", "#A9C6E3", "#9C9A96", "#D55E00"
FLOOR, WALL = "#D9D3CA", "#E6E1D9"

SCENES = {
    "sofa": {
        "case": "sofa_rec-10_v4_multi",
        "bodies": {"farter": RELEASER, "neighbour": OTHER, "sofa": FURNITURE, "emitter": EMITTER},
        # floor and back wall of the room (x -1.0..2.2, y -1.6..1.6)
        "planes": [([-1.0, -1.6, 0.0], [2.2, -1.6, 0.0], [-1.0, 1.6, 0.0], FLOOR),
                   ([-1.0, -1.6, 0.0], [-1.0, 1.6, 0.0], [-1.0, -1.6, 2.6], WALL)],
        "camera": ([5.15, -3.12, 2.54], [0.05, 0.0, 1.1], 30),
        "snaps": {"sofa_A90": ("5", "s1"), "sofa_S50": ("105", "s4")},
        "points": {"releaser_nose": [0.2289, -0.3, 1.1784], "neighbour_nose": [0.1, 0.3, 1.215],
                   "release": [-0.195, -0.3, 0.478]},
    },
    "elev": {
        "case": "elev_v4_FL_multi",
        "bodies": {"FL": RELEASER, "FR": OTHER, "BL": OTHER, "BR": OTHER, "emitter": EMITTER},
        # car 1.4 (x, door at x = 1.4) x 1.1 (y) x 2.1 m: floor, back wall and the far side wall
        "planes": [([0.0, -0.55, 0.0], [1.4, -0.55, 0.0], [0.0, 0.55, 0.0], FLOOR),
                   ([0.0, -0.55, 0.0], [0.0, 0.55, 0.0], [0.0, -0.55, 2.1], WALL),
                   ([0.0, 0.55, 0.0], [1.4, 0.55, 0.0], [0.0, 0.55, 2.1], WALL)],
        "camera": ([0.95, -4.6, 2.0], [0.7, 0.0, 1.05], 31),
        "snaps": {"elev_S50": ("106", "s4")},
        "points": {"releaser_nose": [1.05, -0.27, 1.59], "behind_nose": [0.55, -0.27, 1.59],
                   "release": [0.755, -0.27, 0.83]},
    },
}


def make_view():
    view = ps.CreateRenderView()
    view.ViewSize = [W, H]
    view.OrientationAxesVisibility = 0
    view.UseColorPaletteForBackground = 0
    view.BackgroundColorMode = "Single Color"
    view.Background = [1, 1, 1]
    view.Backgroundmode = "Backplate"  # white backdrop that does not light the scene
    view.EnableRayTracing = 1
    view.BackEnd = "OSPRay pathtracer"
    view.SamplesPerPixel = SPP
    view.Denoise = 1
    view.Shadows = 1
    view.AmbientSamples = 1
    view.KeyLightElevation, view.KeyLightAzimuth, view.KeyLightIntensity = 55, 25, 0.9
    return view


def show(view, src, colour, opacity=1.0):
    d = ps.Show(src, view)
    d.ColorArrayName = [None, ""]
    d.AmbientColor = d.DiffuseColor = hexrgb(colour)
    d.Opacity = opacity
    d.Specular = 0.15
    return d


for scene, cfg in SCENES.items():
    case = data / cfg["case"]
    view = make_view()
    for name, col in cfg["bodies"].items():
        show(view, ps.STLReader(FileNames=[str(case / f"constant/geometry/{name}.stl")]), col)
    for o, p1, p2, col in cfg["planes"]:
        show(view, ps.Plane(Origin=o, Point1=p1, Point2=p2), col)
    clouds = {snap: [show(view, ps.LegacyVTKReader(FileNames=[str(case / f"postProcessing/isoSurfaces/{t}/{s}_{lev}.vtk")]),
                          c, op) for lev, (c, op) in CLOUD.items()]
              for snap, (t, s) in cfg["snaps"].items()}
    ps.Render(view)  # the first render resets the camera, so set it afterwards
    pos, focal, angle = cfg["camera"]
    view.CameraPosition, view.CameraFocalPoint, view.CameraViewUp, view.CameraViewAngle = pos, focal, [0, 0, 1], angle
    if PROJECT:
        from vtkmodules.vtkRenderingCore import vtkCoordinate
        view.EnableRayTracing = 0
        ps.Render(view)
        ren = view.GetRenderer()
        px = {}
        for k, p in cfg["points"].items():
            c = vtkCoordinate(); c.SetCoordinateSystemToWorld(); c.SetValue(*p)
            x, y = c.GetComputedDoubleDisplayValue(ren)
            px[k] = [x * W / view.ViewSize[0], H - y * H / view.ViewSize[1]]
        (out / f"points_px_{scene}.json").write_text(json.dumps({"size": [W, H], "points": px}, indent=1))
        print(scene, px)
        continue
    for snap in cfg["snaps"]:
        for other, ds in clouds.items():
            for d in ds:
                d.Visibility = int(other == snap)
        ps.Render(view)
        ps.SaveScreenshot(str(out / f"cloud_{snap}.png"), view, ImageResolution=[W, H])
        print("wrote", out / f"cloud_{snap}.png")
    ps.Delete(view)
