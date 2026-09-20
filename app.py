import math
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sectional Properties & Cross Section Schematic</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 12px;
            display: flex;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 18px;
            border-radius: 12px;
            max-width: 540px;
            width: 100%;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            box-sizing: border-box;
        }
        h2 {
            color: #0f172a;
            font-size: 17px;
            text-align: center;
            margin: 0 0 15px 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        label {
            font-weight: 600;
            display: block;
            margin-top: 10px;
            color: #334155;
            font-size: 13px;
        }
        select, input, textarea {
            width: 100%;
            padding: 9px;
            margin-top: 4px;
            border-radius: 6px;
            border: 1px solid #cbd5e1;
            box-sizing: border-box;
            font-size: 14px;
            font-family: inherit;
        }
        textarea {
            resize: vertical;
            height: 90px;
        }
        .helper-text {
            font-size: 11px;
            color: #64748b;
            margin-top: 3px;
        }
        button.btn-calc {
            width: 100%;
            padding: 11px;
            background: #2563eb;
            color: white;
            font-size: 15px;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            margin-top: 14px;
            cursor: pointer;
        }
        button.btn-calc:hover {
            background: #1d4ed8;
        }
        .results-box {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px 15px;
            margin-top: 16px;
        }
        .res-item {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px dashed #e2e8f0;
            font-size: 13px;
            color: #334155;
        }
        .res-item:last-child {
            border-bottom: none;
        }
        .schematic-box {
            background: #fafafa;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
            margin-top: 15px;
            position: relative;
        }
        .schematic-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .schematic-title {
            font-size: 12px;
            font-weight: 700;
            color: #475569;
            text-transform: uppercase;
        }
        .btn-maximize {
            background: #0ea5e9;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 4px 9px;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .btn-maximize:hover {
            background: #0284c7;
        }
        .svg-wrap {
            width: 100%;
            overflow-x: auto;
            text-align: center;
        }
        .legend {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 12px;
            font-size: 11px;
            margin-top: 10px;
            color: #64748b;
        }
        .legend span {
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        .err-msg {
            color: #dc2626;
            background: #fef2f2;
            padding: 10px;
            border-radius: 6px;
            margin-top: 12px;
            font-size: 13px;
        }

        /* Fullscreen Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(4px);
            align-items: center;
            justify-content: center;
            padding: 10px;
            box-sizing: border-box;
        }
        .modal-content {
            background: #ffffff;
            border-radius: 12px;
            width: 98%;
            max-width: 850px;
            height: 90vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 16px;
            background: #1e293b;
            color: white;
        }
        .modal-header h3 {
            margin: 0;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .modal-close {
            background: #ef4444;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 12px;
            font-weight: bold;
            cursor: pointer;
            font-size: 13px;
        }
        .modal-body {
            flex: 1;
            overflow: auto;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #ffffff;
            padding: 10px;
        }
    </style>
    <script>
        function updateFields() {
            var s = document.getElementById("shape").value;
            var fields = ["f_b", "f_d", "f_h", "f_dia", "f_r", "f_tsec", "f_isec", "f_uneven"];
            fields.forEach(function(id) {
                var el = document.getElementById(id);
                if (el) el.style.display = "none";
            });

            if (s === "rectangle") {
                document.getElementById("f_b").style.display = "block";
                document.getElementById("f_d").style.display = "block";
            } else if (s === "triangle") {
                document.getElementById("f_b").style.display = "block";
                document.getElementById("f_h").style.display = "block";
            } else if (s === "circle") {
                document.getElementById("f_dia").style.display = "block";
            } else if (s === "semicircle") {
                document.getElementById("f_r").style.display = "block";
            } else if (s === "tsection") {
                document.getElementById("f_tsec").style.display = "block";
            } else if (s === "isection") {
                document.getElementById("f_isec").style.display = "block";
            } else if (s === "uneven") {
                document.getElementById("f_uneven").style.display = "block";
            }
        }

        function openModal() {
            document.getElementById("fullModal").style.display = "flex";
        }
        function closeModal() {
            document.getElementById("fullModal").style.display = "none";
        }
    </script>
</head>
<body onload="updateFields()">
    <div class="container">
        <h2>CROSS SECTION & INERTIA CALCULATOR</h2>
        <form method="POST">
            <label>Select Cross Section:</label>
            <select name="shape" id="shape" onchange="updateFields()">
                <option value="uneven" {% if shape == 'uneven' %}selected{% endif %}>Uneven / Arbitrary Polygon Shape</option>
                <option value="rectangle" {% if shape == 'rectangle' %}selected{% endif %}>Rectangle Section</option>
                <option value="triangle" {% if shape == 'triangle' %}selected{% endif %}>Triangle Section</option>
                <option value="circle" {% if shape == 'circle' %}selected{% endif %}>Circular Section</option>
                <option value="semicircle" {% if shape == 'semicircle' %}selected{% endif %}>Semi-Circular Section</option>
                <option value="tsection" {% if shape == 'tsection' %}selected{% endif %}>T-Section</option>
                <option value="isection" {% if shape == 'isection' %}selected{% endif %}>I-Section</option>
            </select>

            <!-- Uneven Shape Inputs -->
            <div id="f_uneven" style="display:none;">
                <label>Polygon Coordinates (X, Y in order):</label>
                <textarea name="poly_coords">{{ request.form.get('poly_coords', '0, 0\\n140, 0\\n120, 80\\n60, 130\\n0, 90') }}</textarea>
                <div class="helper-text">Dar ek line ma X, Y coordinates lakho. Base line Y=0 consider thase.</div>
            </div>

            <!-- Standard Shapes -->
            <div id="f_b" style="display:none;">
                <label>Width / Base b (mm):</label>
                <input type="number" step="any" name="b" value="{{ request.form.get('b', '230') }}">
            </div>
            <div id="f_d" style="display:none;">
                <label>Total Depth D (mm):</label>
                <input type="number" step="any" name="d" value="{{ request.form.get('d', '450') }}">
            </div>
            <div id="f_h" style="display:none;">
                <label>Height h (mm):</label>
                <input type="number" step="any" name="h" value="{{ request.form.get('h', '300') }}">
            </div>
            <div id="f_dia" style="display:none;">
                <label>Diameter d (mm):</label>
                <input type="number" step="any" name="dia" value="{{ request.form.get('dia', '200') }}">
            </div>
            <div id="f_r" style="display:none;">
                <label>Radius r (mm):</label>
                <input type="number" step="any" name="r" value="{{ request.form.get('r', '100') }}">
            </div>

            <!-- T-Section Inputs -->
            <div id="f_tsec" style="display:none;">
                <label>Flange Width bf (mm):</label>
                <input type="number" step="any" name="t_bf" value="{{ request.form.get('t_bf', '200') }}">
                <label>Flange Thickness tf (mm):</label>
                <input type="number" step="any" name="t_tf" value="{{ request.form.get('t_tf', '30') }}">
                <label>Web Depth dw (mm):</label>
                <input type="number" step="any" name="t_dw" value="{{ request.form.get('t_dw', '170') }}">
                <label>Web Thickness tw (mm):</label>
                <input type="number" step="any" name="t_tw" value="{{ request.form.get('t_tw', '30') }}">
            </div>

            <!-- I-Section Inputs -->
            <div id="f_isec" style="display:none;">
                <label>Top Flange Width b_ft (mm):</label>
                <input type="number" step="any" name="i_bft" value="{{ request.form.get('i_bft', '150') }}">
                <label>Top Flange Thickness t_ft (mm):</label>
                <input type="number" step="any" name="i_tft" value="{{ request.form.get('i_tft', '20') }}">
                <label>Web Depth d_w (mm):</label>
                <input type="number" step="any" name="i_dw" value="{{ request.form.get('i_dw', '260') }}">
                <label>Web Thickness t_w (mm):</label>
                <input type="number" step="any" name="i_tw" value="{{ request.form.get('i_tw', '15') }}">
                <label>Bottom Flange Width b_fb (mm):</label>
                <input type="number" step="any" name="i_bfb" value="{{ request.form.get('i_bfb', '150') }}">
                <label>Bottom Flange Thickness t_fb (mm):</label>
                <input type="number" step="any" name="i_tfb" value="{{ request.form.get('i_tfb', '20') }}">
            </div>

            <button type="submit" class="btn-calc">Calculate & Draw Schematic</button>
        </form>

        {% if error %}
        <div class="err-msg">{{ error }}</div>
        {% endif %}

        {% if result %}
        <div class="results-box">
            <div class="res-item"><span>Sectional Area (A):</span> <strong>{{ result.area }} mm²</strong></div>
            <div class="res-item"><span>Distance from Base to C.G. (ȳ):</span> <strong>{{ result.y_bar }} mm</strong></div>
            <div class="res-item"><span>Centroid from Left Reference (x̄):</span> <strong>{{ result.x_bar }} mm</strong></div>
            <div class="res-item"><span>Moment of Inertia about CG (Ixx):</span> <strong>{{ result.Ixx_cg }} mm⁴</strong></div>
            <div class="res-item"><span>Moment of Inertia about CG (Iyy):</span> <strong>{{ result.Iyy_cg }} mm⁴</strong></div>
            <div class="res-item"><span>Moment of Inertia about Base (I_base):</span> <strong>{{ result.I_base }} mm⁴</strong></div>
        </div>

        <div class="schematic-box">
            <div class="schematic-header">
                <span class="schematic-title">CROSS SECTION SCHEMATIC</span>
                <button type="button" class="btn-maximize" onclick="openModal()">⛶ Maximize</button>
            </div>
            <div class="svg-wrap">
                {{ svg_card|safe }}
            </div>
            <div class="legend">
                <span><span class="dot" style="background:#ef4444;"></span> C.G. Point</span>
                <span><span class="dot" style="background:#2563eb;"></span> Neutral Axis</span>
                <span><span class="dot" style="background:#10b981;"></span> ȳ from Base</span>
            </div>
        </div>
        {% endif %}
    </div>

    <!-- Modal for Maximized View with Engineering Graph Grid -->
    <div id="fullModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>ENGINEERING GRAPH VIEW (PER UNIT SCALE)</h3>
                <button class="modal-close" onclick="closeModal()">✕ Close</button>
            </div>
            <div class="modal-body">
                <div style="width:100%; height:100%; overflow:auto; display:flex; justify-content:center; align-items:center;">
                    {{ svg_graph|safe }}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

def generate_schematic_card(shape, p):
    # Compact Card View (350x290)
    cw, ch = 350, 290
    pad_left, pad_right = 65, 45
    pad_top, pad_bot = 40, 45
    aw = cw - pad_left - pad_right
    ah = ch - pad_top - pad_bot

    coords = p['coords']
    xs = [pt[0] for pt in coords]
    ys = [pt[1] for pt in coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    w = max(max_x - min_x, 1e-4)
    h = max(max_y - min_y, 1e-4)
    x_bar = p['x_bar']
    y_bar = p['y_bar']

    scale = min(aw / w, ah / h)
    sw = w * scale
    sh = h * scale
    offset_x = pad_left + (aw - sw) / 2
    offset_y = pad_top + (ah - sh) / 2

    def to_svg(x, y):
        sx = offset_x + (x - min_x) * scale
        sy = (offset_y + sh) - (y - min_y) * scale
        return sx, sy

    svg = f'<svg width="{cw}" height="{ch}" viewBox="0 0 {cw} {ch}" xmlns="http://www.w3.org/2000/svg">'
    # Header Dimension info
    svg += f'<text x="{cw/2}" y="20" font-size="11" text-anchor="middle" fill="#0f172a" font-weight="700">Max W = {w:.1f} mm | Max H = {h:.1f} mm</text>'

    # Polygon
    pts_str = " ".join([f"{to_svg(x, y)[0]:.1f},{to_svg(x, y)[1]:.1f}" for x, y in coords])
    svg += f'<polygon points="{pts_str}" fill="#e6edf8" stroke="#1e293b" stroke-width="2"/>'

    # Base line (at min_y)
    base_y_svg = to_svg(0, min_y)[1]
    svg += f'<line x1="{offset_x-20}" y1="{base_y_svg}" x2="{offset_x+sw+20}" y2="{base_y_svg}" stroke="#64748b" stroke-width="1.5"/>'
    svg += f'<text x="{offset_x-22}" y="{base_y_svg+4}" font-size="9" text-anchor="end" fill="#64748b" font-weight="600">Base (Y=0)</text>'

    # Centroid CG
    cg_x_svg, cg_y_svg = to_svg(x_bar, y_bar)
    # Neutral Axis line
    svg += f'<line x1="{offset_x-15}" y1="{cg_y_svg}" x2="{offset_x+sw+15}" y2="{cg_y_svg}" stroke="#2563eb" stroke-dasharray="3,3" stroke-width="1.2"/>'
    svg += f'<circle cx="{cg_x_svg}" cy="{cg_y_svg}" r="4.5" fill="#ef4444"/>'
    svg += f'<text x="{cg_x_svg+6}" y="{cg_y_svg-6}" font-size="10" font-weight="bold" fill="#b91c1c">CG ({x_bar:.1f}, {y_bar:.1f})</text>'

    # Vertical dimension indicator for y_bar
    dim_x = offset_x - 12
    svg += f'<line x1="{dim_x}" y1="{base_y_svg}" x2="{dim_x}" y2="{cg_y_svg}" stroke="#10b981" stroke-width="1.5"/>'
    svg += f'<line x1="{dim_x-4}" y1="{base_y_svg}" x2="{dim_x+4}" y2="{base_y_svg}" stroke="#10b981" stroke-width="1.5"/>'
    svg += f'<line x1="{dim_x-4}" y1="{cg_y_svg}" x2="{dim_x+4}" y2="{cg_y_svg}" stroke="#10b981" stroke-width="1.5"/>'
    svg += f'<text x="{dim_x-5}" y="{(base_y_svg + cg_y_svg)/2 + 3}" font-size="9.5" text-anchor="end" fill="#047857" font-weight="bold">ȳ={y_bar:.1f}</text>'

    # Max Height indicator on right
    dim_rx = offset_x + sw + 14
    top_y_svg = to_svg(0, max_y)[1]
    svg += f'<line x1="{dim_rx}" y1="{base_y_svg}" x2="{dim_rx}" y2="{top_y_svg}" stroke="#8b5cf6" stroke-width="1.2"/>'
    svg += f'<line x1="{dim_rx-3}" y1="{base_y_svg}" x2="{dim_rx+3}" y2="{base_y_svg}" stroke="#8b5cf6" stroke-width="1.2"/>'
    svg += f'<line x1="{dim_rx-3}" y1="{top_y_svg}" x2="{dim_rx+3}" y2="{top_y_svg}" stroke="#8b5cf6" stroke-width="1.2"/>'
    svg += f'<text x="{dim_rx+5}" y="{(base_y_svg + top_y_svg)/2 + 3}" font-size="9" text-anchor="start" fill="#6d28d9" font-weight="600">H={h:.1f}</text>'

    # Vertex dots and coordinates
    for x, y in coords:
        px, py = to_svg(x, y)
        svg += f'<circle cx="{px}" cy="{py}" r="3" fill="#334155"/>'
        # Position label cleanly away from vertex
        dx_label = 5 if px >= cg_x_svg else -5
        dy_label = -5 if py <= cg_y_svg else 10
        anchor = "start" if dx_label > 0 else "end"
        svg += f'<text x="{px+dx_label}" y="{py+dy_label}" font-size="8.5" text-anchor="{anchor}" fill="#1e293b" font-weight="600">({x:g},{y:g})</text>'

    svg += '</svg>'
    return svg

def generate_schematic_graph(shape, p):
    # High-Definition Graph Mode (700x520) with MM Grid & Scaled Axes
    gw, gh = 740, 520
    pad_l, pad_r = 75, 45
    pad_t, pad_b = 45, 60
    aw = gw - pad_l - pad_r
    ah = gh - pad_t - pad_b

    coords = p['coords']
    xs = [pt[0] for pt in coords]
    ys = [pt[1] for pt in coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    w = max(max_x - min_x, 1e-4)
    h = max(max_y - min_y, 1e-4)
    x_bar = p['x_bar']
    y_bar = p['y_bar']

    # Grid span calculation
    grid_unit = 10 if max(w, h) <= 120 else (20 if max(w, h) <= 300 else 50)
    grid_min_x = math.floor(min(0, min_x) / grid_unit) * grid_unit
    grid_max_x = math.ceil(max_x / grid_unit) * grid_unit
    grid_min_y = math.floor(min(0, min_y) / grid_unit) * grid_unit
    grid_max_y = math.ceil(max_y / grid_unit) * grid_unit

    span_x = max(grid_max_x - grid_min_x, grid_unit)
    span_y = max(grid_max_y - grid_min_y, grid_unit)

    scale = min(aw / span_x, ah / span_y)

    def to_svg(x, y):
        sx = pad_l + (x - grid_min_x) * scale
        sy = (gh - pad_b) - (y - grid_min_y) * scale
        return sx, sy

    svg = f'<svg width="{gw}" height="{gh}" viewBox="0 0 {gw} {gh}" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff; border-radius:8px;">'
    
    # Background definitions for Engineering Grid
    svg += """
    <defs>
        <pattern id="smallGrid" width="10" height="10" patternUnits="userSpaceOnUse">
            <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#f1f5f9" stroke-width="0.7"/>
        </pattern>
    </defs>
    <rect width="100%" height="100%" fill="#ffffff"/>
    <rect x="{0}" y="{1}" width="{2}" height="{3}" fill="url(#smallGrid)"/>
    """.format(pad_l, pad_t, aw, ah)

    # Draw Major Grid lines & Scale Labels
    # X Grid
    val_x = grid_min_x
    while val_x <= grid_max_x:
        gx, _ = to_svg(val_x, 0)
        svg += f'<line x1="{gx}" y1="{pad_t}" x2="{gx}" y2="{gh - pad_b}" stroke="#cbd5e1" stroke-width="1"/>'
        svg += f'<text x="{gx}" y="{gh - pad_b + 16}" font-size="9" text-anchor="middle" fill="#64748b">{val_x}</text>'
        val_x += grid_unit

    # Y Grid
    val_y = grid_min_y
    while val_y <= grid_max_y:
        _, gy = to_svg(0, val_y)
        svg += f'<line x1="{pad_l}" y1="{gy}" x2="{gw - pad_r}" y2="{gy}" stroke="#cbd5e1" stroke-width="1"/>'
        svg += f'<text x="{pad_l - 8}" y="{gy + 3}" font-size="9" text-anchor="end" fill="#64748b">{val_y}</text>'
        val_y += grid_unit

    # Primary Axes (X=0 and Y=0)
    origin_x, origin_y = to_svg(0, 0)
    svg += f'<line x1="{pad_l}" y1="{origin_y}" x2="{gw - pad_r}" y2="{origin_y}" stroke="#334155" stroke-width="2"/>'
    svg += f'<line x1="{origin_x}" y1="{pad_t}" x2="{origin_x}" y2="{gh - pad_b}" stroke="#334155" stroke-width="2"/>'
    svg += f'<text x="{gw - pad_r + 8}" y="{origin_y + 4}" font-size="10" font-weight="bold" fill="#334155">X (mm)</text>'
    svg += f'<text x="{origin_x}" y="{pad_t - 10}" font-size="10" font-weight="bold" fill="#334155" text-anchor="middle">Y (mm)</text>'

    # Polygon Drawing on Graph
    pts_str = " ".join([f"{to_svg(x, y)[0]:.1f},{to_svg(x, y)[1]:.1f}" for x, y in coords])
    svg += f'<polygon points="{pts_str}" fill="rgba(37, 99, 235, 0.12)" stroke="#1e40af" stroke-width="2.5"/>'

    # Centroid on Graph
    cg_x, cg_y = to_svg(x_bar, y_bar)
    svg += f'<line x1="{pad_l}" y1="{cg_y}" x2="{gw - pad_r}" y2="{cg_y}" stroke="#2563eb" stroke-dasharray="4,4" stroke-width="1.5"/>'
    svg += f'<circle cx="{cg_x}" cy="{cg_y}" r="6" fill="#ef4444" stroke="#ffffff" stroke-width="1.5"/>'
    svg += f'<text x="{cg_x + 10}" y="{cg_y - 8}" font-size="12" font-weight="bold" fill="#b91c1c">C.G. (x̄={x_bar:.2f}, ȳ={y_bar:.2f})</text>'

    # Base to C.G. Distance Annotation
    dim_line_x = min([to_svg(x, y)[0] for x, y in coords]) - 25
    svg += f'<line x1="{dim_line_x}" y1="{origin_y}" x2="{dim_line_x}" y2="{cg_y}" stroke="#10b981" stroke-width="2"/>'
    svg += f'<polygon points="{dim_line_x},{origin_y} {dim_line_x-4},{origin_y-8} {dim_line_x+4},{origin_y-8}" fill="#10b981"/>'
    svg += f'<polygon points="{dim_line_x},{cg_y} {dim_line_x-4},{cg_y+8} {dim_line_x+4},{cg_y+8}" fill="#10b981"/>'
    svg += f'<text x="{dim_line_x - 6}" y="{(origin_y + cg_y)/2 + 4}" font-size="11" font-weight="bold" text-anchor="end" fill="#047857">Distance to CG (ȳ) = {y_bar:.2f} mm</text>'

    # Max Height Annotation
    top_y = min([to_svg(x, y)[1] for x, y in coords])
    max_line_x = max([to_svg(x, y)[0] for x, y in coords]) + 25
    svg += f'<line x1="{max_line_x}" y1="{origin_y}" x2="{max_line_x}" y2="{top_y}" stroke="#8b5cf6" stroke-width="2"/>'
    svg += f'<polygon points="{max_line_x},{origin_y} {max_line_x-4},{origin_y-8} {max_line_x+4},{origin_y-8}" fill="#8b5cf6"/>'
    svg += f'<polygon points="{max_line_x},{top_y} {max_line_x-4},{top_y+8} {max_line_x+4},{top_y+8}" fill="#8b5cf6"/>'
    svg += f'<text x="{max_line_x + 8}" y="{(origin_y + top_y)/2 + 4}" font-size="11" font-weight="bold" text-anchor="start" fill="#6d28d9">Max Height = {h:.2f} mm</text>'

    # Vertex Coordinates details with Callout Labels
    for idx, (x, y) in enumerate(coords):
        px, py = to_svg(x, y)
        svg += f'<circle cx="{px}" cy="{py}" r="4" fill="#0f172a" stroke="#ffffff" stroke-width="1"/>'
        dx = 8 if px >= cg_x else -8
        dy = -8 if py <= cg_y else 14
        anchor = "start" if dx > 0 else "end"
        svg += f'<rect x="{px + dx - (40 if anchor=="end" else 0)}" y="{py + dy - 11}" width="42" height="14" fill="rgba(255,255,255,0.85)" rx="3"/>'
        svg += f'<text x="{px + dx}" y="{py + dy}" font-size="10" font-weight="bold" text-anchor="{anchor}" fill="#0f172a">({x:g}, {y:g})</text>'

    # Graph Legend Banner
    svg += f'<text x="{gw/2}" y="{gh - 12}" font-size="11" text-anchor="middle" fill="#475569" font-weight="600">Scale: 1 Grid Square = {grid_unit} mm × {grid_unit} mm | All values in mm</text>'
    svg += '</svg>'
    return svg

def parse_polygon_coords(text):
    points = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        c = line.replace(',', ' ').split()
        if len(c) >= 2:
            points.append((float(c[0]), float(c[1])))
    return points

def calc_shape(shape, form):
    try:
        raw_p = {}
        if shape == "rectangle":
            b = float(form.get("b", 0))
            d = float(form.get("d", 0))
            area = b * d
            x_bar = b / 2.0
            y_bar = d / 2.0
            Ixx_cg = (b * (d**3)) / 12.0
            Iyy_cg = (d * (b**3)) / 12.0
            I_base = (b * (d**3)) / 3.0
            raw_p = {'coords': [(0,0), (b,0), (b,d), (0,d)], 'x_bar': x_bar, 'y_bar': y_bar}

        elif shape == "triangle":
            b = float(form.get("b", 0))
            h = float(form.get("h", 0))
            area = 0.5 * b * h
            x_bar = b / 2.0
            y_bar = h / 3.0
            Ixx_cg = (b * (h**3)) / 36.0
            Iyy_cg = (h * (b**3)) / 48.0
            I_base = (b * (h**3)) / 12.0
            raw_p = {'coords': [(0,0), (b,0), (b/2.0, h)], 'x_bar': x_bar, 'y_bar': y_bar}

        elif shape == "circle":
            dia = float(form.get("dia", 0))
            r = dia / 2.0
            area = math.pi * (r**2)
            x_bar = r
            y_bar = r
            Ixx_cg = (math.pi * (dia**4)) / 64.0
            Iyy_cg = Ixx_cg
            I_base = Ixx_cg + (area * (y_bar**2))
            pts = [(r + r*math.cos(math.radians(a)), r + r*math.sin(math.radians(a))) for a in range(0, 360, 15)]
            raw_p = {'coords': pts, 'x_bar': x_bar, 'y_bar': y_bar}

        elif shape == "semicircle":
            r = float(form.get("r", 0))
            area = (math.pi * (r**2)) / 2.0
            x_bar = r
            y_bar = (4.0 * r) / (3.0 * math.pi)
            I_base = (math.pi * (r**4)) / 8.0
            Ixx_cg = I_base - (area * (y_bar**2))
            Iyy_cg = (math.pi * (r**4)) / 8.0
            pts = [(r + r*math.cos(math.radians(a)), r*math.sin(math.radians(a))) for a in range(0, 181, 10)]
            pts.append((0, 0))
            raw_p = {'coords': pts, 'x_bar': x_bar, 'y_bar': y_bar}

        elif shape == "tsection":
            bf = float(form.get("t_bf", 0))
            tf = float(form.get("t_tf", 0))
            dw = float(form.get("t_dw", 0))
            tw = float(form.get("t_tw", 0))
            a1, y1 = dw * tw, dw / 2.0
            a2, y2 = bf * tf, dw + (tf / 2.0)
            area = a1 + a2
            y_bar = ((a1 * y1) + (a2 * y2)) / area
            x_bar = bf / 2.0
            I_base = (tw * (dw**3)) / 3.0 + ((bf * (tf**3)) / 12.0) + (a2 * (y2**2))
            Ixx_cg = I_base - (area * (y_bar**2))
            Iyy_cg = ((dw * (tw**3)) / 12.0) + ((tf * (bf**3)) / 12.0)

            pts = [
                ((bf-tw)/2, 0), ((bf+tw)/2, 0), ((bf+tw)/2, dw),
                (bf, dw), (bf, dw+tf), (0, dw+tf), (0, dw), ((bf-tw)/2, dw)
            ]
            raw_p = {'coords': pts, 'x_bar': x_bar, 'y_bar': y_bar}

        elif shape == "isection":
            bft = float(form.get("i_bft", 0))
            tft = float(form.get("i_tft", 0))
            dw = float(form.get("i_dw", 0))
            tw = float(form.get("i_tw", 0))
            bfb = float(form.get("i_bfb", 0))
            tfb = float(form.get("i_tfb", 0))
            max_b = max(bfb, bft)

            a1, y1 = bfb * tfb, tfb / 2.0
            a2, y2 = tw * dw, tfb + (dw / 2.0)
            a3, y3 = bft * tft, tfb + dw + (tft / 2.0)
            area = a1 + a2 + a3
            y_bar = (a1*y1 + a2*y2 + a3*y3) / area
            x_bar = max_b / 2.0

            I_base = ((bfb * (tfb**3)) / 12.0 + a1*(y1**2)) + \
                     ((tw * (dw**3)) / 12.0 + a2*(y2**2)) + \
                     ((bft * (tft**3)) / 12.0 + a3*(y3**2))
            Ixx_cg = I_base - (area * (y_bar**2))
            Iyy_cg = (tfb * (bfb**3)) / 12.0 + (dw * (tw**3)) / 12.0 + (tft * (bft**3)) / 12.0

            # 12 Points mapped to origin at left
            cx = max_b / 2.0
            tot_h = tfb + dw + tft
            pts = [
                (cx - bfb/2, 0), (cx + bfb/2, 0), (cx + bfb/2, tfb),
                (cx + tw/2, tfb), (cx + tw/2, tfb + dw), (cx + bft/2, tfb + dw),
                (cx + bft/2, tot_h), (cx - bft/2, tot_h), (cx - bft/2, tfb + dw),
                (cx - tw/2, tfb + dw), (cx - tw/2, tfb), (cx - bfb/2, tfb)
            ]
            raw_p = {'coords': pts, 'x_bar': x_bar, 'y_bar': y_bar}

        elif shape == "uneven":
            raw_text = form.get("poly_coords", "")
            pts = parse_polygon_coords(raw_text)
            if len(pts) < 3:
                return None, None, None, "Ocha ma ocha 3 coordinates (points) nakho."

            # Close if needed
            calc_pts = list(pts)
            if calc_pts[0] != calc_pts[-1]:
                calc_pts.append(calc_pts[0])

            n = len(calc_pts) - 1
            A_signed = cx_sum = cy_sum = ix_sum = iy_sum = 0.0

            for i in range(n):
                xi, yi = calc_pts[i]
                xi1, yi1 = calc_pts[i+1]
                cross = (xi * yi1) - (xi1 * yi)
                A_signed += cross
                cx_sum += (xi + xi1) * cross
                cy_sum += (yi + yi1) * cross
                ix_sum += (yi**2 + yi * yi1 + yi1**2) * cross
                iy_sum += (xi**2 + xi * xi1 + xi1**2) * cross

            A_val = 0.5 * A_signed
            if abs(A_val) < 1e-6:
                return None, None, None, "Aapela points thi banto area zero chhe. Sacha coordinates nakho."

            if A_val < 0:
                A_val, cx_sum, cy_sum, ix_sum, iy_sum = -A_val, -cx_sum, -cy_sum, -ix_sum, -iy_sum

            area = A_val
            x_bar = cx_sum / (6.0 * area)
            y_bar = cy_sum / (6.0 * area)
            I_base = ix_sum / 12.0
            I_y_orig = iy_sum / 12.0
            Ixx_cg = max(I_base - (area * (y_bar**2)), 0.0)
            Iyy_cg = max(I_y_orig - (area * (x_bar**2)), 0.0)

            raw_p = {'coords': pts, 'x_bar': x_bar, 'y_bar': y_bar}
        else:
            return None, None, None, "Invalid shape selection."

        res = {
            "area": f"{area:.2f}",
            "x_bar": f"{x_bar:.2f}",
            "y_bar": f"{y_bar:.2f}",
            "Ixx_cg": f"{Ixx_cg:.2f}",
            "Iyy_cg": f"{Iyy_cg:.2f}",
            "I_base": f"{I_base:.2f}"
        }

        svg_card = generate_schematic_card(shape, raw_p)
        svg_graph = generate_schematic_graph(shape, raw_p)
        return res, svg_card, svg_graph, None

    except Exception as e:
        return None, None, None, f"Calculation Error: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    svg_card = None
    svg_graph = None
    error = None
    shape = "uneven"

    if request.method == "POST":
        shape = request.form.get("shape", "uneven")
        result, svg_card, svg_graph, error = calc_shape(shape, request.form)

    return render_template_string(
        HTML_TEMPLATE,
        result=result,
        svg_card=svg_card,
        svg_graph=svg_graph,
        error=error,
        shape=shape
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
