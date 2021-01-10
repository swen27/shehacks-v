from flask import Flask, render_template, request
import pandas as pd
import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

df_temp = pd.read_csv("temperature.csv")
df_pre = pd.read_csv("precipitation.csv")
df_pre.drop(columns = ["GeogPoint", "County", "ISO_3166_2", "ISO_A3", "LocalDate"], inplace=True)

city_name = "Toronto"
current_temp = 0
current_pre_rain = 0
current_pre_snow = 0

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if len(request.form) > 0:
        global city_name 
        city_name = request.form["search"]
    return render_template("index.html")


@app.route('/graph', methods=["GET", "POST"])
def graph():
    if len(request.form) > 0:
        global city_name 
        city_name = request.form["search"]
    df_temp_2 = df_temp[df_temp["City"] == city_name]
    df_temp_2_group = df_temp_2.groupby(["LocalHour"]).Temperature_C.mean()
    df_temp_list = df_temp_2_group.tolist()
    global current_temp 
    current_temp = round(df_temp_list[-1],2)

    df_pre_2 = df_pre[df_pre["City"] == city_name]
    df_pre_2_group = df_pre_2.groupby(["LocalHour"]).mean()
    df_pre_list = df_pre_2_group["ProbabilityofPrecipitation"].tolist()
    df_snow_list = df_pre_2_group["ProbabilityofSnow"].tolist()
    global current_pre_rain 
    current_pre_rain = (round(100* df_pre_list[-1], 1))
    global current_pre_snow 
    current_pre_snow = (round(100* df_snow_list[-1], 1))
    return render_template("graph.html", city = city_name, temperature = current_temp, precipitation = current_pre_rain, snow = current_pre_snow)

@app.route("/plot")
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    df_temp_2 = df_temp[df_temp["City"] == city_name]
    df_temp_2_group = df_temp_2.groupby(["LocalHour"]).Temperature_C.mean()
    df_temp_list = df_temp_2_group.tolist()
    global current_temp 
    current_temp = round(df_temp_list[-1],2)

    df_pre_2 = df_pre[df_pre["City"] == city_name]
    df_pre_2_group = df_pre_2.groupby(["LocalHour"]).mean()
    df_pre_list = df_pre_2_group["ProbabilityofPrecipitation"].tolist()
    df_snow_list = df_pre_2_group["ProbabilityofSnow"].tolist()
    global current_pre_rain 
    current_pre_rain = (round(100* df_pre_list[-1], 1))
    global current_pre_snow 
    current_pre_snow = (round(100* df_snow_list[-1], 1))

    fig = Figure(figsize= (10,3))

    axis = fig.add_subplot(1, 2, 1)
    axis.plot(df_temp_2_group.index, df_temp_2_group, color = "forestgreen")
    axis.set_xlabel('Time', fontname="Lato", fontsize=10)
    axis.set_ylabel('Temperature ($^\circ$C)', fontname="Lato", fontsize=10)
    axis.set_title('Temperature in '+city_name, fontname="Lato", fontsize=12)
    axis.set_xticks(range(0, 15, 2))
    axis.set_xticklabels(["12am", "2am", "4am", "6am", "8am", "10am", "12pm", "2pm"],fontname="Lato", fontsize=9)
    labels = axis.get_yticks()
    labels2 = [round(label, 2) for label in labels]
    axis.set_yticklabels(labels2, fontname = "Lato", fontsize = 9)
    axis.fill_between(df_temp_2_group.index, df_temp_2_group, y2=min(df_temp_2_group), alpha=0.2, color = "forestgreen")
    axis2 = fig.add_subplot(1, 2, 2, frame_on = True)
    axis2.plot(df_pre_2_group.index, df_pre_2_group.ProbabilityofPrecipitation, color = "forestgreen")
    axis2.plot(df_pre_2_group.index, df_pre_2_group.ProbabilityofSnow, color = "lightpink")
    axis2.legend(["Rain", "Snow"])
    axis2.set_xlabel('Time', fontname="Lato", fontsize=10)
    axis2.set_ylabel('Probability of precipitation', fontname="Lato", fontsize=10)
    axis2.set_title('Probability of precipitation in '+city_name, fontname="Lato", fontsize=12)
    axis2.set_xticks(range(0, 15, 2))
    axis2.set_xticklabels(["12am", "2am", "4am", "6am", "8am", "10am", "12pm", "2pm"],fontname="Lato", fontsize=9)
    axis2.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    axis2.set_yticklabels([0.0, 0.2, 0.4, 0.6, 0.8, 1.0], fontname = "Lato", fontsize = 9)
    axis2.fill_between(df_pre_2_group.index, df_pre_2_group.ProbabilityofSnow, y2=df_pre_2_group.ProbabilityofPrecipitation, alpha=0.2, color = "lightpink")
    fig.tight_layout()
    fig.subplots_adjust(wspace = 0.2)
    return fig