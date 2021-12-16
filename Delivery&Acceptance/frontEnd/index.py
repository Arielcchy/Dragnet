from flask import Flask, render_template, redirect, request, url_for
import numpy as np
import pandas as pd
import math

app = Flask(__name__)
app.secret_key ="arielplaybootstrap5andlearningalgorithm"

cha=pd.read_csv('CLEAN_charity_data.csv')

# preprocessing dataset
# Replace NaN in leader_comp & leader_comp_p; Motta won't be neccessary to fill in, so just let it NaN
meanLeaderCompPercentage = cha['leader_comp_p'].mean()
meanLeaderCompValue = meanLeaderCompPercentage * cha['tot_exp']
cha['leader_comp_p'].fillna(value=meanLeaderCompPercentage, inplace=True)
cha['leader_comp'].fillna(value=meanLeaderCompValue, inplace=True)
# Replace size object to integer
cha['size'].replace(to_replace ="small", value =1, inplace=True)
cha['size'].replace(to_replace ="mid", value =2, inplace=True)
cha['size'].replace(to_replace ="big", value =3, inplace=True)
# standize all features that put into recommendation
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
content_input = cha.drop(["ascore","description","ein","fscore","tot_exp","fund_eff","leader","leader_comp","motto","name","tot_rev","state","program_exp","fund_exp","admin_exp"],axis = 1)
content_input.dropna(inplace = True)
content_input[content_input.columns[content_input.dtypes == "float64"].values] = sc.fit_transform(content_input[content_input.columns[content_input.dtypes == "float64"].values]) 
content_input
# convert text into other columns to find correlation (cosine-similarity)
content_input = pd.get_dummies(content_input,columns = ["category","subcategory"])
# Find cosine similarity on all features
from sklearn.metrics.pairwise import cosine_similarity
temp = cosine_similarity(content_input)
cha_cosine_similarity = pd.DataFrame(temp)

# routes
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/doc',methods = ["POST","GET"])
def doc():
    if request.method == "POST":
        charity_request = request.form["search"]
        print("searching charity", charity_request) 
        returnValue = redirect(url_for("recommend", charity = charity_request))
    else:
        returnValue = render_template("doc.html")
    return returnValue

@app.route("/recommend/<charity>", methods=["POST", "GET"])
def recommend(charity): 
    try:
        if request.method == 'GET':
            description = list(cha[cha["name"] == charity]["description"])[0]
            recommendation = get_recommendations(charity) 
            return render_template("recommend.html", Recommendation = recommendation, Charity = charity, Description = description)
        else:
            return render_template("index.html")
    except:
        print("THIS IS A EXCEPTION:", charity)
        return redirect(url_for("doc"))

def get_recommendations(charity):
    print("GET_RECOMMENDATOIN",charity)
    id = cha[cha["name"] == charity].index.values[0]
    s = cha_cosine_similarity[id].sort_values(ascending = False).index.values[1:7] 
    x = []
    z = []
    for y in s:
        x.append(cha.iloc[y]["name"])
        similarity = cha_cosine_similarity.at[y,id]
        percent_similarity = math.floor(similarity*10000)/100
        z.append(percent_similarity)
    return zip(x,z)

if __name__ == "__main__":
    app.run(debug = True) 