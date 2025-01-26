import json
import numpy as np
from bokeh.plotting import figure, show
from bokeh.embed import json_item
from bokeh.events import DoubleTap, ButtonClick
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, CustomJS, Button, SetValue

callback_draw_code = """
    var data = new_source.data;
    var x = data['x'];
    var y = data['y'];
    var color = data['color'];
    x.push(cb_obj.x);
    y.push(cb_obj.y);
    color.push("pink")

    new_source.change.emit();
    """

callback_reset_code = """
    var data = new_source.data;
    var seg_data = seg_source.data;
    var x = data['x'];
    var y = data['y'];
    new_source.data['x'].length = 0;
    new_source.data['y'].length = 0;
    new_source.data['color'].length = 0;
    
    seg_data['x0'].length = 0;
    seg_data['y0'].length = 0;
    seg_data['x1'].length = 0;
    seg_data['y1'].length = 0;
    new_source.change.emit();
    seg_source.change.emit();
"""

callback_connect_code = """
    for (var i = 0; i < new_source.data['x'].length; i++) {
        var x0=new_source.data['x'][i];
        var y0=new_source.data['y'][i];
        var dis = [];
        var dis_index = Array.from({ length: origin_source.data['x'].length }, (_, i) => i);
        for (var j=0; j < origin_source.data['x'].length;j++){
            var distance = Math.sqrt(Math.pow(new_source.data['x'][i]-origin_source.data['x'][j],2)+Math.pow(new_source.data['y'][i]-origin_source.data['y'][j],2))
            dis.push(distance)
        }
        dis_index.sort(function(a,b){return dis[a]-dis[b]});

        var color = [0,0,0];
        var color_name = ["red","green","blue"];
        for (var j=0;j<5;j++){
            var target_index = dis_index[j]
            seg_source.data["x0"].push(x0)
            seg_source.data["y0"].push(y0)
            seg_source.data["x1"].push(origin_source.data['x'][target_index])
            seg_source.data["y1"].push(origin_source.data['y'][target_index])
            if(origin_source.data['color'][target_index]=="red"){color[0] += 1}
            if(origin_source.data['color'][target_index]=="green"){color[1] += 1}
            if(origin_source.data['color'][target_index]=="blue"){color[2] += 1}
        }
        function getMaxIndex(arr) {
            let max = Math.max(...arr);
            let maxIndex = arr.indexOf(max);
            return maxIndex;
            }
        var point_color = color_name[getMaxIndex(color)];
        new_source.data['color'][i]=point_color;
        
    }
    seg_source.change.emit();
    new_source.change.emit();
"""


def display_p(p):
    show(p)

def display_bokeh(p, tag, event=None):
    p_json = json.dumps(json_item(p, tag))
    Bokeh.embed.embed_item(JSON.parse(p_json))

cluster_center = [(1, 1), (5, 5), (6, -1)]
point_num = 20
X = []
Y = []
COLOR = ["red", "blue", "green"]
label = []
c_i = 0
color = []
for i in cluster_center:
    x = np.random.randn(point_num) + i[0]
    y = np.random.randn(point_num) + i[1]
    X.append(x)
    Y.append(y)
    color += [COLOR[c_i] for i in range(point_num)]
    c_i += 1
    label += [c_i for i in range(point_num)]
X = np.concatenate(X)
Y = np.concatenate(Y)

def kmeans_scatter():
    origin_source = ColumnDataSource(data=dict(x=X, y=Y, color=color, label=label))
    p = figure(width=400, height=400,tools=["pan","wheel_zoom"])
    p.toolbar.autohide = True
    # p.tools="pan,wheel_zoom"
    p.scatter("x", "y", color="color", source=origin_source)

    return p

def kmeans_cluster():
    reset_button = Button(label="Reset Draw")
    connect_button = Button(label="Classification")

    origin_source = ColumnDataSource(data=dict(x=X, y=Y, color=color, label=label))
    new_source = ColumnDataSource(data=dict(x=[], y=[], color=[]))
    seg_source = ColumnDataSource(data=dict(x0=[], y0=[], x1=[], y1=[]))

    p = figure(width=400, height=400)
    p.scatter("x", "y", color="color", source=origin_source)
    p.scatter('x', 'y', source=new_source, fill_color='color', size=10)
    p.segment(x0="x0", y0="y0", x1="x1", y1="y1", color='pink', source=seg_source)

    callback_draw = CustomJS(args=dict(new_source=new_source), code=callback_draw_code)
    callback_reset = CustomJS(args=dict(new_source=new_source, seg_source=seg_source), code=callback_reset_code)
    callback_connect = CustomJS(args=dict(origin_source=origin_source, new_source=new_source, seg_source=seg_source),
                                code=callback_connect_code)

    p.js_on_event(DoubleTap, callback_draw)
    reset_button.js_on_event(ButtonClick, callback_reset)
    connect_button.js_on_event(ButtonClick, callback_connect)
    layouts = layout(children=[
        [p],
        [reset_button, connect_button]
    ])

    return layouts

DEBUG = False

if DEBUG:
    # display_p(knn_scatter())
    display_p(kmeans_scatter())
else:
    from pyscript import display
    from js import Bokeh, JSON

    # display_bokeh(knn_scatter(),"display_bokeh1")
    display_bokeh(kmeans_scatter(), "sample_distribution")
    display_bokeh(kmeans_cluster(), "kmeans_cluster")

